import logging
import sys

from pathlib import Path

from mne.io import Raw

from utils.file_access import read_raw_format


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


if __name__ == "__main__":

    # Read parameters
    raw_path = sys.argv[1]
    format = sys.argv[2]
    l_freq = int(sys.argv[3])
    h_freq = int(sys.argv[4])
    notch = int(sys.argv[5])  # todo, pass list
    dst_dir = Path(sys.argv[6])
    file_name = sys.argv[7]
    n_jobs = int(sys.argv[8])

    # Read raw
    raw = read_raw_format(raw_path, format)

    # Filter
    raw = apply_filter(raw=raw, l_freq=l_freq, h_freq=h_freq, notch=[notch], n_jobs=n_jobs)

    # Save to file
    raw.save(dst_dir / f"{file_name}-filtered-{l_freq}-{h_freq}Hz-raw.fif")
