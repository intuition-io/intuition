Intuition
=========

> Automated quantitative trading system


![Dashboard](https://raw.github.com/hivetech/hivetech.github.io/master/images/QuantDashboard.png)

Overview
--------

**Intuition** is an engine and a set of tools meant to let you easily and
intuitively build your own **automated quantitative trading system**.  It is
designed to let financial, developer and scientist dudes (together sounds
great) explore, test and deploy market technical hacks.

While the project is still at an early age, you can already write, or use,
**signal detection algorithms, and portfolio allocation strategies**. Then
just plug them in the system and watch it from your dev-console or the web app
run on **backtest** or **live** mode.

In addition I work on facilities to build a distributed system and
21st century application (big data, fat computations, d3.js and other html5
stuff), tools to mix languages like Python, node.js and R and a financial
library. You will find some goodies like machine learning forecast, markowitz
portfolio optimization, genetic optimization, sentiment analysis from twitter, ...


Features
--------

* Highly configurable trading backtest environment, powered by zipline
* Made to let you write easily algorithms, portfolio manager, parameters optimization and add data sources
* Already includes many
* Experimental live trading on different markets (Nyse, Nasdaq, CAC40 and Forex for now)
* R integration (and soon other languages) in your algorithms
* Complete results analyser
* Web front end for efficient results visualization
* Android notifications (for now with the help of freely available NotifyMyAndroid)
* Message architecture for interprocess communication and distributed computing
* Ressources to learn about quantitative finance (cleaning it, coming soon)
* Neuronquant is also a financial library, with common used trading functions, graphics, ... used for example to solve Coursera econometrics assignments
* Easy to use data management, powered by mysql and rethinkdb
* Advanced computations available: neural networks, natural language processing, genetic optimization, checkout playground directory !


Status
------

[![License](https://pypip.in/license/intuition/badge.png)](https://pypi.python.org/pypi/intuition/)
[![Build Status](https://travis-ci.org/hackliff/intuition.png?branch=develop)](https://travis-ci.org/hackliff/intuition)
[![Code Health](https://landscape.io/github/hackliff/intuition/develop/landscape.png)](https://landscape.io/github/hackliff/intuition/develop)

Branch   | Version
-------- | -----
Master   | 0.0.9
Develop  | 0.2.9
Pypi     | [![Latest Version](https://pypip.in/v/intuition/badge.png)](https://pypi.python.org/pypi/intuition/)

**Attention** Project is in an *early alpha*, and under heavy development.
 The new version (december 2013) revises a lot of code :

* Algoithms, managers and data sources have their [own repository](https://github.com/hackliff/intuition-modules)
* More powerful API to build custom versions of them
* The context module now handles configuration
* [Shiny]() interface, [Dashboard]() and clustering will have their intuition-plugins repository (soon)
* ZeroMQ messaging is for now removed but might be back for inter-algo communication
* Neither MySQL, that has been removed and will be re-implemented as a [data plugin](https://github.com/hackliff/intuition-modules/tree/develop/plugins)
* But currently it has been replaced by [Rethinkdb](rethinkdb.com)
* Installation is much simpler and a docker image is available for development and deployment
* More intuitive configuration splitted between the context mentioned, command line argument and environment variables
* And a lot of house keeping and code desgin stuff


Installation
------------

You are just a few steps away from algoritmic trading. Choose one of the
following installation method

* The usual way

```console
$ pip install intuition
```

* The full installation (i.e. with buit-in [modules](https://github.com/hackliff/intuition-modules))

```console
$ export FULL_INTUITION=1
$ wget -qO- https://raw.github.com/hackliff/intuition/develop/scripts/installation/bootstrap.sh | sudo -E bash
```

* From source

```console
$ git clone --recursive https://github.com/hackliff/intuition.git
$ cd intuition && sudo make
```

* Sexy, cutting edge style

```console
$ docker pull hivetech/intuition
```

Getting started
---------------

Concept : A data source generates events processed by the algorithm that can
optionnaly use a portfolio manager to compute assets allocation.

You can configure the algorithm and the portfolio manager in
~/.intuition/plugins.json. Third party services use environment variable, take
a look in config/local.env.

```console
$ docker run \
  -e PUSHBULLET_API_KEY=$PUSHBULLET_API_KEY \
  -e QUANDL_API_KEY=$QUANDL_API_KEY \
  -e MAILGUN_API_KEY=$MAILGUN_API_KEY \
  -e TRUEFX_API=$TRUEFX_API \
  -e DB_HOST=$DB_HOST \
  -e DB_PORT=$DB_PORT \
  -e DB_NAME=$DB_NAME \
  -e LANGUAGE="fr_FR.UTF-8" \
  -e LANG="fr_FR.UTF-8" \
  -e LC_ALL="fr_FR.UTF-8" \
  -name trade_box hivetech/intuition \
  intuition --context mongodb::192.168.0.12:27017/backtestNasdaq --showlog
```

For Hackers
-----------

As mentionned you can easily write your own strategies, head out to :

* [Algorithm API](https://github.com/hackliff/intuition-modules/blob/develop/algorithms/readme.md)
* [Portfolio API](https://github.com/hackliff/intuition-modules/blob/develop/managers/readme.md)
* [Data API](https://github.com/hackliff/intuition-modules/blob/develop/sources/readme.md)
* [Context API](https://github.com/hackliff/intuition-modules/blob/develop/contexts/readme.md)

Here is the Fair manager example, which allocates the same weight to all of your assets:

```python
from intuition.zipline.portfolio import PortfolioFactory

class Fair(PortfolioFactory):
    '''
    Dispatch equals weigths for buy signals and give up everything on sell ones
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

Here is a classic buy and hold strategy, with a plugin which stores metrics in
[rethinkdb](www.rethinkdb.com):

```python
from intuition.zipline.algorithm import TradingFactory
import intuition.modules.plugins.database as database

class BuyAndHold(TradingFactory):
    '''
    Simpliest algorithm ever, just buy every stocks at the first frame
    '''
    def initialize(self, properties):
        self.debug = properties.get('debug', False)
        self.save = properties.get('save', False)

    def warming(self, data):
        if self.save:
            self.db = database.RethinkdbBackend(self.manager.name, True)

    def event(self, data):
        signals = {}
        ''' ---------------------------------------------------    Init   --'''

        if self.day == 2:

            if self.save:
                self.db.save_portfolio(self.datetime, self.portfolio)
                self.db.save_metrics(
                    self.datetime, self.perf_tracker.cumulative_risk_metrics)
            ''' -----------------------------------------------    Scan   --'''
            for ticker in data:
                signals[ticker] = data[ticker].price

        ''' ---------------------------------------------------   Orders  --'''
        return signals
```


Credits
-------

Projects and websites below are awesome works that i heavily use, learn from
and want to gratefully thank:

* [Zipline](http://github.com/quantopian/zipline and quantopian http://wwww.quantopian.com)
* [Quantopian](http://www.quantopian.com/)
* [Pandas](http://github.com/pydata/pandas)
* [R-bloggers](http://www.r-bloggers.com/)
* [QSTK](https://github.com/tucker777/QSTK)
* [Coursera](http://www.coursera.org/)
* [Udacity](http://www.udacity.com/)
* [Babypips](http://www.babypips.com/)
* [GLMF](http://www.unixgarden.com/)
