#!/bin/bash

#SBATCH --array=1,2,3,4,5,7,8,9
#SBATCH --ntasks-per-node=10

#SBATCH --job-name=test_preprocessing
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr

#SBATCH --chdir=/data/home/hiroyoshi/logs

#SBATCH --mem=15gb
#SBATCH --ntasks=10


export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python /data/home/hiroyoshi/scripts/meg-mvpa/scripts/test_preprocessing.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE