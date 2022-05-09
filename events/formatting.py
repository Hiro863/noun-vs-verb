import logging
from math import isnan
import re
import sys
import numpy as np
import pandas as pd

fmt = "%(levelname)s :: %(asctime)s :: Process ID %(process)s :: %(module)s :: " + \
      "%(funcName)s() :: Line %(lineno)d :: %(message)s"

logging.basicConfig(level=logging.DEBUG,
                    format=fmt,
                    handlers=[logging.StreamHandler(sys.stdout)])

id_to_name = {1: "word",
              2: "word",
              3: "word",
              4: "word",
              5: "word",
              6: "word",
              7: "word",
              8: "word",
              10: "block",
              15: "offset",
              20: "fixation",
              30: "pause",
              40: "question",
              # Re-assigned IDs (these are assigned 1-3 which overlaps with word conditions)
              50: "response/1",
              60: "response/2",
              70: "response/3"}

########################################################################################################################
# STIMULI PROCESSING                                                                                                   #
########################################################################################################################
# Processing related to stimuli prior to running the dataset generation pipeline. Can be run independently of the      #
# said pipeline. It can also be combined with manual correction.                                                       #
# `format_event_data` can be used to convert `event.tsv` into cleaner format                                           #
########################################################################################################################


def assign_ids(text: str):
    """
    From stimuli.txt content construct two dictionaries by assigning and ID to every token in the text.
    :param text: text file of stimuli.txt. Contains list of stimuli in the format: [stimulus no.] [sentence/list]\n
    :return:
        id_to_word: dictionary, key = token ID, value = token string
        position_to_id: dictionary, key = sentence number, value = dictionary {position in sentence: token ID}
    """
    ids = 0
    id_to_word = {}
    position_to_id = {}

    for line in text.splitlines():
        sentence_id = int(re.findall(r"^\d+(?=\s)", line)[0])
        line = re.sub(r"\d+", "", line)  # remove the sentence number
        position_to_id[sentence_id] = {}

        words = line.split()
        for pos, word in enumerate(words):
            id_to_word[ids] = word
            position_to_id[sentence_id][pos] = ids
            ids += 1

    return id_to_word, position_to_id


def _clean_df(df):
    sample_list = []
    type_list = []
    onset_list = []
    form_list = []

    curr_sample = 1
    curr_event = []
    for idx, row in df.iterrows():

        if row["sample"] in [curr_sample, curr_sample + 1]:  # sample value can vary by max. 1 sample
            curr_event.append(row)

        else:  # new event
            _match_event(curr_event, sample_list, type_list, onset_list, form_list)
            curr_sample = row["sample"]
            curr_event = [row]

    df = pd.DataFrame()
    df["sample"] = sample_list
    df["type"] = type_list
    df["onset"] = onset_list
    df["form"] = form_list
    return df


def _match_event(events, sample_list, type_list, onset_list, form_list):
    matched = False
    event_name = None
    form = None

    for row in events:

        # Response
        if row["type"] == "Response":

            event_name = "response/"

            if row["value"] == "1":
                event_name += "1"
            elif row["value"] == "2":
                event_name += "2"
            elif row["value"] == "3":
                event_name += "3"

            matched = True
            break

        elif row["type"] in ["trial", "UDIO001"]:  # ignore these
            break

        elif row["type"] == "Picture":
            if re.match(r"(ZINNEN|WOORDEN).*", row["value"]):
                event_name = "block"
                matched = True
                form = row["value"]
                break

            elif row["value"].startswith("FIX"):
                event_name = "fixation"
                matched = True
                break

            elif row["value"].startswith("QUESTION"):
                event_name = "question"
                matched = True
                break

            elif row["value"] in ["blank", "pause", "ISI", "PULSE MODE 0", "PULSE MODE 1", "PULSE MODE 2", "PULSE MODE 3", "PULSE MODE 4", "PULSE MODE 5"]:  # ignore, TODO CHECK OUT PULSE MODES
                break

            # Word
            elif re.match(r"^\d\s?[a-zA-Z]+", row["value"]):
                event_name = "word"
                form = row["value"]
                form = re.sub(r"\d|\s|\.", "", form)  # remove space and numbers
                matched = True
                break

            elif re.match(r"^\d+\s+\d+", row["value"]):  # e.g. 5 300
                event_name = "empty"
                form = ""
                matched = True
                break

            else:
                t, v = row["type"], row["value"]
                raise ValueError(f"The row with type '{t}' and value '{v}' was not matched")

    if matched:
        sample_list.append(events[0]["sample"])
        type_list.append(event_name)
        onset_list.append(events[0]["onset"])
        form_list.append(form)


def _add_sentence_column(df, stimuli_text):

    df["sentence"] = ""
    df["position"] = ""

    word_list = None
    rejected_list = []

    for idx, row in df.iterrows():

        if row["type"] == "fixation":  # new sentence is preceded by "fixation"

            df = _modify_df(df, word_list, stimuli_text, rejected_list)

            word_list = []

        elif row["type"] == "word":
            word_list.append((idx, row["form"]))  # remember index: word matching

    df = _modify_df(df, word_list, stimuli_text, rejected_list)
    return df, rejected_list


