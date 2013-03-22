#!/bin/sh

if [ $# != 2 ]; then
    echo "Usage: ./convert.sh <currency1> <currency2>"
    echo "Example: ./convert.sh USD EUR"
    exit
fi

curl -s http://www.google.com/finance/converter\?a\=1\&from\=$1\&to\=$2 |  sed '/res/!d;s/<[^>]*>//g'
