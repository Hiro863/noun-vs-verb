#!/bin/bash


#SBATCH --ntasks-per-node=10

#SBATCH --job-name=freesurfer-test
#SBATCH --mail-type=BEGIN,END,
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr

#SBATCH --chdir=logs

#SBATCH --mem=10gb
#SBATCH --ntasks=10

export FREESURFER_HOME=/data/home/hiroyoshi/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh
export SUBJECTS_DIR=/data/home/hiroyoshi/freesurfer/subjects

my_subject=sub-V1004
my_NIfTI=/data/home/hiroyoshi/data/MOUS/sub-V1004/anat/sub-V1004_T1w.nii
srun recon-all -i $my_NIfTI -s $my_subject -all


