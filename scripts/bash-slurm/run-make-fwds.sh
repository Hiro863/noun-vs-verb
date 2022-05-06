#!/bin/bash

#SBATCH --job-name=forward-model
#SBATCH --array=1-117
#SBATCH --ntasks-per-node=1   ## number of cores per subject
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs
#SBATCH --mem=10gb

# Skip non-existent subjects
no_subject=(14 15 18 21 23 41 43 47 51 56 60 67 82 91 112)  # non-existent subjects
if [[ ${no_subject[*]} =~ ^${SLURM_ARRAY_TASK_ID}$ ]]; then
  echo "Subject ${SLURM_ARRAY_TASK_ID} does not exist"
  exit 0
fi

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts  # scripts directory
mous_dir=/data/home/hiroyoshi/data/MOUS                    # data directory
subjects_dir=/data/home/hiroyoshi/freesurfer/subjects      # freesurfer subjects
fwd_dir=/data/home/hiroyoshi/data/MOUS/fwds                # directory to save forward models

export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa

python $scripts_dir/make_fwds.py $mous_dir $subjects_dir $fwd_dir $SLURM_ARRAY_TASK_ID