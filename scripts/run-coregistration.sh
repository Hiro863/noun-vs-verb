#!/bin/bash

#SBATCH --job-name=test_preprocessing
#SBATCH --array=1          ## subject IDs
#SBATCH --ntasks-per-node=10   ## number of cores per subject

#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr

#SBATCH --chdir=/data/home/hiroyoshi/logs

#SBATCH --mem=15gb

param_dir=/data/home/hiroyoshi/params

export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts
python $scripts_dir/run_coregstration.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE $param_dir