#!/bin/bash

## Quick run of usual backtests

#$QTRADE/backtester/backtest.py -t google,apple -a BuyAndHold -m Constant -s 2012-02-06 -e 2012-02-10 -d 2min --exchange paris --live

$QTRADE/backtester/backtest.py -i 100000 -t random,2 -a BuyAndHold -m Constant -s 2005-01-10 -e 2010-07-03 --database test --exchange paris
