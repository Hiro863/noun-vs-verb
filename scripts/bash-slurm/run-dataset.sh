#!/bin/bash

#SBATCH --job-name=dataset
#SBATCH --array=0,14,16,22,24,28,30,36,38,40,60,62,64,66       ###0-68  ## -68  ##1-447cortical area IDs, for aparc_sub
#SBATCH --ntasks-per-node=1   ## number of cores per subject
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs/dataset
#SBATCH --mem-per-cpu=15gb

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts/py_slurm  # scripts directory
param_dir=/data/home/hiroyoshi/semi-final/param-dir                    # parameter directory


export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python $scripts_dir/run_dataset.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE $param_dir