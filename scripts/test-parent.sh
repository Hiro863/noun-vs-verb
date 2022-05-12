#!/bin/bash

#SBATCH --job-name=test-parent
#SBATCH --array=1
#SBATCH --ntasks-per-node=1
#SBATCH --mail-type=BEGIN,END
#SBATCH --mail-user=hiroyoshi.yamasaki@etu.univ-amu.fr
#SBATCH --chdir=/data/home/hiroyoshi/logs
#SBATCH --mem-per-cpu=1gb




job_id1=$(sbatch test.sh)

sbatch  --dependency=afterany:$job_id1 --mem=1g test2.sh