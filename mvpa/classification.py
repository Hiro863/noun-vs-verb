import numpy as np

from sklearn.base import clone
from sklearn.model_selection import KFold
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier

from mne.stats import bootstrap_confidence_interval


def get_indices(times, start, end, sfreq):
    start_idx = int((start - times[0]) / (1 / sfreq))
    end_idx = int((end - times[0]) / (1 / sfreq))
    return start_idx, end_idx


def get_t_steps(window_size, sfreq):
    return int(window_size / (1e3 / sfreq))


def get_slice(x, t_idx, window_size=-1., sfreq=-1):

    if window_size < 0:
        return x[..., t_idx]
    else:
        t_steps = get_t_steps(window_size, sfreq)
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



