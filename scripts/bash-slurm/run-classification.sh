#!/bin/bash

#SBATCH --job-name=classification
#SBATCH --array=0-68  ## parcel ID
#SBATCH --ntasks-per-node=30   ## number of cores per parcel
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs/classification
#SBATCH --mem-per-cpu=3gb

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts/py_slurm  # scripts directory
param_dir=/data/home/hiroyoshi/mous_wd/param-dir                    # parameter directory

export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python $scripts_dir/run_classification.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE $param_dir