

sim_name=$1
it=$2
SIM_FILE=$CHASTE_TEST_OUTPUT/TCellABM/$1/sim_$2
VIS_FOLDER=visualisations/$1/sim_$2
echo $SIM_FILE

echo $sim_name sim_$it standard
python3 run-visualise.py $SIM_FILE
python3 ffmpeg-convert.py $VIS_FOLDER/standard
./trim-frames.sh $VIS_FOLDER/standard

#echo $sim_name sim_$it histogram
#python3 run-visualise-histogram.py $SIM_FILE
#python3 ffmpeg-convert.py $VIS_FOLDER/histogram
#./trim-frames.sh $VIS_FOLDER/histogram

#echo $sim_name sim_$it oxygen
#python3 run-visualise-chemokine.py $SIM_FILE oxygen
#python3 ffmpeg-convert.py $VIS_FOLDER/oxygen
#./trim-frames.sh $VIS_FOLDER/oxygen

#echo $sim_name sim_$it ccl5
#python3 run-visualise-chemokine.py $SIM_FILE ccl5
#python3 ffmpeg-convert.py $VIS_FOLDER/ccl5
#./trim-frames.sh $VIS_FOLDER/ccl5

#echo $sim_name sim_$it ifn-gamma
#python3 run-visualise-chemokine.py $SIM_FILE ifn-gamma
#python3 ffmpeg-convert.py $VIS_FOLDER/ifn-gamma
#./trim-frames.sh $VIS_FOLDER/ifn-gamma

#echo $sim_name sim_$it cxcl9
#python3 run-visualise-chemokine.py $SIM_FILE cxcl9
#python3 ffmpeg-convert.py $VIS_FOLDER/cxcl9
#./trim-frames.sh $VIS_FOLDER/cxcl9

#echo $sim_name sim_$it pcf
#python3 run-visualise-pcf.py $SIM_FILE
#python3 ffmpeg-convert.py $VIS_FOLDER/pcf
#./trim-frames.sh $VIS_FOLDER/pcf

#echo $sim_name sim_$it w_pcf
#python3 run-visualise-wpcf.py $SIM_FILE
#python3 ffmpeg-convert.py $VIS_FOLDER/w_pcf
#./trim-frames.sh $VIS_FOLDER/w_pcf

echo $sim_name sim_$it standard_tumour
python3 run-visualise-tumour.py $SIM_FILE
python3 ffmpeg-convert.py $VIS_FOLDER/standard_tumour
./trim-frames.sh $VIS_FOLDER/standard_tumour

