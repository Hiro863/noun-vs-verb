#!/bin/bash

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts/bash-slurm  # scripts directory

job_id1=$(sbatch $scripts_dir/run-preprocessing.sh)
sbatch --dependency=aferok:$job_id1 $scripts_dir/run-source-localization.sh
