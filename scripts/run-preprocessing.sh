#!/bin/bash

#SBATCH --job-name=preprocessing
#SBATCH --array=9,10,11,20,22,24,25,26,27,28,29,30,31,32,34,35,36,37,38,39
#SBATCH --ntasks-per-node=10   ## number of cores per subject

#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr

#SBATCH --chdir=/data/home/hiroyoshi/logs

#SBATCH --mem=100gb   ## filtering and ICA requires memory
## finished: 1, 2, 3, 4, 5, 7
## skipped: 6
##,2,3,4,5,6,7,8,9,10,11,12,13,15,16,17,19,20       ## subject IDs

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts  # scripts directory
param_dir=/data/home/hiroyoshi/results/param-dir           # parameter directory

export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa

python $scripts_dir/run_preprocessing.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE $param_dir