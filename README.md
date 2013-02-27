NeuronQuant: Automated quantitative trading system
==================================================

Overview
--------

**NeuronQuant** is a set of tools and an engine meant to let you easily and intuitively build your own **automated quantitative trading system**.
It is designed to let financial, developer and scientist dudes (together sounds great) explore, test and deploy market technical hacks.

While the project is still at an early age, you can already write, or use, **buy/sell signal algorithms, and portfolio allocation strategies**.
Then just plug it in the system and watch it from your dev-console or the web app run on **backtest** or **live-trading** mode.

In addition the project propose facilities to build a distributed system and 21st century application (big data, fat computations, d3.js and other html5 stuff),
tools to mix languages like Python, node.js and R and a financial library.
You will find some goodies like machine learning forecast, markowitz portfolio optimization, genetic optimization, sentiment analysis from twitter, ...


Installation
------------
    - Clone this repos
    - Clone my zipline fork, or the original and apply changes in management/changelog
    - Edit config.sh to suit your machine
    - Run a mysql database and edit neuronquant/data/config.py 
    - Create the tables with neuronquant/data/database.py create, then populate it with neuronquant/data/database.py add symbols.csv (see database/QSDATA for a huge list)
    - You should be ready to use, see below 


Getting started
---------------

To run a backtest manually, configure algos.cfg and manager.cfg file, and then run

```./backtest.py --tickers google,apple --algorithm DualMA --manager OptimalFrontier --start 2005-01-10 --end 2010-07-03```

Or in realtime mode:

```./backtest.py --tickers random,6 --algorithm StdBased --manager Equity --delta 2min --live```

More examples available in bactester/runBacktest.sh

As mentionned you can easily write your own algorithms. Here is the equity manager example, which allocates the same weight
to all of your assets:

```python
from neuronquant.ai.portfolio import PortfolioManager

class Equity(PortfolioManager):
    """"
    dispatch equal weigths
    """
    def optimize(self, date, to_buy, to_sell, parameters):
        allocations = dict()
        if to_buy:
            fraction = round(1.0 / float(len(to_buy)), 2)
            for s in to_buy:
                allocations[s] = fraction
        for s in to_sell:
            allocations[s] = - self.portfolio.positions[s].amount
        return allocations, 0, 1
```

Strategies triggering buy or sell signals are used with great zipline backtester engine and therefore use quite the same scheme,
plus the manager, and some config parameters. Here a classic momentum strategie:

```python
class Momentum(TradingAlgorithm):
    '''
    https://www.quantopian.com/posts/this-is-amazing
    '''
    def initialize(self, properties):
        self.max_notional = 100000.1
        self.min_notional = -100000.0

        self.add_transform(MovingAverage, 'mavg', ['price'], window_length=properties.get('window_length', 3))

    def handle_data(self, data):
        ''' ----------------------------------------------------------    Init   --'''
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())
        signals = dict()
        notional = 0

        ''' ----------------------------------------------------------    Scan   --'''
        for ticker in data:
            sma          = data[ticker].mavg.price
            price        = data[ticker].price
            cash         = self.portfolio.cash
            notional     = self.portfolio.positions[ticker].amount * price
            capital_used = self.portfolio.capital_used

            # notional stuff are portfolio strategies, implement a new one, combinaison => parameters !
            if sma > price and notional > -0.2 * (capital_used + cash):
                signals[ticker] = - price
            elif sma < price and notional < 0.2 * (capital_used + cash):
                signals[ticker] = price

        ''' ----------------------------------------------------------   Orders  --'''
        if signals:
            order_book = self.manager.trade_signals_handler(signals)
            for ticker in order_book:
                self.order(ticker, order_book[ticker])
                if self.debug:
                    self.logger.info('{}: Ordering {} {} stocks'.format(self.datetime, ticker, order_book[ticker]))
                    self.logger.info('{}:  {} / {}'.format(self.datetime, sma, price))
```

Rememeber that managers and algorithms should be configured in their own \*.cfg files or through the webapp.

You can setup your trading environment by running from the root directory::
    ./run_labo.py
and access to the shiny frontend page. From there configure the backtest, run it and explore detailed results.


Credits
-------

Projects and websites below are awesome works that i heavily use, learn from and want to gratefully thank:

* pandas http://github.com/pydata/pandas

* r-bloggers http://www.r-bloggers.com/

* zipline http://github.com/quantopian/zipline and quantopian http://wwww.quantopian.com

* QSTK https://github.com/tucker777/QSTK

* coursera http://www.coursera.org/

* udeacity http://www.udacity.com/

* Babypips http://www.babypips.com/

* GLMF http://www.unixgarden.com/
