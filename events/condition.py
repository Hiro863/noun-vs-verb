import logging
import numpy as np
import pandas as pd

fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"

logging.basicConfig(level=logging.DEBUG, filename="../../data/logs/debug.log", format=fmt)


def generate_id_df(id_to_word, dictionary):

    token_ids = []
    forms = []
    mapped = []
    for id_val, word in id_to_word.items():

        token_ids.append(id_val)
        forms.append(word)

        # Match indices
        matches = dictionary.index[dictionary.Form == word].tolist()
        if len(matches) == 1:
            mapped.append(matches[0])
        elif len(matches) > 1:
            mapped.append(-1)  # ambiguous cases must be matched by hand, mark by -1
        else:
            mapped.append(-2)  # items not found must be matched by hand, mark by -2

    df = pd.DataFrame()
    df["token ID"] = token_ids
    df["Form"] = forms
    df["meaning ID"] = mapped
    return df


def get_token_to_meaning_dict(df_path, missing="drop"):
    df = pd.read_csv(df_path)

    if missing == "drop":
        df.drop(df[df["meaning ID"] < 0].index, inplace=True)  # drop ambiguous cases

    token_to_meaning = {row["token ID"]: row["meaning ID"] for _, row in df.iterrows()}
    return token_to_meaning


def convert(events, mapper, token_to_meaning, dictionary):

    event_list = []
    index_list = []
    rejected_list = []
    for idx, event in enumerate(events):
        if event in token_to_meaning:
            valid, condition_id = mapper(token_to_meaning[event], dictionary)
            if valid:
                event_list.append(condition_id)
                index_list.append(idx)
            else:
                rejected_list.append(event)
        else:
            rejected_list.append(event)

    new_events = np.array(event_list)
    indices = np.array(index_list)

    # Calculate missing amount
    n_total = events.shape[0]
    n_rejected = len(rejected_list)
    logging.debug(f"{n_rejected} items out of {n_total} ({n_rejected / n_total * 100:.2f}%) "
                  f"rejected due to missing data")

    return new_events, indices


def balance(events):
    conditions = list(set(events[:, 2]))

    separated = {}
    for condition in conditions:
        separated[condition] = events[np.where(events[:, 2] == condition)]


########################################################################################################################
# PART OF SPEECH                                                                                                       #
########################################################################################################################


pos_dict = {"N": 1,
            "V": 2,
            "ADJ": 3,
            "ADV": 4,
            "PREP": 5,
            "CONJ": 6}


def convert_to_pos(meaning_id, dictionary, picks=("V", "N"),
                   include_ambiguous=False, include_homonyms=False):  # todo: fix picks

    match = dictionary.iloc[[meaning_id]]
    if match["Ambiguous"].values[0] and not include_ambiguous:
        valid = False
        return valid, -1
    if match["Homonyms"].values[0] and not include_homonyms:
        valid = False
        return valid, -1

    pos = match["POS"].values[0]

    condition_id = -1
    valid = False
    if type(pos) == str:
        if pos in picks:
            if pos in pos_dict:
                condition_id = pos_dict[pos]
                valid = True

    return valid, condition_id

########################################################################################################################
# INFLECTIONS                                                                                                          #
########################################################################################################################

# todo: inflections
