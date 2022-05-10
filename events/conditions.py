import pandas as pd
import numpy as np


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

    id_to_nv = load_to_nv(csv_path, to_index)
    for item in y:
        if item in id_to_nv:
            conditions.append(id_to_nv[item])
            tokens.append(item)

    return np.array([conditions, tokens])