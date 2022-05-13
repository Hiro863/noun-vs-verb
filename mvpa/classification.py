import logging
import numpy as np
from joblib import Parallel, delayed
from pathlib import Path

from sklearn.base import clone
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.metrics import balanced_accuracy_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC

from mne.stats import bootstrap_confidence_interval


def _get_indices(times, start, end, sfreq):
    start_idx = int((start - times[0]) / (1 / sfreq))
    end_idx = int((end - times[0]) / (1 / sfreq))
    return start_idx, end_idx


def _get_t_steps(window_size, sfreq):
    return int(window_size / (1e3 / sfreq))


def get_slice(x, t_idx, window_size=-1., sfreq=-1):

    if window_size < 0:
        return x[..., t_idx]
    else:
        t_steps = _get_t_steps(window_size, sfreq)
        return x[..., t_idx - t_steps + 1: t_idx + 1].reshape(x.shape[0], -1)


def classify(x, y, cv, clf: Pipeline, scoring):

    kf = KFold(cv)
    scores = np.zeros((cv,))
    dummy_scores = np.zeros((cv,))

    y = y[0].reshape(-1,) # todo tmp
    dummy_clf = make_pipeline(StandardScaler(), DummyClassifier(strategy="stratified"))

    for i, (train_idx, test_idx) in enumerate(kf.split(x)):

        x_train, x_test = x[train_idx], x[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        clf = clone(clf)

        clf.fit(x_train, y_train)

        y_pred = clf.predict(x_test)
        scores[i] = scoring(y_test, y_pred)

        dummy_clf.fit(x_train, y_train)
        y_pred = dummy_clf.predict(x_test)
        dummy_scores[i] = scoring(y_test, y_pred)

    lower, upper = bootstrap_confidence_interval(scores, ci=.95, n_bootstraps=2000, stat_fun="mean")
    dummy_lower, dummy_upper = bootstrap_confidence_interval(dummy_scores, ci=.95, n_bootstraps=2000, stat_fun="mean")
    return scores, lower, upper, dummy_scores, dummy_lower, dummy_upper


def classify_temporal(x: np.array, y: np.array, params: dict, n_jobs=1):

    name_to_obj = {"LinearSVC": LinearSVC(max_iter=params["max-iter"])}

    # Time array
    times = np.arange(params["epochs-tmin"], params["epochs-tmax"], 1 / params["sfreq"])
    start_idx, end_idx = _get_indices(times,
                                      params["classification-tmin"],
                                      params["classification-tmax"],
                                      params["sfreq"])
    clf = make_pipeline(StandardScaler(), name_to_obj[params["clf"]])

    # Create parallel functions per time point
    parallel_funcs = []

    for t_idx in range(start_idx, end_idx):
        x_slice = get_slice(x=x, t_idx=t_idx, window_size=params["window-size"], sfreq=params["sfreq"])

        func = delayed(classify)(x=x_slice, y=y, cv=params["cv"],
                                 clf=clf, scoring=balanced_accuracy_score)
        parallel_funcs.append(func)

    logging.info(f"Total of {len(parallel_funcs)} parallel functions added")
    logging.info(f"Executing {n_jobs} jobs in parallel")

    parallel_pool = Parallel(n_jobs=n_jobs)
    results = parallel_pool(parallel_funcs)
    results = format_results(data=results, params=params)

    logging.info(f"{len(parallel_funcs)} time steps processed")
    return results


def format_results(data, params):
    scores, lowers, uppers = [], [], []
    d_scores, d_lowers, d_uppers = [], [], []
    for s, l, u, ds, dl, du in data:  # per time step
        scores.append(s)
        lowers.append(l)
        uppers.append(u)
        d_scores.append(ds)
        d_lowers.append(dl)
        d_uppers.append(du)

    scores = np.stack(scores, axis=1)  # cv x time steps
    lowers = np.array(lowers)
    uppers = np.array(uppers)
    d_scores = np.stack(d_scores, axis=1)
    d_lowers = np.array(d_lowers)
    d_uppers = np.array(d_uppers)

    results = {"meta": params,
               "data":
                   {
                       "scores": scores,
                       "lowers": lowers,
                       "uppers": uppers,
                       "dummy-scores": d_scores,
                       "dummy-lowers": d_lowers,
                       "dummy-uppers": d_uppers
                   }}
    return results
