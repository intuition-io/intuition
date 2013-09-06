QuanTrade: Automated quantitative trading system
==================================================

[![Build Status](https://travis-ci.org/Gusabi/ppQuanTrade.png?branch=master)](https://travis-ci.org/Gusabi/ppQuanTrade)

**Super Attention!** Since I am currently involved on other ambitious IT projects, I paused this one for a few months. However development should retake by the end of september, hopefully with new tools and skills!

**Attention!** Project is under early development, use for your own risk.

Overview
--------

**QuanTrade** is an engine and a set of tools meant to let you easily and intuitively build your own **automated quantitative trading system**.
It is designed to let financial, developer and scientist dudes (together sounds great) explore, test and deploy market technical hacks.

While the project is still at an early age, you can already write, or use, **signal detection algorithms, and portfolio allocation strategies**.
Then just plug it in the system and watch it from your dev-console or the web app run on **backtest** or **live** mode.

In addition the project proposes facilities to build a distributed system and 21st century application (big data, fat computations, d3.js and other html5 stuff),
tools to mix languages like Python, node.js and R and a financial library.
You will find some goodies like machine learning forecast, markowitz portfolio optimization, genetic optimization, sentiment analysis from twitter, ...


![Dashboard](https://raw.github.com/Gusabi/ppQuanTrade/master/QuantDashboard.png)


Features
--------

* Highly configurable trading backtest environment, powered by zipline
* Made to let you write easily algorithms, portfolio manager, parameters optimization and add data sources
* Already includes many
* R integration (and soon other languages) in your algorithms
* Complete results analyser
* Web front end for efficient results visualization
* Android notifications (for now with the help of freely available NotifyMyAndroid)
* Message architecture for interprocess communication and distributed computing, with a central remote console controling everything
* Ressources to learn about quantitative finance (cleaning it, coming soon)
* Neuronquant is also a financial library, with common used trading functions, graphics, ... used for example to solve Coursera econometrics assignments
* Easy to use data management, powered by mysql 
* Advanced computations available: neural networks, natural language processing, genetic optimization, checkout playground directory !
* Random fancy stuff as well in this directory


Installation
------------

You are just a few steps away from algoritmic trading. Follow one of those 3 methods:

- Plateform independant with Vagrant  and VMs/containers (http://www.vagrantup.com/):

```
$ git clone https://github.com/Gusabi/ppQuanTrade.git
$ sudo apt-get install lxc redir
$ sudo apt-get update && apt-get dist-upgrade
$ vagrant plugin install vagrant-lxc
$ cd ppQuanTrade && vagrant up --provider=lxc
```

Default is lxc because it is much more lightweight than plain VM and
performances are of importance for trading. Anyway, you can use an other
provider but edit eventually the Vagrantfile for fine
customization.  You can also change default base image by setting env variables ```BOX_NAME``` (and
optionnaly ```BOX_URI``` if you don't have it already on your system)

- Classic style:

```
$ git clone https://github.com/Gusabi/ppQuanTrade.git
$ cd ppQuanTrade && sudo make all
```

- Or one liner style (with more installation options, only the first one is required):

```
$ export PROJECT_URL=Gusabi/ppQuanTrade
$ export INSTALL_PATH=/some/where
$ export MAKE_TARGET=all
$ export VIRTUALIZE=false
$ export PROVIDER=lxc
```

And shoot:

```
$ wget -qO- https://raw.github.com/Gusabi/Dotfiles/master/utils/apt-git | sudo -E bash
```

- Then, in any case, you have to setup a mysql database:

Edit the script in scripts/installation/createdb.sql and your preferences in
~/.quantrade/config/default.json, the symbols you want to trade in
ppQuanTrade/data/symbols.csv and run:

```
$ sudo chown -R $USER $HOME/.quantrade   # Fixes weird issue
$ sudo chown -R $USER ppQuanTrade/       # Idem 
$ make database
```

At any moment you can change or edit symbols files and run it again for update.

- QuanTrade is able to send to your android device(s) notifications, using
  NotifyMyAndroid. However you will need an API key, available for free with
  the trial version of the application. Super simple to setup, check their
  website.

- You're done !


Getting started
---------------

You can configure the soft trough default.json and plugins.json in
~/.quantrade. Then run:

```
./application/app.py --initialcash 50000 --tickers random,10 \
        --loglevel CRITICAL --algorithm BuyAndHold --manager Constant --start 2011-05-10 \
        --frequency daily --database backtest --exchange paris --source DBPriceSource
```

Or in realtime mode (Broken, I am improving it):

```./application/app.py --initialcash 100000 --tickers EUR/USD,EUR/GBP --algorithm StdBased 
		--manager Equity --frequency minute --exchange forex --live --source EquitiesLiveSource ```

More examples available in scripts/run_app.sh

As mentionned you can easily write your own algorithms. Here is the equity
manager example, which allocates the same weight to all of your assets:

```python
from portfolio import PortfolioManager

class Fair(PortfolioManager):
    '''
    dispatch equals weigths
    '''
    def optimize(self, date, to_buy, to_sell, parameters):
        allocations = dict()
        if to_buy:
            fraction = round(1.0 / float(len(to_buy)), 2)
            for s in to_buy:
                allocations[s] = fraction
        for s in to_sell:
            allocations[s] = - self.portfolio.positions[s].amount

        expected_return = 0
        expected_risk = 1
        return allocations, expected_return, expected_risk
```

Strategies triggering buy or sell signals are used within zipline backtester
engine and therefore use quite the same scheme, plus the manager, and some
config parameters. Here is a classic momentum strategie:

```python
from neuronquant.zipline.algorithm import QuantitativeTrading

class BuyAndHold(QuantitativeTrading):
    '''Simpliest algorithm ever, just buy a stock at the first frame'''
    def initialize(self, properties):
        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)

        self.loops = 0

    def handle_data(self, data):
        self.loops += 1
        signals = {}
        ''' ----------------------------------------------------------    Init   --'''
        if self.initialized:
            self.manager.update(
                self.portfolio,
                self.datetime,
                self.perf_tracker.cumulative_risk_metrics.to_dict(),
                save=self.save)
        else:
            # Perf_tracker need at least a turn to have an index
            self.initialized = True

        if self.loops == 2:
            ''' ------------------------------------------------------    Scan   --'''
            for ticker in data:
                signals[ticker] = data[ticker].price

        ''' ----------------------------------------------------------   Orders  --'''
        if signals:
            orderBook = self.manager.trade_signals_handler(signals)
            for stock in orderBook:
                if self.debug:
                    self.logger.notice('{}: Ordering {} {} stocks'.format(
                        self.datetime, stock, orderBook[stock]))
                self.order(stock, orderBook[stock])
```


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
