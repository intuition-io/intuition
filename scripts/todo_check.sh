#!/bin/bash

set -u
clear
cd $QTRADE

if [ $# != 1 ]; then
    echo "Usage: ./todo_check 'pattern to match'"
    exit
fi

echo "QuanTrade $1 list..."

count=0
#FIXME how ugly...
for file in $(find . -type f | grep -v "res" | grep -v "git" | grep -v "doc" | grep -v "management" | grep -v "^data"); do 
    #echo $file
    TODOS=$(cat $file | grep -i $1)
    if [ ! -z "${TODOS}" ]; then
        count=$((count + 1))
        echo
        echo "_________________________________________________    $file    __________"
        echo "$TODOS" | sed -e 's/^ *//g' -e 's/ *$//g'
    fi
done

zenity --info --text "$1 list: $count tasks, have fun !"
