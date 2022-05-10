import sys
import pandas as pd
from events.condition_ import convert_to_nv, get_token_to_meaning_dict, generate_id_df

name_to_mapper = {"noun-verb": convert_to_nv}


def main(dictionary_path, mapping):



    pass


if __name__ == "__main__":
    dictionary_path = sys.argv[1]
    mapping = sys.argv[2]

    main(dictionary_path, mapping)



