#!/bin/bash
#
# Copyright 2012 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script search for the given pattern in files recursively

set -u
clear

if [ $# -lt 1 ]; then
    echo "Usage: ./todo_check 'pattern to match'"
    exit
elif [ $# == 2 ]; then
    echo "Location provided, going there..."
    cd $2
fi

echo "QuanTrade $1 list..."

count=0
#NOTE how ugly...
for file in $(find . -type f | grep -v "res" | grep -v "git" | grep -v "doc" | grep -v "management" | grep -v "^./data" | grep -v "deprecated"); do 
    #echo $file
    TODOS=$(cat $file | grep -i $1)
    if [ ! -z "${TODOS}" ]; then
        count=$((count + 1))
        echo
        echo "___________________________________________________________________    $file"
        echo "$TODOS" | sed -e 's/^ *//g' -e 's/ *$//g'
    fi
done

zenity --info --text "$1 list: $count tasks, have fun !"
