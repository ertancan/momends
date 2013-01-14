#!/bin/bash
frame=$1
x=$2
y=$3
input=$4
output=$5
convert -size `identify -format %wx%h $frame` xc:none $output
convert $output $input -geometry $x$y -composite $output
convert $output $frame -composite $output