def _modify_df(df, word_list, stimuli_text, rejected_list):
    if word_list is not None:

        # Find the sentence that matches the list of words given here
        sentence_number = _find_sentence(word_list, stimuli_text)
        if sentence_number is None:
            words = [y for x, y in word_list]  # word_list is a list of tuples
            rejected = " ".join(words)
            rejected_list.append(rejected)
            logging.debug(f"The sentence '{rejected}' was rejected")

        # Modify the DataFrame
        for s_idx, (w_idx, word) in enumerate(word_list):
            df.at[w_idx, "sentence"] = sentence_number
            df.at[w_idx, "position"] = s_idx  # position with the sentence
    return df


def _find_sentence(word_list, stimuli_text):

    stimuli_list = stimuli_text.splitlines()
    for stimulus in stimuli_list:
        stimulus_words = stimulus.split()
        sentence_number = int(stimulus_words[0])  # first element is the sentence number
        stimulus_words = stimulus_words[1:]       # the rest are the real sentences

        # Assume a match until it fails
        found = True
        min_length = min(len(word_list), len(stimulus_words))  # to avoid out of range error
        for idx in range(min_length):
            if stimulus_words[idx].lower() != word_list[idx][1].lower():  # word_list is a list of tuples (index, word)
                found = False
                break

        if found:
            return sentence_number

    return None


def _add_ids(df, position_to_id):

    df["ID"] = ""

    for idx, row in df.iterrows():
        sentence_number = row["sentence"]
        position = row["position"]
        if sentence_number is not None and position != "":  # missing sentence or position
            token_id = position_to_id[sentence_number][position]
            df.at[idx, "ID"] = token_id

    return df


def format_event_data(events_path, stimuli_path):
    events_df = pd.read_csv(events_path, sep="\t")
    with open(stimuli_path, "r") as f:
        stimuli_text = f.read()

    _, position_to_id = assign_ids(stimuli_text)

    events_df = _clean_df(events_df)
    events_df, rejected_list = _add_sentence_column(events_df, stimuli_text)
    events_df = _add_ids(events_df, position_to_id)
    return events_df, rejected_list

########################################################################################################################
# EVENT VALIDATION                                                                                                     #
########################################################################################################################
# Validating the events array generated by MNE signals. Reject any events that are inconsistent                        #
########################################################################################################################


def _simplify(events):
    for event in events:
        if event[2] < 10:
            event[2] = 1

    return events
# todo: make sure that events are long enough (2>
# todo: make sure new and old event have the same shape
def get_event_array(events, event_path):  # todo: tidy

    # events = mne.find_events(raw)
    original_events = events[0]
    new_events = events[1]
    df = pd.read_csv(event_path)

    valid_events = []
    invalid_events = []
    id_events = []  # identical to valid_events except instead of event ID, use token ID
    for idx, o_event in enumerate(original_events):

        # Ignore events that are not in the dictionary
        if o_event[2] in id_to_name:
            mne_event = id_to_name[o_event[2]]
        else:
            continue

        # Sample value can vary by maximum on 1 on either side
        if o_event[0] in df["sample"].values:
            df_event = df.loc[df["sample"] == o_event[0]]
        elif o_event[0] - 1 in df["sample"].values:
            df_event = df.loc[df["sample"] == o_event[0] - 1]
        elif o_event[0] + 1 in df["sample"].values:
            df_event = df.loc[df["sample"] == o_event[0] + 1]
        else:
            invalid_events.append(o_event)
            continue

        # The event name is identical
        if df_event["type"].values[0] == mne_event:
            event = new_events[idx].copy()
            token = new_events[idx].copy()
            token[2] = int(df_event["ID"].values[0]) if not isnan(df_event["ID"].values[0]) else -1
            valid_events.append(event)
            id_events.append(token)

        # Check for response, because they reflect response values (1, 2 or 3) rather than event type
        elif df_event["type"].values[0].startswith("response") and mne_event == "word":
            value = int(df_event["type"].values[0][-1])  # 1, 2 or 3, e.g. "response/1"
            if value == o_event[2]:
                event = new_events[idx].copy()
                token = new_events[idx].copy()
                token[2] = int(df_event["ID"].values[0]) if not isnan(df_event["ID"].values[0]) else -1
                valid_events.append(event)
                id_events.append(token)

        # These are neither valid nor relevant
        elif mne_event == "word" and df_event["type"].values[0] == "empty":  # blank "words", e.g. 5 300
            pass
        else:
            invalid_events.append(o_event)

    logging.debug(f"{len(valid_events) / (len(valid_events) + len(invalid_events)) * 100}% valid")
    logging.debug(f"Total of {len(valid_events)} events added")

    events = np.array(valid_events)
    id_events = np.array(id_events)

    events = _simplify(events)
    return events, id_events


def crop_events(events, id_events):
    event_list = []
    id_event_list = []

    for event, id_event in zip(events, id_events):
        if event[2] in id_to_name:
            if id_to_name[event[2]] == "word":
                event_list.append(event)
                id_event_list.append(id_event)

    events = np.array(events)
    id_events = np.array(id_event_list)
    return events, id_events
