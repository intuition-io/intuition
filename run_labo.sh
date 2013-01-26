#!/bin/sh

echo "Running Backtest laboratory..."
cd $QTRADE

echo "Turning online backtester node..."
nodejs $QTRADE/network/server.js &
sleep(1)

echo "Turning online shiny gui..."
(sudo $QTRADE/network/node_modules/.bin/shiny-server $QTRADE/network/shiny-server.config) &
sleep(2)

echo "Opening web-brother to shiny server..."
chromium-browser http://localhost:3838/users/xavier/shiny-backtest

read
