#!/bin/bash
cd WebManager/static/
frame=$1
x=$2
y=$3
input=$4
output=$5
size=`identify -format %wx%h $frame`
convert -size $size xc:none $output
resize=$input.res
convert $input -resize $size^ $resize
convert $output $resize -geometry $x$y -composite $output
convert $output $frame -composite $output
rm $resize
