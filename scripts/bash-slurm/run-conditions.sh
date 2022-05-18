#!/bin/bash

#SBATCH --job-name=conditions
#SBATCH --array=0,14,16,22,24,28,30,36,38,40,60,62,64,66   ##14,22,60,62  ##1-447 cortical area IDs, for aparc_sub
#SBATCH --ntasks-per-node=1   ## number of cores per subject
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs/conditions
#SBATCH --mem-per-cpu=3gb

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts/py_slurm  # scripts directory
param_dir=/data/home/hiroyoshi/semi-final/param-dir/conditions                    # parameter directory


export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python $scripts_dir/run_conditions.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE $param_dir