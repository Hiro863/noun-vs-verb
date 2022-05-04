from pathlib import Path
from mne.coreg import Coregistration
from mne import (Info, write_trans, setup_source_space, make_bem_model, make_bem_solution, make_forward_solution,
                 write_forward_solution)


def make_trans(subject: str, dst_dir: Path, subjects_dir: Path, info: Info):
    coreg = Coregistration(info, subject=subject, subjects_dir=subjects_dir, fiducials="estimated")
    coreg.fit_icp(n_iterations=6, nasion_weight=2.)
    coreg.omit_head_shape_points(distance=5. / 1000)
    coreg.fit_icp(n_iterations=20, nasion_weight=10.)
    write_trans(str(dst_dir / f"{subject}-trans.fif"), coreg.trans)


def make_forward(raw_path: str, trans: str, bem: str, subject: str, subjects_dir: Path, dst_dir: Path):
    src = setup_source_space(subject, spacing="ico5", add_dist="patch", subjects_dir=subjects_dir)

    # conductivity = (0.3,)             # for single layer
    conductivity = (0.3, 0.006, 0.3)    # for three layers

    model = make_bem_model(subject=subject, ico=5, conductivity=conductivity, subjects_dir=subjects_dir)
    bem = make_bem_solution(model)

    fwd = make_forward_solution(raw_path, trans=trans, src=src, bem=bem,
                                meg=True, eeg=False, mindist=5.0, n_jobs=1,
                                verbose=True)

    write_forward_solution(str(dst_dir / f"{subject}-fwd.fif"), fwd, overwrite=True)
