#!/bin/bash

## Quick run of usual backtests
clear
echo "C'est parti..."

# Equitie backtest 
#time $QTRADE/backtester/backtest.py --initialcash 10000 --tickers random,2 \
    #--algorithm BuyAndHold --manager Constant --start 2005-01-10 --end 2010-07-03 \
    #--frequency minute --database test --exchange paris

# Forex live test !
#time $QTRADE/backtester/backtest.py --initialcash 10000 --tickers EUR/USD,EUR/GBP,EUR/JPY \
    #--algorithm BuyAndHold --manager Constant --end 13h00 \
    #--database test --exchange forex --frequency minute --live

# Equitie live test !
time $QTRADE/backtester/backtest.py --initialcash 10000 --tickers random,2 \
    --algorithm BuyAndHold --manager Constant --end 18h59 \
    --database test --exchange nasdaq --frequency minute --live
