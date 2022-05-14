import logging
import sys

from pathlib import Path

from typing import Tuple
import numpy as np
from mne import find_events
from mne.io import Raw

from utils.exceptions import SubjectNotProcessedError
from utils.file_access import read_raw_format

########################################################################################################################
# DOWNSAMPLING                                                                                                         #
########################################################################################################################


def downsample(raw: Raw, sfreq: int, n_jobs) -> Tuple[Raw, np.array, np.array]:
    """
    Downsample to some lower sampling frequency
    :param raw: raw object
    :param sfreq: sampling frequency
    :param n_jobs: number of jobs for parallelism
    :return:
        raw: resampled raw object
        events: original events (needed for validating events)
        new_events: events with new sampling frequency
    """

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

        raw, new_events = raw.resample(sfreq=sfreq, events=events, n_jobs=n_jobs)

        return raw, events, new_events
    else:
        return raw, events, events


if __name__ == "__main__":

    # Read parameters
    raw_path = sys.argv[1]
    format = sys.argv[2]
    sfreq = int(sys.argv[3])
    n_jobs = int(sys.argv[4])
    dst_dir = Path(sys.argv[5])
    file_name = sys.argv[6]

    # Read raw
    raw = read_raw_format(raw_path, format)

    # Downsample
    raw, events, new_events = downsample(raw=raw, sfreq=sfreq)

    # Save to file
    raw.save(dst_dir / f"{file_name}-downsampled-{sfreq}-raw.fif")
    np.save(dst_dir / f"{file_name}-downsampled-{sfreq}-original-events.npy")
    np.save(dst_dir / f"{file_name}-downsampled-{sfreq}-new-events.npy")
