


SIM_FILE=$CHASTE_TEST_OUTPUT/TCellABM/$1/sim_$2
echo $SIM_FILE

#python3 run-visualise.py $SIM_FILE
#python3 run-visualise-histogram.py $SIM_FILE
#python3 run-visualise-chemokine.py $SIM_FILE oxygen
#python3 run-visualise-chemokine.py $SIM_FILE ccl5
#python3 run-visualise-chemokine.py $SIM_FILE ifn-gamma
#python3 run-visualise-chemokine.py $SIM_FILE cxcl9
#python3 run-visualise-pcf.py $SIM_FILE
python3 run-visualise-wpcf.py $SIM_FILE

VIS_FOLDER=visualisations/$1/sim_$2
#python3 ffmpeg-convert.py $VIS_FOLDER/standard
#python3 ffmpeg-convert.py $VIS_FOLDER/histogram
#python3 ffmpeg-convert.py $VIS_FOLDER/oxygen
#python3 ffmpeg-convert.py $VIS_FOLDER/ccl5
#python3 ffmpeg-convert.py $VIS_FOLDER/ifn-gamma
#python3 ffmpeg-convert.py $VIS_FOLDER/cxcl9
#python3 ffmpeg-convert.py $VIS_FOLDER/pcf
python3 ffmpeg-convert.py $VIS_FOLDER/w_pcf
