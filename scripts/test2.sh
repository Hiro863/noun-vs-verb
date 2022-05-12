#!/bin/bash

#SBATCH --job-name=test2
#SBATCH --array=1
#SBATCH --ntasks-per-node=1
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs
#SBATCH --mem-per-cpu=1gb

echo $SLURM_ARRAY_TASK_ID



