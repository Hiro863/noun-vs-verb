#!/bin/bash

export FREESURFER_HOME=/home/hiro/freesurfer
source $FREESURFER_HOME/SetUpFreeSurfer.sh

for subject in  sub-V1061 sub-V1062 sub-V1063 sub-V1064 sub-V1065 sub-V1066 sub-V1068 sub-V1069
do
  mne watershed_bem -s $subject --overwrite
done




