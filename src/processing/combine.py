import numpy as np

# todo what is this and is this needed?
def _get_labels(indices):
    return []

def _get_data(label):
    return 0


def combine(dst_dir, subject, params):

    labels = _get_labels(params["indices"])

    data_list = []
    for label in labels:
        data_list.append(_get_data(label))

    data = np.concatenate(data_list, axis=1)  # n_samples x n_dipoles x n_times

    np.save(dst_dir / params["name"], data)

if __name__ == "__main__":
    pass