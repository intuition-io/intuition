#!/bin/bash

## Quick run of usual backtests
clear
echo "C'est parti..."

#$QTRADE/backtester/backtest.py -t google,apple -a BuyAndHold -m Constant -s 2012-02-06 -e 2012-02-10 -d 2min --exchange paris --live

time $QTRADE/backtester/backtest.py --initialcash 100000 --tickers random,2 \
    --algorithm BuyAndHold --manager Constant --start 2005-01-10 --end 2010-07-03 \
    --database test --exchange paris

# Forex live test !
#time $QTRADE/backtester/backtest.py --initialcash 100000 --tickers EUR/USD,EUR/GBP,EUR/JPY \
    #--algorithm BuyAndHold --manager Constant --start 2013-03-17 --end 2013-03-22 \
    #--database test --exchange forex --frequency minute --live
