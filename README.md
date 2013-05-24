QuanTrade: Automated quantitative trading system
==================================================

**Attention!** Project is under early development, use for your own risk.

Overview
--------

**QuanTrade** is a set of tools and an engine meant to let you easily and intuitively build your own **automated quantitative trading system**.
It is designed to let financial, developer and scientist dudes (together sounds great) explore, test and deploy market technical hacks.

While the project is still at an early age, you can already write, or use, **signal detection algorithms, and portfolio allocation strategies**.
Then just plug it in the system and watch it from your dev-console or the web app run on **backtest** or **live** mode.

In addition the project proposes facilities to build a distributed system and 21st century application (big data, fat computations, d3.js and other html5 stuff),
tools to mix languages like Python, node.js and R and a financial library.
You will find some goodies like machine learning forecast, markowitz portfolio optimization, genetic optimization, sentiment analysis from twitter, ...


![Dashboard](https://raw.github.com/Gusabi/ppQuanTrade/master/management/QuantDashboard.png)


Features
--------

* Highly configurable trading backtest environment, powered by zipline project
* Made to let you write easily algorithms, portfolio manager, parameters optimization and add data sources
* Already includes many
* R integration (and soon other languages) in your algorithms
* Complete results analyser
* Web front end for efficient results visualization
* Android notifications (for now with the help of freely available NotifyMyAndroid)
* Message architecture for interprocess communication and distributed computing, with a central remote console controling everything
* Ressources to learn about quantitative finance (cleaning it, coming soon)
* Neuronquant is also a financial library, with common used trading functions, graphics, ... used for example to solve Coursera econometrics assignments
* MySQL and SQLite data management for optimized financial storage and access 
* Advanced computations available: neural networks, natural language processing, genetic optimization, checkout playground directorie !
* Random fancy stuff as well in this directory


Installation
------------

- Zipline backtster engine: 
   - Clone (outside QuanTrade project) or fork (then clone your own copy) the original project at https://github.com/quantopian/zipline
   - To stay up-to-date: add streams to the original project and to my fork:
      - ```./zipline $> git remote add quantopian https://github.com/quantopian/zipline.git ```
      - ```./zipline $> git remote add neuronquant https://github.com/Gusabi/zipline.git ```
      - ```./zipline $> git fetch quantopian && git merge quantopian/master ```
      - ```./zipline $> git fetch neuronquant && git merge neuronquant/master ```
      - note: I keep my version updated with the original, so you usually won't need to fetch both

- Run now the installation script (or check in the wiki how to do it manually):
``` ./ppQuanTrade #> ./scripts/installation/install.sh```

- Edit ~/.quantrade/local.sh to suit your environment

- Database:
   - Make sure you have a well configured mysql database running (check data/readme.rst or http://dev.mysql.com/tech-resources/articles/mysql_intro.html)
   - ``` $> mysql -u root -p ```
   - ```mysql> create database stock_data;```
   - ```mysql> set password for 'user'@'host' = password('chut');
   - ```mysql> grant all privileges on stock_data.* to 'user'@'host'``` (replace user and host as you want)
   - Edit ./ppQuanTrade/config/mysql.cfg 
   - Create tables with ```./ppQuanTrade $>`./scripts/database.py -c```
   - Fill it with ``` ./ppQuanTrade $> ./scripts/database.py -a data/dump_sql.csv ```

- NeuronQuant is able to send to your android device(s) notifications, using NotifyMyAndroid. However you will need an API key,
available for free with the trial version of the application. Super simple to setup, check their website and then edit ~/.quantrade/local.sh

- Congrats you're Done !


Getting started
---------------

To run a backtest manually, configure ppQuanTrade/config/algorithms.json and ppQuanTrade/config/managers.json file, and then run

```./backtest.py --initial cash --tickers random,6 --algorithm DualMA \
	 	--manager OptimalFrontier --exchange paris --start 2005-01-10 --end 2010-07-03```

Or in realtime mode:

```./backtest.py --initialcash 100000 --tickers EUR/USD,EUR/GBP --algorithm StdBased \
		--manager Equity --frequency minute --exchange forex --live```

More examples available [root]/scripts/run_backtest.sh

As mentionned you can easily write your own algorithms. Here is the equity manager example, which allocates the same weight
to all of your assets:

```python
from neuronquant.ai.portfolio import PortfolioManager

class Equity(PortfolioManager):
    """"
    dispatch equal weigths
    """
    def optimize(self, date, to_buy, to_sell, parameters):
        # allocations will store stocks weigths, used to process orders later
        # negative amounts will be sold, positive will be bought
        allocations = dict()

        # Split stocks to buy in equal weigths
        if to_buy:
            fraction = round(1.0 / float(len(to_buy)), 2)
            for s in to_buy:
                allocations[s] = fraction

        # Simply sell current hold amount per stock
        for s in to_sell:
            allocations[s] = - self.portfolio.positions[s].amount

        expected_return = 0
        expected_risk = 1
        return allocations, expected_return, expected_risk
```

Strategies triggering buy or sell signals are used within the great zipline backtester engine and therefore use quite the same scheme,
plus the manager, and some config parameters. Here is a classic momentum strategie:

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
        ''' __________________________________________________________    Init   __'''
        # Update the portfolio manager with current simulation universe
        self.manager.update(self.portfolio, self.datetime.to_pydatetime())
        signals = dict()
        notional = 0

        ''' __________________________________________________________    Scan   __'''
        # Check every stock in the specified universe and apply the algorithm on it
        for ticker in data:
            sma          = data[ticker].mavg.price
            price        = data[ticker].price
            cash         = self.portfolio.cash
            notional     = self.portfolio.positions[ticker].amount * price
            capital_used = self.portfolio.capital_used

            # Check for sell signal
            if sma > price and notional > -0.2 * (capital_used * cash):
                signals[ticker] = - price

            # Check for buy signal
            elif sma < price and notional < 0.2 * (capital_used * cash):
                signals[ticker] = price

        ''' __________________________________________________________   Orders  __'''
        # If signals detected, re-compute portfolio allocation and process orders
        if signals:
            order_book = self.manager.trade_signals_handler(signals)

            for ticker in order_book:
                self.order(ticker, order_book[ticker])
                if self.debug:
                    self.logger.info('{}: Ordering {} {} stocks'.format(self.datetime, ticker, order_book[ticker]))
                    self.logger.info('{}:  {} / {}'.format(self.datetime, sma, price))
```

Rememeber that managers and algorithms should be configured in their own \*.json files or through the webapp.

You can setup your trading environment by running from the root directory::
    ./scripts/run_labo.py
and access to the shiny frontend page. From there configure the backtest, run it and explore detailed results.

Checkout the wiki for more details about web labo front end, remote console use, algorithm optimization,
neural network forecasting, ...


Resources for Newcomers
-----------------------

* [The Wiki](https://github.com/Gusabi/ppQuanTrade/wiki)
* [Contributing](https://github.com/Gusabi/ppQuanTrade/wiki/Contribution)
* [Tutorial](https://github.com/Gusabi/ppQuanTrade/wiki/How-to-become-a-ninja-trader)


Credits
-------

Projects and websites below are awesome works that i heavily use, learn from and want to gratefully thank:

* [Zipline](http://github.com/quantopian/zipline and quantopian http://wwww.quantopian.com)
* [Quantopian](http://www.quantopian.com/)
* [Pandas](http://github.com/pydata/pandas)
* [R-bloggers](http://www.r-bloggers.com/)
* [QSTK](https://github.com/tucker777/QSTK)
* [Coursera](http://www.coursera.org/)
* [Udacity](http://www.udacity.com/)
* [Babypips](http://www.babypips.com/)
* [GLMF](http://www.unixgarden.com/)
