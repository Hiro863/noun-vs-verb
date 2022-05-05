import sys
import re
from pathlib import Path
from mne import write_forward_solution
from utils.file_access import get_mous_raw_paths, read_mous_subject
from processing.coregistration import get_trans, get_forward


def main(raw_dir, subjects_dir, fwd_dir):

    raw_paths = get_mous_raw_paths(raw_dir)

    failed_list = []
    for path, subject in raw_paths:
        if subject in ["sub-V1001", "sub-V1002", "sub-V1003", "sub-V1006"]:
            continue
        if re.match(r"^sub-A\d+", subject):  # e.g. sub-A2002
            continue
        print(subjects_dir)
        raw = read_mous_subject(path, preload=False)

        trans = get_trans(subject=subject, subjects_dir=subjects_dir, info=raw.info)
        """try:
            fwd = get_forward(info=raw.info, trans=trans, subject=subject, subjects_dir=subjects_dir, layers=3)
            write_forward_solution(fwd_dir / f"{subject}-fwd.fif", fwd, overwrite=True)
        except RuntimeError as e:
            print(f"Runtime error: {e}")
            print(f"Failed to make forward model with three layers for the subject {subject}")
            print("Trying one layer instead...")
            failed_list.append(f"{subject}: failed for 3 layers")"""

        try:
            fwd = get_forward(info=raw.info, trans=trans, subject=subject, subjects_dir=subjects_dir, layers=1)
            write_forward_solution(fwd_dir / f"{subject}-fwd.fif", fwd, overwrite=True)
        except RuntimeError as e:
            print(f"Runtime error: {e}")
            print(f"Failed to make forward model with one layers")
            failed_list.append(f"{subject}: failed for 1 layer")


if __name__ == "__main__":
    mous_dir = Path(sys.argv[1])
    subjects_dir = sys.argv[2]
    fwd_dir = Path(sys.argv[3])

    main(mous_dir, subjects_dir, fwd_dir)
