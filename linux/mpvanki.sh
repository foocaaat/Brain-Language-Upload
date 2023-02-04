#!/bin/bash

time_in_seconds(){
     input="$1"
     a=$(echo $input | awk -F. '{print $1}')
a="$(echo $a | sed 's/^0*//')"
     b=$(echo $input | awk -F. '{print $2}')
b="$(echo $b | sed 's/^0*//')"
     c=$(echo $input | awk -F. '{print $3}')
c="$(echo $c | sed 's/^0*//')"
     d=$(echo $input | awk -F. '{print $4}')
d="$(echo $d | sed 's/^0*//')"
    echo $(($((a*3600)) + $((b*60+c))))\.$d
}

file=".cache/mpvanki"
file2=".cache/$1mpvanki"

var1=$(awk '{print $1}' $file)
var2=$(awk '{print $2}' $file)
var3=$(awk '{print $3}' $file)
var4=$(awk '{print $4}' $file)
START=$(time_in_seconds $2)
END=$(time_in_seconds $3)


# Convert the time format from minutes.seconds.miliseconds to seconds

START=$(time_in_seconds $2)
END=$(time_in_seconds $3)
number="$(echo $4 | sed 's/^0*//')"

var5=$(awk '{print $1}' $file2)

socee="socat - /tmp/mpv-socket"

if [ "1" == "$6" ];then
echo '{"command": ["set_property", "sub-visibility", true]}' | $socee 
else
echo '{"command": ["set_property", "sub-visibility", false]}' | $socee 
fi
if [ "$(echo '{ "command": ["get_property", "path"] }' | $socee | jq '.data' | tr -d '"')" != "$HOME/.local/share/AnkiVideo/$1" ]; then
echo '{ "command": ["loadfile", "'$HOME/.local/share/AnkiVideo/$1'"] }' | $socee
while true; do
    stream=$(echo '{ "command": ["get_property", "stream-pos"] }' | $socee | jq '.data' | tr -d '"')
    if [ "$stream" -gt 0 ]; then
        break
    fi
done
fi

if [ "$var1" == "$1" ] && [ $var4 == $(( number - 1 )) ] && [ $(echo "$var3 < $START"|bc -l) -eq 1 ]; then
    echo e
else
    if [ "$5" == "yes" ] && [ $(echo "$number == 1"|bc -l) -eq 1 ] && [ $(echo "$var4 != 1"|bc -l) -eq 1 ] ; then
        echo '{ "command": ["seek", '0', "absolute"] }' | $socee
    else
        if [ "$5" == "yes" ] && [ $(echo "$var5 < $START"|bc -l) -eq 1 ]; then
            echo '{ "command": ["seek", '$var5', "absolute"] }' | $socee
        else
            echo '{ "command": ["seek", '$START', "absolute"] }' | $socee
        fi
    fi
fi
echo '{ "command": ["set_property", "pause", false] }' | $socee


echo $1 $START $END $number > $file
if [ "$5" == "yes" ]; then
echo $END > $file2
fi


while true; do
    position=$(echo '{ "command": ["get_property", "time-pos"] }' | $socee | jq '.data' | tr -d '"')
    if (( $(echo "$position >= $END" | bc -l) )); then
        echo '{ "command": ["set_property", "pause", true] }' | $socee
        break
    fi
    sleep 0.05 # so the cpu don't die
done
