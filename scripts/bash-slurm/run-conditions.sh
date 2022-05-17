#!/bin/bash

#SBATCH --job-name=conditions
#SBATCH --array=30,40   ##0-67     ##1-447          ## cortical area IDs, for aparc_sub
#SBATCH --ntasks-per-node=1   ## number of cores per subject
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs/conditions
#SBATCH --mem-per-cpu=3gb

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts/py_slurm  # scripts directory
param_dir=/data/home/hiroyoshi/mous_wd/param-dir/conditions                    # parameter directory


export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python $scripts_dir/run_conditions.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE $param_dir