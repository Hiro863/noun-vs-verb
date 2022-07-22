import logging
import os
import re
import sys
import traceback
from pathlib import Path
from typing import Callable, Tuple
import numpy as np
from mne import (compute_covariance, read_labels_from_annot,
                 find_events, Epochs, Evoked, Label, read_forward_solution,
                 read_source_spaces, compute_source_morph)

from joblib import Parallel, delayed
from mne.io import Raw
from mne.preprocessing import ICA
from mne.minimum_norm import make_inverse_operator, apply_inverse, apply_inverse_epochs
from src.events.formatting import get_event_array, select_conditions
from src.utils.exceptions import SubjectNotProcessedError
from src.utils.file_access import read_mous_subject, get_mous_meg_channels, read_raw


log_path = Path("/data/home/hiroyoshi/mous_wd/logs")

########################################################################################################################
# DOWNSAMPLING                                                                                                         #
########################################################################################################################


def downsample(raw: Raw, params: dict, n_jobs) -> Tuple[Raw, np.array, np.array]:
    """
    Downsample to some lower sampling frequency
    :param raw: raw object
    :param params: dictionary of parameters {"sfreq": sampling frequency, "n_jobs": number of workers for joblib}
    :param n_jobs: number of jobs for parallelism
    :return:
        raw: resampled raw object
        events: original events (needed for validating events)
        new_events: events with new sampling frequency
    """

    sfreq = params["sfreq"]
    logging.info(f"Downsampling to {sfreq} Hz")

    # Find events (needed whether or not downsampled)
    try:
        events = find_events(raw, stim_channel=["UPPT001", "UPPT002"])
    except ValueError as e:
        logging.exception(f"Issue with shortest event. Needs manual inspection {e}")
        raise SubjectNotProcessedError(e)

    # If sampling frequency is specified, downsample
    if sfreq > 0 and not None:
        logging.debug(f"Resampling at {sfreq} Hz")

        # n_jobs = min(5, n_jobs)  # to avoid running out of memory
        raw, new_events = raw.resample(sfreq=sfreq, events=events, n_jobs=n_jobs)

        return raw, events, new_events
    else:
        return raw, events, events

########################################################################################################################
# ARTIFACT REMOVAL                                                                                                     #
########################################################################################################################


def remove_artifacts(raw: Raw, n_components: int,
                     eog_channels=None, ecg_channel=None, n_jobs=1) -> Raw:
    """
    Perform artifact removal using ICA.
    :param raw: mne raw object
    :param n_components: number of components to use for ICA
    :param eog_channels: list of channel names to be used as EOG channels
    :param ecg_channel: the name of the channel to be used as the ECG channel
    :param n_jobs: number of jobs for parallelism
    :return: raw: repaired raw
    """

    logging.info("Removing artifacts")

    if eog_channels is None and ecg_channel is None:
        logging.debug("Skipping artifact repair")
        return raw

    # Perform ICA
    logging.info(f"Starting ICA with {n_components} components")

    n_jobs = min(5, n_jobs)  # to avoid running out of memory
    filtered_raw = raw.copy().filter(l_freq=1., h_freq=None, n_jobs=n_jobs)

    ica = ICA(n_components=n_components)
    ica.fit(filtered_raw)

    ica.exclude = []

    # Remove ocular artifacts
    if eog_channels is not None:
        logging.debug("Repairing ocular artifacts")
        eog_indices, _ = ica.find_bads_eog(raw, ch_name=eog_channels, verbose=True)
        ica.exclude = eog_indices

    # Remove heartbeat artifacts
    if ecg_channel is not None:
        logging.debug("Repairing heartbeat artifacts")
        ecg_indices, _ = ica.find_bads_eog(raw, ch_name=ecg_channel, verbose=True)
        ica.exclude = ecg_indices

    logging.info(f"Total of {len(ica.exclude)} components removed")

    ica.apply(raw)
    return raw


########################################################################################################################
# FILTERING                                                                                                            #
########################################################################################################################


def apply_filter(raw: Raw, l_freq: int, h_freq: int, notch: list, n_jobs=1) -> Raw:
    """
    Apply band-pass filter and notch filter
    :param raw: raw file to apply filter to
    :param l_freq: lower frequency limit
    :param h_freq: upper frequency limit
    :param notch: list frequencies
    :param n_jobs: number of jobs for parallelism
    :return: filtered raw
    """

    logging.info(f"Filtering at high pass {l_freq} Hz, low pass {h_freq} and notches {notch}. n_jobs = {n_jobs}")

    raw = raw.filter(l_freq=l_freq, h_freq=h_freq)

    if len(notch) > 0:
        raw = raw.notch_filter(freqs=notch)

    return raw


