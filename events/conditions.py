from pathlib import Path
import pandas as pd
import numpy as np


modes = {"nv": None,
         "length": None, "frequency": None,
         "tense": None, "v-number": None, "voice": None,
         "gender": None, "n-number": None
         }

SUBTLEX_PATH = Path("/Users/yamazakihiroyoshi/Desktop/InCog/meg-mvpa/data")


def convert_y(y, mode, df_dir, to_index, params):

    id_to_cond = None
    if mode == "nv":
        id_to_cond = _to_nv(df_dir=df_dir, to_index=to_index, params=params)

    elif mode == "length":
        pass
    elif mode == "frequency":
        pass
    elif mode == "tense":
        pass
    elif mode == "v-number":
        pass
    elif mode == "voice":
        pass
    elif mode == "gender":
        pass
    elif mode == "n-number":
        pass
    else:
        raise ValueError(f"Unknown mode \'{mode}\'")

    y, included = _to_arrays(y, id_to_cond)
    return y, included


def _to_dict(df, key, column, mapper, to_index):
    # mapper: {"N": 0, "V": 1}
    id_to_cond = {}

    for idx, row in df.iterrows():
        if to_index:
            id_to_cond[row[key]] = mapper[row[column]]
        else:
            id_to_cond[row[key]] = row[column]
    return id_to_cond


def _to_arrays(y, id_to_cond):
    conditions = []
    tokens = []
    included = []

    for idx, item in enumerate(y):
        if item in id_to_cond:
            conditions.append(id_to_cond[item])
            tokens.append(item)
            included.append(idx)

    return np.array([conditions, tokens]), np.array(included)


def _to_nv(df_dir, to_index, params):
    nv_df = pd.read_csv(df_dir / "NV.csv")
    v_df = pd.read_csv(df_dir / "Verbs-Grammatical.csv")
    n_df = pd.read_csv(df_dir / "Nouns-Grammatical.csv")

    v_df = _select_verbs(v_df, number=params["number"], tense=params["tense"], person=params["person"],
                         voice=params["voice"], allow_non_finite=params["finite"], allow_complex=params["complex"],
                         allow_aux=params["aux"])

    n_df = _select_nouns(n_df, allow_ambiguous_gender=params["ambiguous"], allow_common_gender=params["common"],
                         allow_diminutives=params["diminutive"], allow_uncountables=params["uncountable"],
                         allow_proper=params["proper"])

    df_v = pd.merge(nv_df, v_df, how="right", on="Token ID").dropna(axis=0)[["Token ID", "POS"]]
    df_n = pd.merge(nv_df, n_df, how="outer", on="Token ID").dropna(axis=0)[["Token ID", "POS"]]

    df = pd.concat([df_v, df_n])

    return _to_dict(df=df, key="Token ID", column="POS", mapper={"N": 0, "V": 1}, to_index=to_index)


def _select_verbs(verbs, number=None, tense=None, person=None, voice=None,
                  allow_non_finite=False, allow_complex=False, allow_aux=False):

    # Filter by number
    if number is not None:
        if number not in ["sg.", "pl."]:
            verbs["Number"] = verbs[verbs["Number"].isin(["sg.", "pl."])]

        verbs = verbs[verbs["Number"] == number]

    # Filter by tense
    if tense is not None:
        if tense not in ["present", "past"]:
            verbs = verbs[verbs["Tense"].isin(["present", "past"])]

        verbs = verbs[verbs["Tense"] == tense]

    # Filter by person
    if person is not None:
        if person not in [1, 2, 3]:
            verbs = verbs[verbs["Person"].isin([1, 2, 3])]

        verbs = verbs[verbs["Person"] == person]

    # Filter by voice
    if voice is not None:
        if tense not in ["active", "passive"]:
            verbs = verbs[verbs["Voice"].isin(["active", "passive"])]

        verbs = verbs[verbs["Voice"] == voice]

    # Filter by finiteness
    if allow_non_finite:
        verbs = verbs[verbs["Complex"] == "finite"]

    # Filter by simple (single word) vs complex (multiple word)
    if not allow_complex:
        verbs = verbs[verbs["Complex"] == False]

    # Filter auxiliary words
    if not allow_aux:
        verbs = verbs[verbs["Complex"] != "auxiliary"]

    return verbs


def _select_nouns(nouns, allow_ambiguous_gender=False, allow_common_gender=False,
                  allow_diminutives=False, allow_uncountables=False, allow_proper=False):
    # Filter ambiguous genders
    if not allow_ambiguous_gender:
        nouns = nouns[~nouns["Gender"].isin(["n./c.", "m./f."])]

    # Filter common gender
    if not allow_common_gender:
        nouns = nouns[~nouns["Gender"].isin(["n./c.", "c."])]

    # Filter diminutives
    if not allow_diminutives:
        nouns = nouns[nouns["Diminutive"] == False]

    # Filter uncountable
    if not allow_uncountables:
        nouns = nouns[nouns["Number"] != "uncount."]

    # Filter proper nouns
    if not allow_proper:
        nouns = nouns[nouns["Proper"] == False]

    return nouns


