from pathlib import Path
import numpy as np
from utils.file_access import read_json
from events.conditions import convert_to_nv


def convert_y(params):

    y = np.load(params["y-path"])

    y_nv, dropped = convert_to_nv(y, params["NV-path"], to_index=params["to-index"])

    np.save(str(Path(params["dst-dir"]) / "y-nv.npy"), y_nv)
    np.save(str(Path(params["dst-dir"]) / "included-nv.npy"), dropped)


if __name__ == "__main__":

    param_dir = Path("/Users/yamazakihiroyoshi/Desktop/InCog/meg-mvpa/data")
    params = read_json(param_dir, "conditions-params.json")

    convert_y(params)



