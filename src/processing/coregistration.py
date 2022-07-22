from pathlib import Path
from mne.coreg import Coregistration
from mne import Info, setup_source_space, make_bem_model, make_bem_solution, make_forward_solution


def get_trans(subject: str, subjects_dir: Path, info: Info):
    # todo

    coreg = Coregistration(info, subject=subject, subjects_dir=subjects_dir, fiducials="auto")
    coreg.fit_icp(n_iterations=6, nasion_weight=2.)
    coreg.omit_head_shape_points(distance=5. / 1000)
    coreg.fit_icp(n_iterations=20, nasion_weight=10.)
    return coreg.trans


def get_forward(info: Info, trans: str, subject: str, subjects_dir: Path, layers):
    # todo

    src = setup_source_space(subject, spacing="ico5", add_dist="patch", subjects_dir=subjects_dir)

    if layers == 3:
        conductivity = (0.3, 0.006, 0.3)    # for three layers
    elif layers == 1:
        conductivity = (0.3,)  # for single layer
    else:
        raise ValueError(f"Invalid layer number \"{layers}\" was given")

    model = make_bem_model(subject=subject, ico=5, conductivity=conductivity, subjects_dir=subjects_dir)
    bem = make_bem_solution(model)

    fwd = make_forward_solution(info=info, trans=trans, src=src, bem=bem,
                                meg=True, eeg=False, mindist=5.0, n_jobs=1,
                                verbose=True)
    return fwd
