#!/bin/bash

#SBATCH --array=110,111,113,114,115,116,117
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=freesurfer-recon-all
#SBATCH --mail-type=BEGIN,END,
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs
#SBATCH --mem=10gb

export FREESURFER_HOME=/data/home/hiroyoshi/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=/data/home/hiroyoshi/freesurfer/subjects

my_subject="sub-V10${SLURM_ARRAY_TASK_ID}"
my_NIfTI="/data/home/hiroyoshi/data/MOUS/sub-V1${SLURM_ARRAY_TASK_ID}/anat/sub-V1${SLURM_ARRAY_TASK_ID}_T1w.nii"
srun recon-all -i $my_NIfTI -s $my_subject -all


