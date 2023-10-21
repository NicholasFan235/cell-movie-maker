#!/bin/bash

# set verbose level to info
__LOG_LEVEL=5
#FFMPEG_LOG_LEVEL=info
FFMPEG_LOG_LEVEL=warning
MAX_PROC=16

set -eo pipefail

declare -A LOG_LEVELS
# https://en.wikipedia.org/wiki/Syslog#Severity_level
LOG_LEVELS=([0]="emerg" [1]="alert" [2]="crit" [3]="err" [4]="warning" [5]="notice" [6]="info" [7]="debug")
LOG_COLOURS=([0]='\033[1;33m' [1]='\033[0:33m' [2]='\033[1;31m' [3]='\033[0;31m' [4]='\033[0;34m' [5]='\033[0;32m' [6]='\033[1;37m' [7]='\033[0;37m')
function .log () {
  local LEVEL=${1}
  shift
  if [ ${__LOG_LEVEL} -ge ${LEVEL} ]; then
    echo -e ${LOG_COLOURS[$LEVEL]} "[${LOG_LEVELS[$LEVEL]}]" "$@" '\033[0m'
  fi
}

VIS_FOLDER=$1

vis_types="tcell-svg tumour-svg hypoxia-svg pressure-svg oxygen-svg ccl5-svg density-svg macrophage-svg"
fps=30
if [ -z $2 ]; then fps=$2; fi

cd $VIS_FOLDER
for vis_type in $vis_types; do
    if [ ! -d $vis_type ]; then
        .log 4 "$vis_type does not exist"
        continue
    fi
    cd $vis_type

    .log 5 "Png convert $VIS_FOLDER/$vis_type"
    if [ ! -d ../$vis_type-png ]; then
        mkdir ../$vis_type-png
    else
        rm -f ../$vis_type-png/frame_*.png
    fi
    wait
    i=0
    for frame_num in $(ls $svg_folder | grep -oP "(?<=frame_)\d+(?=\.svg)" | sort -n); do
        .log 6 "    $vis_type/frame_$frame_num.svg to png"
        if [ $i -eq 0 ]; then
            wait
        fi
        i=$(($i+1))
        i=$(($i%MAX_PROC))
        cairosvg --output-width 512 --output-height 512 \
            frame_$frame_num.svg -o ../$vis_type-png/frame_$frame_num.png &
    done
    wait
    cd ..

    .log 5 "png to mp4 $VIS_FOLDER $vis_type"
    ffmpeg -y -framerate $fps -i $vis_type-png/frame_%d.png \
        -start_number 0 -c:v libx264 -r $fps -pix_fmt yuv420p \
        -loglevel $FFMPEG_LOG_LEVEL \
        $vis_type.mp4
    
    #rm -r $vis_type-png
done

