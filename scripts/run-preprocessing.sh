#!/bin/bash

#SBATCH --job-name=preprocessing
#SBATCH --array=1
#SBATCH --ntasks-per-node=10   ## number of cores per subject

#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr

#SBATCH --chdir=/data/home/hiroyoshi/logs

#SBATCH --mem=30gb
##,2,3,4,5,6,7,8,9,10,11,12,13,15,16,17,19,20       ## subject IDs

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts  # scripts directory
param_dir=/data/home/hiroyoshi/results/param-dir           # parameter directory

export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa

python $scripts_dir/run_preprocessing.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE $param_dir