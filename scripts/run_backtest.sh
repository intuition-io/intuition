#!/bin/bash

## Quick run of usual backtests

#$QTRADE/backtester/backtest.py -t google,apple -a BuyAndHold -m Constant -s 2012-02-06 -e 2012-02-10 -d 2min --exchange paris --live

$QTRADE/backtester/backtest.py -i 50000 -t random,40 -a DualMA -m Constant -s 2005-01-10 -e 2010-07-03 --database test --exchange nasdaq