########################################################################################################################
# EPOCHING                                                                                                             #
########################################################################################################################


def epoch(dst_dir: Path, events_dir: Path, subject: str,
          raw: Raw, events: np.array, mode,
          tmin: float, tmax: float, reject: dict, channel_reader: Callable,
          dictionary_path, simplify_mode) -> Epochs:
    """
    Epoch the subject data
    :param dst_dir: path to which the epochs object will be saved
    :param events_dir: path to events csv files
    :param subject: name of the subject
    :param raw: raw object
    :param events: events array (possibly downsampled)
    :param mode: whether to use `index` or `binary` noun vs. verb
    :param tmin: start time of epoch
    :param tmax: end time of epoch
    :param reject: rejection criteria
    :param channel_reader: a function for getting a list of relevant channels
    :param dictionary_path: path to .csv file containing POV information
    :param simplify_mode: how to select events. `sentence`, `list` or `both`
    :return:
        Non
    """

    # Get events data
    events = _read_events_file(events_dir, events, subject, mode, dictionary_path, simplify_mode)

    # Get relevant channels
    picks = channel_reader(channels=raw.ch_names)

    epochs = None
    try:
        epochs = Epochs(raw, events, tmin=tmin, tmax=tmax,
                        picks=picks, preload=True, reject=reject, on_missing="warn")

    except ValueError as e:
        # Not all events are present for all subjects
        logging.exception(f"Missing event ids. Continuing {e}")

    # Save epochs to file
    _save_epochs(epochs, subject, dst_dir)

    # Save events to file
    fname = "events.npy"
    np.save(str(dst_dir / fname), epochs.events)

    return epochs


def _read_events_file(events_dir: Path, events: np.array, subject: str, mode,
                      dictionary_path, simplify_mode) -> Tuple[np.array, dict]:
    """
    Convert the original events generated by mne.find_events and format + validate the events.
    :param events_dir: directory containing .csv files about events
    :param events: events array generated by MNE-python
    :param subject: subject name
    :param mode: whether to use `index` or `binary` noun vs. verb
    :param dictionary_path: path to .csv file containing POS information
    :param simplify_mode: how to select events. `sentence`, `list` or `both`
    :return:
        reformatted events array
    """

    events_file = None

    # Find the corresponding event info file
    for file in os.listdir(events_dir):
        if re.match(fr"{subject}.*\.csv", file):  # otherwise finds "...-rejected.txt"
            events_file = file

    if events_file is None:
        msg = f"Events info for {subject} was not found"
        logging.exception(msg)
        raise SubjectNotProcessedError(FileNotFoundError, msg)

    event_path = events_dir / events_file
    events = get_event_array(events, event_path, dictionary_path, simplify_mode)

    events = select_conditions(events, mode=mode)

    return events


def _save_epochs(epochs: Epochs, subject: str, dst_dir: Path) -> None:
    """
    Save epochs to file
    :param epochs: epochs to be saved
    :param subject: subject name
    :param dst_dir: directory to save in
    """

    if epochs is not None:

        epoch_fname = f"{subject}-epo.fif"
        logging.debug(f"Writing {epoch_fname} epochs to file")
        try:
            epochs.save(str(dst_dir / epoch_fname), overwrite=True)
        except OSError as e:
            msg = f"Failed to write the file {dst_dir / epoch_fname}. {e}"
            logging.exception(msg)
            SubjectNotProcessedError(e, msg)

########################################################################################################################
# SOURCE LOCALIZATION                                                                                                  #
########################################################################################################################


def source_localize(dst_dir: Path, subject: str, epochs: Epochs, params: dict, n_jobs=1) -> None:
    """

    :param dst_dir:
    :param subject:
    :param epochs:
    :param params:
    :param n_jobs:
    :return:
    """

    logging.info(f"Source localizing {subject} files")

    # Make inverse model
    logging.info(f"Making an inverse model for the subject {subject} ")
    inv = get_inv(epochs, fwd_path=Path(params["fwd_path"]) / f"{subject}-fwd.fif", n_jobs=n_jobs)

    # Common source space
    logging.info(f"Setting up morph to FS average")
    fsaverage_src_path = Path(params["subjects dir"]) / "fsaverage" / "bem" / "fsaverage-ico-5-src.fif"
    fs_src = read_source_spaces(str(fsaverage_src_path))
    morph = compute_source_morph(src=inv["src"], subject_from=subject, subject_to="fsaverage", src_to=fs_src,
                                 subjects_dir=params["subjects dir"], verbose=False)

    # Generate set of labels
    logging.info(f"Reading labels")
    labels = read_labels_from_annot("fsaverage", params["parcellation"], params["hemi"],
                                    subjects_dir=params["subjects dir"], verbose=False)

    # Create parallel functions per time point
    parallel_funcs = []

    for label in labels:
        # Ignore irrelevant labels
        if re.match(r".*(unknown|\?|deeper|cluster|default|ongur|medial\.wall).*", label.name.lower()):
            continue
        func = delayed(_process_single_label)(dst_dir=dst_dir,
                                              epochs=epochs, label=label, inv=inv,
                                              params=params, morph=morph)
        parallel_funcs.append(func)

    logging.info(f"Total of {len(parallel_funcs)} parallel functions added")
    logging.info(f"Executing {n_jobs} jobs in parallel")
    parallel_pool = Parallel(n_jobs=n_jobs)
    parallel_pool(parallel_funcs)

    logging.debug(f"{len(parallel_funcs)} time steps processed")


