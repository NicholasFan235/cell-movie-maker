#!/bin/bash

sim_name=$1 # e.g. test-tcellabm-pdes
start_it=$2 # e.g. 0
stop_it=$2
if [ ! -z $3 ]; then
    stop_it=$3
fi

for ((i=$start_it; i<=$stop_it; i++)) do
    python3 run-preprocess.py $CHASTE_TEST_OUTPUT/TCellABM/$sim_name/sim_$i;
done
