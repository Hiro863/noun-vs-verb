#!/bin/bash

#SBATCH --job-name=test_dataset
#SBATCH --array=0-447          ## cortical area IDs, for aparc_sub
#SBATCH --ntasks-per-node=10   ## number of cores per subject
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs
#SBATCH --mem=15gb


export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python /data/home/hiroyoshi/scripts/meg-mvpa/scripts/run_dataset.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE