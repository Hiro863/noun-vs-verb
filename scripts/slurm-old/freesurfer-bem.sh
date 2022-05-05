#!/bin/bash

#SBATCH --array=1            ## subject ID
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=freesurfer-bem
#SBATCH --mail-type=BEGIN,END,
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs
#SBATCH --mem=10gb

export FREESURFER_HOME=/data/home/hiroyoshi/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=/data/home/hiroyoshi/freesurfer/subjects

my_subject="sub-V1%03d${SLURM_ARRAY_TASK_ID}"
mne watershed_bem -s sample



