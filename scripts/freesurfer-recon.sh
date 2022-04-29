#!/bin/bash

#SBATCH --array=sub-V1001,sub-V1003,sub-V1004          ## subject IDs
#SBATCH --ntasks-per-node=10
#SBATCH --job-name=freesurfer-recon-all
#SBATCH --mail-type=BEGIN,END,
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs
#SBATCH --mem=10gb

export FREESURFER_HOME=/data/home/hiroyoshi/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=/data/home/hiroyoshi/freesurfer/subjects

my_subject="${SLURM_ARRAY_TASK_ID}"
my_NIfTI="/data/home/hiroyoshi/data/MOUS/${SLURM_ARRAY_TASK_ID}/anat/${SLURM_ARRAY_TASK_ID}_T1w.nii"
srun recon-all -i $my_NIfTI -s $my_subject -all