def _process_single_label(dst_dir: Path, epochs: Epochs, label: Label, inv, params, morph):  # todo
    """
    Perform source localization on a particular cortical area.
    :param dst_dir: directory to store the results in
    :param epochs: epochs object to perform source localization on
    :param label: cortical area of interest
    :param inv: inverse operator
    :param params: should contain `method` and `pick ori`
    :param morph: todo
    :return:
    """

    logging.info(f"Processing single subject for {label.name} ")

    stcs = _inverse_epochs(epochs, inv=inv, method=params["method"], pick_ori=params["pick ori"])
    stcs = _morph_to_common(stcs, morph)

    data_list = []
    for stc in stcs:
        stc = stc.in_label(label)
        data_list.append(stc.data)

    data = np.stack(data_list)

    _write_array(dst_dir=dst_dir, label=label, data_array=data)


def _morph_to_common(stcs: list, morph):
    """
    Morph the source localization into a common (fsaverge) space
    :param stcs: list of source localizations (per epoch)
    :param morph: todo
    :return:
    """

    logging.info(f"Morphing to fsaverage")

    for stc in stcs:
        fs_stc = morph.apply(stc)
        yield fs_stc


def _write_array(dst_dir: Path, label: Label, data_array):
    """
    Write the resulting file into appropriate directory
    :param dst_dir: path to directory in which results will be saved
    :param label: name of the cortical area
    :param data_array: data array to be saved
    """

    logging.info(f"Writing the data for {label.name} to file")

    stc_fname = f"{label.name}.npy"

    logging.info(f"Saving {stc_fname} to file in {dst_dir}")

    stc_dir = dst_dir / "stc"

    if not stc_dir.exists():
        os.makedirs(stc_dir)

    try:
        np.save(str(stc_dir / stc_fname), data_array)

    except OSError as e:
        logging.exception(f"Failed to write {dst_dir / stc_fname} to file. {e.strerror}")
        raise SubjectNotProcessedError(e)


def _inverse_evoked(evoked: Evoked, fwd_path: str, method="dSPM", snr=3., return_residual=True, pick_ori=None, inv=None,
                    epochs=None, n_jobs=1, tmax=0.,
                    inv_method=("shrunk", "empirical"), rank=None,
                    loose=0.2, depth=0.8, verbose=False):
    """
    todo
    :param evoked: evoked object
    :param fwd_path: path to precomputed forward object
    :param method:
    :param snr: signal to noise ratio
    :param return_residual: return residual (see MNE)
    :param pick_ori: pick orientation (see MNE)
    :param inv: inverse operator object
    :param epochs: epochs object
    :param n_jobs: number of jobs
    :param tmax: todo
    :param inv_method: source estimation method
    :param rank: todo
    :param loose: todo
    :param depth: todo
    :param verbose: verbose
    :return:
        source estimation
    """

    if not inv:
        inv = get_inv(epochs, fwd_path=fwd_path, n_jobs=n_jobs, tmax=tmax, method=inv_method, rank=rank,
                      loose=loose, depth=depth, verbose=verbose)

    lambda2 = 1. / snr ** 2
    return apply_inverse(evoked, inv, lambda2,
                         method=method, pick_ori=pick_ori,
                         return_residual=return_residual, verbose=False)


