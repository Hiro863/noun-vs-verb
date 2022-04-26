#!/bin/bash

#SBATCH --array=1
#SBATCH --ntasks-per-node=10

#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=user@univ-amu.fr

#SBATCH --chdir=logs

python3 script/data/home/hiroyoshi/scripts/meg-mvpa/scripts/test_script.py