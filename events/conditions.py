from pathlib import Path
import pandas as pd
import numpy as np


########################################################################################################################
#
########################################################################################################################

def convert_y(y: np.array, mode: str, df_dir: Path, to_index: bool, params: dict):

    if mode == "nv":
        id_to_cond = _to_nv(df_dir=df_dir, to_index=to_index, params=params)

    elif mode == "length":
        id_to_cond = _to_length(df_dir=df_dir, to_index=to_index, params=params)

    elif mode == "frequency":
        id_to_cond = _to_frequency(df_dir=df_dir, to_index=to_index, params=params)

    elif mode == "tense":
        id_to_cond = _to_tense(df_dir=df_dir, to_index=to_index, params=params)

    elif mode == "v-number":
        id_to_cond = _to_v_number(df_dir=df_dir, to_index=to_index, params=params)

    elif mode == "voice":
        id_to_cond = _to_voice(df_dir=df_dir, to_index=to_index, params=params)

    elif mode == "gender":
        id_to_cond = _to_gender(df_dir=df_dir, to_index=to_index, params=params)

    elif mode == "n-number":
        id_to_cond = _to_n_number(df_dir=df_dir, to_index=to_index, params=params)

    else:
        raise ValueError(f"Unknown mode \'{mode}\'")

    y, included = _to_arrays(y, id_to_cond)

    # Balance the number of items per class
    if params["balance"]:
        y, idx = _balance_classes(y)
        included = included[idx]

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


def _balance_classes(y):
    classes = list(set(y[0].tolist()))

    # get least frequent class
    counts = np.bincount(y[0])
    least_class = counts.argmin()
    size = counts[least_class]

    idx_list = []
    for cl in classes:
        idx = np.where(y[0] == cl)
        idx = np.random.choice(idx[0], size, replace=False)
        idx_list.append(idx)

    idx = np.concatenate(idx_list)
    y = y[:, idx]
    return y, idx


########################################################################################################################


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

    # Remove items not found in the verb and noun dataframes
    df_v = pd.merge(nv_df, v_df, how="left", on="Token ID").dropna(axis=0)[["Token ID", "POS"]]
    df_n = pd.merge(nv_df, n_df, how="left", on="Token ID").dropna(axis=0)[["Token ID", "POS"]]
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


########################################################################################################################


def _to_length(df_dir, to_index, params):
    df = pd.read_csv(df_dir / "NV.csv")

    df["Length"] = df["Word"].apply(lambda x: len(x))

    # Conditions for grouping into 3 groups
    conditions = [(df["Length"] < params["lower"]),
                  (params["lower"] <= df["Length"]) & (df["Length"] < params["upper"]),
                  (params["upper"] <= df["Length"])]
    df["Group"] = np.select(conditions, ["short", "medium", "long"])

    if not params["medium"]:
        df["Group"] = df[(df["Group"] == "short") | (df["Group"] == "long")]["Group"]
        mapper = {"short": 0, "long": 1}
    else:
        mapper = {"short": 0,  "medium": 1, "long": 2}

    return _to_dict(df=df, key="Token ID", column="Group", mapper=mapper, to_index=to_index)


def _to_frequency(df_dir, to_index, params):
    df = pd.read_csv(df_dir / "NV.csv")
    sub = pd.read_csv(df_dir / "SUBTLEX-NL.csv")
    df = pd.merge(df, sub, how="left", on="Word")
    df = df[["Token ID", "Frequency", "CD", "POS"]]

    if params["mode"] == "noun":
        df = df[df["POS"] == "N"]
    elif params["mode"] == "verb":
        df = df[df["POS"]]

    #todo
    return _to_dict(df=df, key="Token ID", column="Group", mapper=None, to_index=to_index)


########################################################################################################################


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


########################################################################################################################


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