def _inverse_epochs(epochs: Epochs, label=None, method="dSPM", snr=3., pick_ori=None, inv=None,
                    n_jobs=1, tmax=0., fwd_path="",
                    inv_method=("shrunk", "empirical"), rank=None,
                    loose=0.2, depth=0.8, verbose=False):
    """
    todo
    :param epochs: epochs object
    :param label: labels (cortical area)
    :param method: source estimation method
    :param snr: signal to noise ratio
    :param pick_ori: todo
    :param inv: inverse operator
    :param n_jobs: number of jobs
    :param tmax: todo
    :param fwd_path: path to precomputed forward operator
    :param inv_method: todo
    :param rank: todo
    :param loose: todo
    :param depth: todo
    :param verbose: verbosity
    :return:
        source estiamtion
    """

    logging.info(f"Inverting epochs")

    if not inv:
        inv = get_inv(epochs, fwd_path=fwd_path, n_jobs=n_jobs, tmax=tmax, method=inv_method, rank=rank,
                      loose=loose, depth=depth, verbose=verbose)

    lambda2 = 1. / snr ** 2
    return apply_inverse_epochs(epochs, inv, lambda2, label=label,
                                method=method, pick_ori=pick_ori, verbose=verbose, return_generator=True)


def get_inv(epochs: Epochs, fwd_path: str, tmax=0., n_jobs=1, method=("shrunk", "empirical"),
            rank=None, loose=0.2, depth=0.8, verbose=False):
    """
    todo
    :param epochs: epochs object
    :param fwd_path: path to precomputed forward operator
    :param tmax: todo
    :param n_jobs: number of jobs for parallelism
    :param method: todo
    :param rank: todo
    :param loose: todo
    :param depth: todo
    :param verbose: verbosity
    :return:
        inverse operator
    """

    fwd = read_forward_solution(fwd_path, verbose=verbose)
    noise_cov = compute_covariance(epochs, tmax=tmax, method=method, rank=rank, n_jobs=n_jobs, verbose=verbose)
    inv = make_inverse_operator(epochs.info, fwd, noise_cov, loose=loose, depth=depth, verbose=verbose)

    return inv


def get_labels_names(params: dict):
    """

    :param params:
    :return:
    """
    # todo

    # Generate set of labels
    labels = read_labels_from_annot("fsaverage", params["parcellation"], params["hemi"],
                                    subjects_dir=params["subjects dir"], verbose=False)
    label_names = []
    for label in labels:

        # Ignore irrelevant labels
        if not re.match(r".*(unknown|\?|deeper|cluster|default|ongur|medial\.wall).*", label.name.lower()):

            label_names.append(label.name)

    return label_names


########################################################################################################################
# PREPROCESSING PIPELINE                                                                                               #
########################################################################################################################


def process_single_subject(src_dir: Path, dst_dir: Path, events_dir: Path,
                           subject_name: str,
                           downsample_params: dict, filter_params: dict,
                           artifact_params: dict, epoch_params: dict,
                           stc_params: dict,
                           stc: bool,
                           n_cores: int) -> None:

    logging.debug(f"Processing subject data from {src_dir}")

    rejected_path = log_path / "rejected_log.txt"

    try:
        # Read files
        raw = read_raw(src_dir=src_dir, dst_dir=dst_dir, file_reader=read_mous_subject)

        # Resample
        raw, events, new_events = downsample(raw, downsample_params, n_jobs=n_cores)

        # Filter
        if filter_params["filter"]:
            raw = apply_filter(raw, l_freq=filter_params["l_freq"], h_freq=filter_params["h_freq"],
                               notch=filter_params["notch"], n_jobs=n_cores)

        # Remove physiological artifacts
        if artifact_params["eog"] or artifact_params["ecg"]:
            raw = remove_artifacts(raw, n_components=artifact_params["n components"],
                                   eog_channels=artifact_params["eog channels"],
                                   ecg_channel=artifact_params["ecg channel"], n_jobs=n_cores)

        # Epoch
        epochs = epoch(dst_dir=dst_dir, events_dir=events_dir, subject=subject_name, raw=raw,
                       events=(events, new_events),
                       mode=epoch_params["mode"],
                       tmin=epoch_params["tmin"], tmax=epoch_params["tmax"],
                       reject=epoch_params["reject"],
                       dictionary_path=epoch_params["dictionary-path"],
                       simplify_mode=epoch_params["simplify-mode"],
                       channel_reader=get_mous_meg_channels)

        # Source localize
        if stc:
            source_localize(dst_dir=dst_dir, subject=subject_name, epochs=epochs, params=stc_params, n_jobs=n_cores)

    except SubjectNotProcessedError as e:
        logging.error(f"Subject {subject_name} was not processed correctly. \n {e} \n {traceback.format_exc()}")

        with open(str(rejected_path), "a") as file:
            file.write(f"{subject_name}\n")
        sys.exit(-1)

    except Exception as e:  # noqa

        logging.error(f"Unexpected exception with the subject {subject_name}. {traceback.format_exc()}")

        with open(str(rejected_path), "a") as file:
            file.write(f"{subject_name}\n")
        sys.exit(-1)