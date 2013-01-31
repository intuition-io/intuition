#!/bin/bash

clear
mode="debug"

#TODO check if $QTRADE exist and source it otherwize

echo "Running Backtest laboratory..."
cd $QTRADE

echo "Turning online backtester node..."
(nodejs $QTRADE/network/server.js) &
sleep 1

echo "Turning online shiny gui..."
if [ "$mode" == "debug" ]; then
    R -q -e "shiny::runApp(\"$QTRADE/network/shiny-backtest\")" &
    sleep 2
    echo "Opening web-brother to shiny server..."
    chromium-browser http://localhost:8100
elif [ "$mode" == "prod" ]; then
    (sudo $QTRADE/network/node_modules/.bin/shiny-server $QTRADE/network/shiny-server.config) &
    sleep 2
    echo "Opening web-brother to shiny server..."
    chromium-browser http://localhost:3838/users/xavier/shiny-backtest
else
    echo "Mode not implemented..."
    exit 1
fi
echo "Done..."
echo "Process has been crrectly ran."
ps -aux | grep server.js
ps -aux | grep shiny
