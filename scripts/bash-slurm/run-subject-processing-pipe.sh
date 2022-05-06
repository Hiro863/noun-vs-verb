#!/bin/bash

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts/bash-slurm  # scripts directory

job_id1=$(sbatch $scripts_dir/run-preprocessing.sh)
sbatch $scripts_dir/run-source-localization.sh
