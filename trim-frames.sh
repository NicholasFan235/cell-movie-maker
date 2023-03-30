
VIS_FOLDER=$1

frames=$(ls $VIS_FOLDER | grep -oP "(?<=frame_)\d+(?=\.png)" | sort -n)

for frame in $frames
do
    file=$VIS_FOLDER/frame_$frame.png
    if [ $(($frame % 100)) != 0 ]
    then
        rm $file
    fi
done
