#python backtest.py -t goog,aapl -a StdBased -m Equity -s 2012-02-04 -e 2012-02-06 -d D --interactive --realtime
#python backtest.py -t random,1 -a StdBased -m Equity -s 2005-01-10 -e 2010-07-03 --interactive
#python backtest.py -t apple,starbucks -a DualMA -m OptimalFrontier -s 2005-01-10 -e 2010-07-03 -i
#python backtest.py -t random,6 -a DualMA -m OptimalFrontier -s 2005-01-10 -e 2010-07-03 --interactive

python backtest.py -t random,1 -a Momentum -m Constant -s 2005-01-10 -e 2010-07-03 --interactive
