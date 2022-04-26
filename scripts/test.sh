#!/bin/bash

#SBATCH --array=1
#SBATCH --ntasks-per-node=10

#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=user@univ-amu.fr

#SBATCH --chdir=logs

export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python scripts/meg-mvpa/scripts/test_script.py