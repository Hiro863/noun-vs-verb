import logging
import os
import re
import sys
import traceback
from pathlib import Path
from typing import Callable, Tuple, List
import numpy as np
from mne import (make_forward_solution, compute_covariance, read_labels_from_annot,
                 find_events, Epochs, SourceEstimate, Label)
from mne.io import Raw
from mne.preprocessing import ICA
from mne.minimum_norm import make_inverse_operator, apply_inverse, apply_inverse_epochs
from events.formatting import get_event_array
from utils.exceptions import SubjectNotProcessedError
from utils.file_access import read_mous_subject, get_mous_meg_channels, read_raw, get_project_root


fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"

root = get_project_root()
log_path = root / "meg-mvpa/data/logs"

logging.basicConfig(level=logging.DEBUG,
                    format=fmt,
                    handlers=[logging.StreamHandler(sys.stdout)])


########################################################################################################################
# DOWNSAMPLING                                                                                                         #
########################################################################################################################


def downsample(raw: Raw, params: dict, n_jobs) -> Tuple[Raw, np.array, np.array]:
    """
    Downsample to some lower sampling frequency
    :param raw: raw object
    :param params: dictionary of parameters {"sfreq": sampling frequency, "n_jobs": number of workers for joblib}
    :return:
        raw: resampled raw object
        events: original events (needed for validating events)
        new_events: events with new sampling frequency
    """

    sfreq = params["sfreq"]

    # Find events (needed whether or not downsampled)
    try:
        events = find_events(raw, stim_channel=["UPPT001", "UPPT002"])
    except ValueError as e:
        logging.exception(f"Issue with shortest event. Needs manual inspection {e}")
        raise SubjectNotProcessedError(e)

    # If sampling frequency specified, downsample
    if sfreq > 0 and not None:
        logging.debug(f"Resampling at {sfreq} Hz")

        n_jobs = min(n_jobs, params["n_jobs"])
        raw, new_events = raw.resample(sfreq=sfreq, events=events, n_jobs=n_jobs)

        return raw, events, new_events
    else:
        return raw, events, events

########################################################################################################################
# ARTIFACT REMOVAL                                                                                                     #
########################################################################################################################


def remove_artifacts(raw: Raw, n_components: int,
                     eog_channels=None, ecg_channel=None) -> Raw:
    """
    Perform artifact removal using ICA.
    :param raw: mne raw object
    :param n_components: number of components to use for ICA
    :param eog_channels: list of channel names to be used as EOG channels
    :param ecg_channel: the name of the channel to be used as the ECG channel
    :return: raw: repaired raw
    """

    if eog_channels is None and ecg_channel is None:
        logging.debug("Skipping artifact repair")
        return raw

    # Perform ICA
    logging.info(f"Starting ICA with {n_components} components")

    filtered_raw = raw.copy().filter(l_freq=1., h_freq=None)

    ica = ICA(n_components=n_components)
    ica.fit(filtered_raw)

    ica.exclude = []

    # Remove ocular artifacts
    if eog_channels is not None:
        logging.debug("Repairing ocular artifacts")
        eog_indices, _ = ica.find_bads_eog(raw, ch_name=eog_channels, verbose=False)
        ica.exclude = eog_indices

    # Remove heartbeat artifacts
    if ecg_channel is not None:
        logging.debug("Repairing heartbeat artifacts")
        ecg_indices, _ = ica.find_bads_eog(raw, ch_name=ecg_channel, verbose=False)
        ica.exclude = ecg_indices

    logging.info(f"Total of {len(ica.exclude)} components removed")

    ica.apply(raw)
    return raw


########################################################################################################################
# FILTERING                                                                                                            #
########################################################################################################################


def apply_filter(raw: Raw, l_freq: int, h_freq: int, notch: list, n_jobs=1) -> Raw:

    logging.debug(f"Filtering at high pass {l_freq} Hz, low pass {h_freq} and notches {notch}. n_jobs = {n_jobs}")
    # todo: filter

    #todo raw.filter(l_freq=l_freq, h_freq=h_freq)
    #raw_highpass = raw.copy().filter(l_freq=cutoff, h_freq=None)

    return raw


