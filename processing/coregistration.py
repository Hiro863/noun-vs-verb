from pathlib import Path
from mne.coreg import Coregistration
from mne import Info, write_trans


def get_trans(subject: str, dst_dir: Path, subjects_dir: Path, info: Info):
    coreg = Coregistration(info, subject, subjects_dir, fiducials="estimated")
    coreg.fit_icp(n_iterations=6, nasion_weight=2.)
    coreg.omit_head_shape_points(distance=5. / 1000)
    coreg.fit_icp(n_iterations=20, nasion_weight=10.)
    write_trans(str(dst_dir / f"{subject}-trans.fif"), coreg.trans)
