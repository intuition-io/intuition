#!/bin/bash

## Quick run of usual backtests

#./backtest.py -t google,apple -a BuyAndHold -m Constant -s 2012-02-06 -e 2012-02-10 -d 2min --live

#./backtest.py -t random,1 -a StdBased -m Equity -s 2005-01-10 -e 2010-07-03
#./backtest.py -t apple,starbucks -a DualMA -m OptimalFrontier -s 2005-01-10 -e 2010-07-03 
#./backtest.py -t random,6 -a DualMA -m OptimalFrontier -s 2005-01-10 -e 2010-07-03 

./backtest.py -t random,3 -a BuyAndHold -m Constant -s 2005-01-10 -e 2010-07-03 --remote
