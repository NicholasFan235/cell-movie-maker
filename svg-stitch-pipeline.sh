#!/bin/bash

sim_name=$1 # e.g. test-tcellabm-pdes
start_it=$2 # e.g. 0
stop_it=$2
if [ ! -z $3 ]; then
    stop_it=$3
fi

for ((i=$start_it; i<=$stop_it; i++)) do
    #python3 run-svg-stitch-tumour.py $CHASTE_TEST_OUTPUT/TCellABM/$sim_name/sim_$i;
    #python3 ffmpeg-convert.py visualisations/$sim_name/sim_$i/tumour-stitched
    
    python3 run-svg-stitch-tcell.py $CHASTE_TEST_OUTPUT/TCellABM/$sim_name/sim_$i;
    #python3 ffmpeg-convert.py visualisations/$sim_name/sim_$i/tcell-stitched
    #python3 ffmpeg-convert.py visualisations/$sim_name/sim_$i/tcell-cxcl9-stitched
    python3 ffmpeg-convert.py visualisations/$sim_name/sim_$i/tcell-exhaustion-stitched
    #python3 ffmpeg-convert.py visualisations/$sim_name/sim_$i/pcf-stitched
    #python3 ffmpeg-convert.py visualisations/$sim_name/sim_$i/graph-stats-stitched

    #python3 run-svg-stitch-tcell-stats.py $CHASTE_TEST_OUTPUT/TCellABM/$sim_name/sim_$i;
done