########################################################################################################################
# EPOCHING                                                                                                             #
########################################################################################################################


def epoch(dst_dir: Path, events_dir: Path, subject: str,
          raw: Raw, events: np.array, events_id: dict,
          tmin: float, tmax: float, reject: dict, channel_reader: Callable) -> Epochs:
    """
    Epoch the subject data
    :param dst_dir: path to which the epochs object will be saved
    :param events_dir: path to events csv files
    :param subject: name of the subject
    :param raw: raw objectm
    :param events: events array (possibly downsampled)
    :param events_id: dictionary of events and names
    :param tmin: start time of epoch
    :param tmax: end time of epoch
    :param reject: rejection criteria
    :param channel_reader: a function for getting a list of relevant channels
    :return:
        None
    """

    # Get events data
    events, id_events = _read_events_file(events_dir, events, subject)

    # Get relevant channels
    picks = channel_reader(channels=raw.ch_names)

    epochs = None
    try:
        epochs = Epochs(raw, events, event_id=events_id, tmin=tmin, tmax=tmax,
                        picks=picks, preload=True, reject=reject, on_missing="warn")

    except ValueError as e:
        # Not all events are present for all subjects
        logging.exception(f"Missing event ids. Continuing {e}")

    # Save epochs to file
    _save_epochs(epochs, subject, dst_dir)

    # Save events to file
    events = id_events[epochs.selection]  # some events may be rejected
    fname = "events.npy"
    np.save(str(dst_dir / fname), events)

    return epochs


def _read_events_file(events_dir: Path, events: np.array, subject: str) -> Tuple[np.array, dict]:
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
    events, id_events = get_event_array(events, event_path)

    return events, id_events


def _save_epochs(epochs: Epochs, subject: str, dst_dir: Path) -> None:

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


def source_localize(dst_dir: Path, subject: str, epochs: Epochs, params: dict) -> None:
    """
    Source localize and save the data as a numpy array
    :param dst_dir: path to directory in which results will be saved
    :param subject: name of the subject
    :param epochs: epochs object
    :param params: relevant parameters for source localization
    :return:
        None
    """

    logging.debug(f"Source localizing {subject} files")

    # Generate set of labels
    labels = read_labels_from_annot(params["subject"], params["parcellation"], params["hemi"],
                                    subjects_dir=params["subjects dir"], verbose=False)
    inv = get_operator(epochs, trans=params["trans"], src=params["src"], bem=params["bem"])
    for label in labels:

        # Ignore irrelevant labels
        if re.match(r".*(unknown|\?|deeper|cluster|default|ongur|medial\.wall).*", label.name.lower()):
            continue

        stcs = _inverse_epochs(epochs, label, inv=inv, method=params["method"], pick_ori=params["pick ori"],
                               trans=params["trans"], src=params["src"], bem=params["bem"])

        data_array = _concatenate_arrays(stcs)

        _write_array(dst_dir=dst_dir, label=label, data_array=data_array)

        logging.debug(f"Source localization for {subject} has finished")


def _concatenate_arrays(stcs: List[SourceEstimate]) -> np.array:
    """
    Concatenate the data into a single array, shape n_epochs x n_dipoles x n_times
    :param stcs: list of source estimate objects (per epoch)
    :return:
        data_array: data in form n_epochs x n_dipoles x n_times
    """

    data_list = []

    for i, stc in enumerate(stcs):
        data_list.append(stc.data)

    data_array = np.stack(data_list)
    return data_array


def _write_array(dst_dir: Path, label: Label, data_array):
    """
    Write the resulting file into appropriate directory
    :param dst_dir: path to directory in which results will be saved
    :param label: name of the cortical area
    :param data_array: data array to be saved
    :return:
        None
    """

    stc_fname = f"{label.name}.npy"

    logging.debug(f"Saving {stc_fname} to file in {dst_dir}")

    stc_dir = dst_dir / "stc"

    if not stc_dir.exists():
        os.makedirs(stc_dir)

    try:
        np.save(str(stc_dir / stc_fname), data_array)

    except OSError as e:
        logging.exception(f"Failed to write {dst_dir / stc_fname} to file. {e.strerror}")
        raise SubjectNotProcessedError(e)


