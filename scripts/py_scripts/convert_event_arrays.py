import sys
from events.condition_ import convert_to_nv

name_to_mapper = {"noun-verb": convert_to_nv}


def main(dictionary_path, mapping):



    pass


if __name__ == "__main__":
    dictionary_path = sys.argv[1]
    mapping = sys.argv[2]

    main(dictionary_path, mapping)



