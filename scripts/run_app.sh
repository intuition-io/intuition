#!/bin/bash

## Quick run of usual backtests
clear
echo "C'est parti..."

# Equitie backtest 
time $QTRADE/application/app.py --initialcash 100000 --tickers random,4 \
    --algorithm BuyAndHold --manager Constant --start 2006-01-10 --end 2008-07-03 \
    --frequency daily --database test --exchange paris

# Forex live test !
#time $QTRADE/backtester/backtest.py --initialcash 10000 --tickers EUR/USD,EUR/GBP,EUR/JPY \
    #--algorithm BuyAndHold --manager Constant --end 21h20 \
    #--database test --exchange forex --frequency minute --live

# Equitie live test !
#time $QTRADE/backtester/backtest.py --initialcash 10000 --tickers random,3 \
    #--algorithm BuyAndHold --manager OptimalFrontier --end 14h30 \
    #--database test --exchange paris --frequency minute --live
