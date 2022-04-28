#!/bin/bash

#SBATCH --array=0, 1, 2, 3,
#SBATCH --ntasks-per-node=10

#SBATCH --job-name=test_dataset
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr

#SBATCH --chdir=logs

#SBATCH --mem=15gb
#SBATCH --ntasks=10


export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python scripts/meg-mvpa/scripts/test_dataset.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE