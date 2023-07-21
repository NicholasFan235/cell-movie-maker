#!/bin/bash

sim_name=$1 # e.g. test-tcellabm-pdes
sim_it=$2 # e.g. 0

python3 run-visualise-svgs.py $CHASTE_TEST_OUTPUT/TCellABM/$sim_name/sim_$sim_it;
./svg-to-mp4.sh visualisations/$sim_name/sim_$sim_it

