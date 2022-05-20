#!/bin/bash

#SBATCH --job-name=classification
#SBATCH --array=11
#SBATCH --ntasks-per-node=15   ## number of cores per parcel
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs/classification
#SBATCH --mem-per-cpu=15gb

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts/py_slurm  # scripts directory
param_dir=/data/home/hiroyoshi/semi-final/param-dir                    # parameter directory

export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python $scripts_dir/run_classification.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE $param_dir