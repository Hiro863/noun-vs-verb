#!/bin/bash

#SBATCH --job-name=preprocessing
#SBATCH --array=22,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,42,44,45,46,48,49,50,52,53,54,55,57,58,59
#SBATCH --ntasks-per-node=1   ## number of cores per subject

#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr

#SBATCH --chdir=/data/home/hiroyoshi/logs

#SBATCH --mem=10gb

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts  # scripts directory
mous_dir=/data/home/hiroyoshi/data/MOUS
subjects_dir=/data/home/hiroyoshi/freesurfer/subjects
fwd_dir=/data/home/hiroyoshi/data/MOUS/fwds

export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa

python $scripts_dir/make_fwds.py $mous_dir $subjects_dir $fwd_dir $SLURM_ARRAY_TASK_ID