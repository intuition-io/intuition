#!/bin/sh

if [ $# > 1 ]; then
    echo "Testing function $1 from module DataAgent..."
    python -m unittest -c -f test_data.test_DataAgent.test_$1
else 
    echo "Usage ./fctTest.sh fct"
fi