def _inverse_evoked(evoked, method="dSPM", snr=3., return_residual=True, pick_ori=None, inv=None,
                    epochs=None, trans=None, src=None, bem=None,
                    mindist=5., n_jobs=1, tmax=0.,
                    inv_method=("shrunk", "empirical"), rank=None,
                    loose=0.2, depth=0.8, verbose=True):

    if not inv:
        inv = get_operator(epochs, trans=trans, src=src, bem=bem, mindist=mindist, n_jobs=n_jobs, tmax=tmax,
                           method=inv_method, rank=rank, loose=loose, depth=depth, verbose=verbose)

    lambda2 = 1. / snr ** 2
    return apply_inverse(evoked, inv, lambda2,
                         method=method, pick_ori=pick_ori,
                         return_residual=return_residual, verbose=verbose)


def _inverse_epochs(epochs, label=None, method="dSPM", snr=3., pick_ori=None, inv=None,
                    trans=None, src=None, bem=None,
                    mindist=5., n_jobs=1, tmax=0.,
                    inv_method=("shrunk", "empirical"), rank=None,
                    loose=0.2, depth=0.8, verbose=True):

    if not inv:
        inv = get_operator(epochs, trans=trans, src=src, bem=bem, mindist=mindist, n_jobs=n_jobs, tmax=tmax,
                           method=inv_method, rank=rank, loose=loose, depth=depth, verbose=verbose)

    lambda2 = 1. / snr ** 2
    return apply_inverse_epochs(epochs, inv, lambda2, label=label,
                                method=method, pick_ori=pick_ori, verbose=verbose)


def get_operator(epochs, trans, src, bem, mindist=5., n_jobs=1, tmax=0.,
                 method=("shrunk", "empirical"), rank=None,
                 loose=0.2, depth=0.8, verbose=True):

    fwd = make_forward_solution(epochs.info, trans=trans, src=src, bem=bem, mindist=mindist,
                                n_jobs=n_jobs, verbose=verbose)
    noise_cov = compute_covariance(epochs, tmax=tmax, method=method, rank=rank, verbose=verbose)
    inv = make_inverse_operator(epochs.info, fwd, noise_cov, loose=loose, depth=depth, verbose=verbose)
    return inv


def get_labels_names(params: dict):

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
                           n_cores) -> None:

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
                               notch=filter_params["notch"], n_jobs=filter_params["n_jobs"])

        # Remove physiological artifacts
        if artifact_params["eog"] or artifact_params["ecg"]:
            raw = remove_artifacts(raw, n_components=artifact_params["n components"],
                                   eog_channels=artifact_params["eog channels"],
                                   ecg_channel=artifact_params["ecg channel"])

        # Epoch
        epochs = epoch(dst_dir=dst_dir, events_dir=events_dir, subject=subject_name, raw=raw,
                       events=(events, new_events),
                       events_id=epoch_params["event id"],
                       tmin=epoch_params["tmin"], tmax=epoch_params["tmax"],
                       reject=epoch_params["reject"], channel_reader=get_mous_meg_channels)

        # Source localize
        source_localize(dst_dir=dst_dir, subject=subject_name, epochs=epochs, params=stc_params)

    except SubjectNotProcessedError as e:
        logging.error(f"Subject {subject_name} was not processed correctly. \n {e} \n {traceback.format_exc()}")

        with open(str(rejected_path), "a") as file:
            file.write(f"{subject_name}\n")

    except Exception as e:  # noqa

        logging.error(f"Unexpected exception with the subject {subject_name}. {traceback.format_exc()}")

        with open(str(rejected_path), "a") as file:
            file.write(f"{subject_name}\n")
