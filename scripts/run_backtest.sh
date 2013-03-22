#!/bin/bash

## Quick run of usual backtests
clear
echo "C'est parti..."

time $QTRADE/backtester/backtest.py --initialcash 10000 --tickers random,2 \
    --algorithm BuyAndHold --manager Constant --start 2005-01-10 --end 2010-07-03 \
    --database test --exchange paris

# Forex live test !
#time $QTRADE/backtester/backtest.py --initialcash 100000 --tickers EUR/USD,EUR/GBP,EUR/JPY \
    #--algorithm BuyAndHold --manager Constant --start 2013-03-20 --end 2013-04-22 \
    #--database test --exchange forex --frequency minute --live

# Equitie live test !
#time $QTRADE/backtester/backtest.py --initialcash 10000 --tickers random,2 \
    #--algorithm BuyAndHold --manager Constant --start 2013-03-20 --end 2013-04-22 \
    #--database test --exchange paris --frequency daily --live
