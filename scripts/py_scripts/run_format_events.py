from pathlib import Path
import os
import re

from events.formatting import format_event_data

SRC_DIR = Path("/Users/yamazakihiroyoshi/Desktop/events-src")
DST_DIR = Path("/Users/yamazakihiroyoshi/Desktop/events-dst")
STIMULI_PATH = Path("/Users/yamazakihiroyoshi/Desktop/Stage/stimuli-processing/stimuli-modified-cropped.txt")

skip = ["sub-V1044", "sub-V1032", "sub-V1086", "sub-V1038", "sub-V1104", "sub-V1033", "sub-V1080",
        "sub-V1042"]


def main():

    for file in os.listdir(SRC_DIR):
        print(f"Processing the file {file}")

        if re.match(r"^sub-V\d+_task-visual_events\.tsv", file):

            subject_name = re.findall(r"^sub-V\d+", file)[0]

            if subject_name not in skip:

                events_df, rejected_list = format_event_data(SRC_DIR / file, STIMULI_PATH)
                events_df.to_csv(DST_DIR / f"{subject_name}-clean-events.csv")

                if len(rejected_list) > 0:
                    with open(DST_DIR / f"rejected-{subject_name}.txt", "w") as f:
                        f.write("\n".join(rejected_list))
            else:
                print(f"skipping the subject {subject_name}")


if __name__ == "__main__":
    main()


