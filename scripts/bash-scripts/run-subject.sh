#!/bin/bash

#SBATCH --job-name=subject
#SBATCH --array=1     ###30,40   ##0-67     ##1-447          ## cortical area IDs, for aparc_sub
#SBATCH --ntasks-per-node=1   ## number of cores per subject
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs/conditions
#SBATCH --mem-per-cpu=3gb

scripts=/data/home/hiroyoshi/scripts/meg-mvpa/processing/downsample.py  # scripts directory
json=/data/home/hiroyoshi/mous_wd/param-dir/downsample-params.json                    # parameter directory


export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python scripts $json