def _to_length(df_dir, to_index, params):
    df = pd.read_csv(df_dir / "NV.csv")

    df["Length"] = df["Word"].apply(lambda x: len(x))
    #return _to_dict(df=df, key="Token ID", column="Length", mapper=)


def _to_frequency(df_dir, to_index, params):
    pass


def _to_tense(df_dir, to_index, params):
    nv_df = pd.read_csv(df_dir / "NV.csv")
    v_df = pd.read_csv(df_dir / "Verbs-Grammatical.csv")

    if params["tense"] not in ["present", "past"]:
        tense = params["tense"]
        raise ValueError(f"allowed tenses are 'present' and 'past' but got '{tense}'")

    v_df = v_df[v_df["Tense"] == v_df]
    df = pd.merge(nv_df, v_df, how="right", on="Token ID")
    return _to_dict(df=df, key="Token ID", column="Tense", mapper={"present": 0, "past": 1}, to_index=to_index)


def _to_v_number(df_dir, to_index, params):
    nv_df = pd.read_csv(df_dir / "NV.csv")
    v_df = pd.read_csv(df_dir / "Verbs-Grammatical.csv")

    if params["v-number"] not in ["sg.", "pl."]:
        number = params["v-number"]
        raise ValueError(f"allowed numbers are 'sg.' and 'pl.' but got '{number}'")

    v_df = v_df[v_df["Number"] == v_df]
    df = pd.merge(nv_df, v_df, how="right", on="Token ID")
    return _to_dict(df=df, key="Token ID", column="Number", mapper={"sg.": 0, "pl.": 1}, to_index=to_index)


def _to_voice(df_dir, to_index, params):
    nv_df = pd.read_csv(df_dir / "NV.csv")
    v_df = pd.read_csv(df_dir / "Verbs-Grammatical.csv")

    if params["voice"] not in ["active", "passive"]:
        voice = params["voice"]
        raise ValueError(f"allowed tenses are 'active' and 'passive' but got '{voice}'")

    v_df = v_df[v_df["Voice"] == v_df]
    df = pd.merge(nv_df, v_df, how="right", on="Token ID")
    return _to_dict(df=df, key="Token ID", column="Voice", mapper={"active": 0, "passive": 1}, to_index=to_index)


def _to_gender(df_dir, to_index, params):
    nv_df = pd.read_csv(df_dir / "NV.csv")
    n_df = pd.read_csv(df_dir / "Nouns-Grammatical.csv")

    if params["gender"] not in ["m.", "f.", "n."]:
        gender = params["gender"]
        raise ValueError(f"allowed tenses are 'm.', 'f.' and 'n.' but got '{gender}'")

    n_df = n_df[n_df["Gender"] == n_df]
    df = pd.merge(nv_df, n_df, how="right", on="Token ID")
    return _to_dict(df=df, key="Token ID", column="Gender", mapper={"m.": 0, "f.": 1, "n.": 2}, to_index=to_index)


def _to_n_number(df_dir, to_index, params):
    nv_df = pd.read_csv(df_dir / "NV.csv")
    n_df = pd.read_csv(df_dir / "Nouns-Grammatical.csv")

    if params["n-number"] not in [1, 2, 3]:
        number = params["n-number"]
        raise ValueError(f"allowed numbers are '1', '2' and '3' but got '{number}'")

    n_df = n_df[n_df["Number"] == n_df]
    df = pd.merge(nv_df, n_df, how="right", on="Token ID")
    return _to_dict(df=df, key="Token ID", column="Number", mapper={1: 0, 2: 1, 3: 2}, to_index=to_index)

"""
def load_to_nv(path, to_index=False):
    df = pd.read_csv(path)

    id_to_nv = {}
    for idx, row in df.iterrows():
        if to_index:
            id_to_nv[row["Token ID"]] = 0 if row["POS"] == "N" else 1
        else:
            id_to_nv[row["Token ID"]] = row["POS"]
    return id_to_nv


def generate_frequency_table(tokens_path, subtlex_path):
    tokens = pd.read_csv(tokens_path)
    subtlex = pd.read_csv(subtlex_path)
    merged = pd.merge(subtlex, tokens, how="right", on="Word")
    merged = merged[["Token ID", "Word", "Meaning", "Frequency", "CD", "Lemma Frequency", "POS"]]
    return merged


def convert_to_nv(y, csv_path, to_index):
    conditions = []
    tokens = []
    included = []

    id_to_nv = load_to_nv(csv_path, to_index)
    for idx, item in enumerate(y):
        if item in id_to_nv:
            conditions.append(id_to_nv[item])
            tokens.append(item)
            included.append(idx)

    return np.array([conditions, tokens]), np.array(included)
"""
