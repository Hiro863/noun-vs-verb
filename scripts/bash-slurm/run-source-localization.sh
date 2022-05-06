#!/bin/bash

#SBATCH --job-name=source-localization
#SBATCH --array=1-2  #117           ## subject IDs
#SBATCH --ntasks-per-node=1         ## number of cores per subject
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs
#SBATCH --mem-per-cpu=10gb

# Skip non-existent subjects
no_subject=(14 15 18 21 23 41 43 47 51 56 60 67 82 91 112)  # non-existent subjects
if [[ ${no_subject[*]} =~ ^${SLURM_ARRAY_TASK_ID}$ ]]; then
  echo "Subject ${SLURM_ARRAY_TASK_ID} does not exist"
  exit 0
fi

scripts_dir=/data/home/hiroyoshi/scripts/meg-mvpa/scripts/py_slurm  # scripts directory
param_dir=/data/home/hiroyoshi/results/param-dir                    # parameter directory

export PYTHONPATH=$PYTHONPATH:/data/home/hiroyoshi/scripts/meg-mvpa
python $scripts_dir/run_source_localization.py $SLURM_ARRAY_TASK_ID $SLURM_NTASKS_PER_NODE $param_dir