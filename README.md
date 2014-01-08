Intuition
=========

> Automated quantitative trading system kit, for hackers


![Dashboard](https://raw.github.com/hivetech/hivetech.github.io/master/images/QuantDashboard.png)


Overview
--------

**Intuition** is an engine, some building bricks and a set of tools meant to
let you efficiently and intuitively make your own **automated quantitative trading
system**. It is designed to let traders, developers and scientists explore,
improve and deploy market technical hacks.

While the project is still at an early stage, you can already write, use, combine
**signal detection algorithms, portfolio allocation strategies, data sources
and contexts configurators**. Just plug your strategies and analyze
**backtests** or monitor **live trading sessions**.

In addition I work on facilities to build a distributed system and
21st century application (big data, fat computations, d3.js and other html5
stuff), tools to mix languages like Python, node.js and R and a financial
library. You will find some goodies like machine learning forecast, markowitz
portfolio optimization, genetic optimization, sentiment analysis from twitter, ...


Features
--------

* Highly configurable trading environment, powered by [zipline](https://github.com/quantopian/zipline)
* From instant kickstart to full control
* Made to let you tweak algorithms, portfolio manager, data sources, contexts and plugins
* Already includes many
* Experimental live trading on different markets (Nyse, Nasdaq, CAC40 and Forex for now)
* Experimental R integration in your algorithms
* Results analyser
* Mail and Android notifications (for now with the help of freely available [NotifyMyAndroid](http://www.notifymyandroid.com/) or [PushBullet](https://www.pushbullet.com))
* Financial library, with common used trading functions, data fetchers, ... used for example to solve Coursera econometrics assignments
* Easy to use data management, powered by [rethinkdb](rethinkdb.com)
* [Docker](docker.io) support for development workflow and deployment
* Kind of a CI showcase as I am testing [travis](https://travis-ci.org), [wercker](wercker.com), [shippable](shippable.com), [drone.io](shippable.com), [coveralls](coveralls.io) and [landscape](landscape.io)


Status
------

<!--[![wercker status](https://app.wercker.com/status/f39a4be40502a31b3dcb94875c787b56/m "wercker status")](https://app.wercker.com/project/bykey/f39a4be40502a31b3dcb94875c787b56)-->
[![wercker status](https://app.wercker.com/status/f39a4be40502a31b3dcb94875c787b56 "wercker status")](https://app.wercker.com/project/bykey/f39a4be40502a31b3dcb94875c787b56)
[![Build Status](https://drone.io/github.com/hackliff/intuition/status.png)](https://drone.io/github.com/hackliff/intuition/latest)
[![Build Status](https://travis-ci.org/hackliff/intuition.png?branch=develop)](https://travis-ci.org/hackliff/intuition)
[![Coverage Status](https://coveralls.io/repos/hackliff/intuition/badge.png)](https://coveralls.io/r/hackliff/intuition)
[![Code Health](https://landscape.io/github/hackliff/intuition/develop/landscape.png)](https://landscape.io/github/hackliff/intuition/develop)
[![License](https://pypip.in/license/intuition/badge.png)](https://pypi.python.org/pypi/intuition/)

**Attention** Project is in an *early alpha*, and under heavy development.
 The new version 0.3.0 revises a lot of code :

* Algoithms, managers and data sources have their [own repository](https://github.com/hackliff/insights)
* More powerful API to build custom versions of them
* The context module now handles configuration
* [Shiny](http://www.rstudio.com/shiny/) interface, [Dashboard](http://fdietz.github.io/team_dashboard/) and clustering will have their intuition-plugins repository (soon)
* ZeroMQ messaging is for now removed but might be back for inter-algo communication
* So is MySQL, that has been removed and will be re-implemented as a [data plugin](https://github.com/hackliff/intuition-modules/tree/develop/plugins)
* But currently it has been replaced by [Rethinkdb](rethinkdb.com)
* Installation is much simpler and a docker image is available for development and deployment
* More intuitive configuration splitted between the context mentioned, command line argument and environment variables
* And a lot (I mean A LOT) of house keeping and code desgin stuff


Installation
------------

You are just a few steps away from algoritmic trading. Choose one of the
following installation method

* The usual way

```console
$ pip install intuition
$ # Optionnaly, install offcial algorithms, managers, ...
$ pip install insights
```

* One-liner for the full installation (i.e. with packages and buit-in
  [modules](https://github.com/hackliff/insights))

```console
$ export FULL_INTUITION=1
$ wget -qO- http://bit.ly/1izVUJJ | sudo -E bash
$ # ... Go grab a coffee
```

* From source

```console
$ git clone https://github.com/hackliff/intuition.git
$ cd intuition && sudo make
```

* Sexy, early-adopter style

```console
$ docker pull hivetech/intuition
```

Getting started
---------------

Intuition wires 4 primitives to build up the system : A data source generates
events, processed by the algorithm, that can optionnaly use a portfolio manager
to compute assets allocation. They are configured through a Context, while
third party services use environment variables (take a look in
config/local.env).

The following example trades in real time forex, with a simple buy and hold
algorithm and a portfolio manager that allocates same amount for each asset.
Their configuration below is stored in a json file.

```console
$ intuition --context file::liveForex.json --id chuck --showlog
```

```json
{
    id: "liveForex",
    start: "2011-05-05",
    end: "2013-10-05",
    frequency: "day",
    universe: "forex,5",
    algorithm: {
        save: false
    },
    manager: {
        android: 0,
        buy_scale: 150,
        cash: 10000,
        max_weight: 0.3,
        perc_sell: 1,
        sell_scale: 100
    },
    modules: {
        context: "file",
        algorithm: "algorithms.buyandhold.BuyAndHold",
        data: "sources.live.forex.ForexLiveSource",
        manager: "managers.fair.Fair"
    }
}
```

Note that in the current implementation, Nasdaq, Nyse, Cac 40 and Forex markets
are available.

Alternatively you can use docker. Here we also fire up a [rethinkdb](rethinkdb.com)
database to store portfolios while trading, and
[mongodb](http://www.mongodb.org/) to store configurations.

```console
$ docker run -d -name mongodb -p 27017:27017 -p 28017:28017 waitingkuo/mongodb

$ docker run -d -name rethinkdb crosbymichael/rethinkdb --bind all

$ docker run \
  -e PUSHBULLET_API_KEY=$PUSHBULLET_API_KEY \
  -e QUANDL_API_KEY=$QUANDL_API_KEY \
  -e MAILGUN_API_KEY=$MAILGUN_API_KEY \
  -e TRUEFX_API=$TRUEFX_API \
  -e DB_HOST=$DB_HOST \
  -e DB_PORT=$DB_PORT \
  -e DB_NAME=$DB_NAME \
  -e LOG=debug \
  -e LANGUAGE="fr_FR.UTF-8" \
  -e LANG="fr_FR.UTF-8" \
  -e LC_ALL="fr_FR.UTF-8" \
  -name trade_box hivetech/intuition \
  intuition --context mongodb::${host_ip}:27017/backtestNasdaq --showlog
```

For Hackers
-----------

You can easily work out and plug your own strategies :

* [Algorithm API](https://github.com/hackliff/insights/blob/develop/insights/algorithms/readme.md)
* [Portfolio API](https://github.com/hackliff/insights/blob/develop/insights/managers/readme.md)
* [Data API](https://github.com/hackliff/insights/blob/develop/insights/sources/readme.md)
* [Context API](https://github.com/hackliff/insights/blob/develop/insights/contexts/readme.md)
* [Middlewares](https://github.com/hackliff/insights/blob/develop/insights/plugins/readme.md)

Either clone the [insights repository](https://github.com/hackliff/insights)
and hack it or start from scratch. Just make sure the modules paths you give in
the configuration are in the python path.


The [provided](https://github.com/hackliff/intuition/blob/develop/app/intuition)
``intuition`` command does already a lot of things but why not improve it or
write your own. Here is a minimal implementation, assuming you installed
*insights*.

```python
from datetime import datetime
from intuition.core.engine import Simulation

engine = Simulation({
    'end': datetime(2014, 1, 7),
    'universe': 'cac40',
    'modules': {
        'algorithm': 'algorithms.movingaverage.DualMovingAverage',
        'manager': 'managers.gmv.GlobalMinimumVariance',
        'data': 'sources.live.Equities.EquitiesLiveSource'}})

# Use the configuration to prepare the trading environment
engine.configure()

data = {'universe': 'cac40',
        'index': pd.date_range(datetime.now(), datetime(2014, 1, 7))}
analyzes = engine.run(session, data)

# Explore the analyzes object
print analyzes.overall_metrics('one_month')
print analyzes.results.tail()
```


Contributing
------------

> Fork, implement, add tests, pull request, get my everlasting thanks and a
> respectable place here [=)](https://github.com/jondot/groundcontrol)


License
-------

Copyright 2014 Xavier Bruhiere
Intuition is available under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0.html).

---------------------------------------------------------------

Credits
-------

* [Zipline](http://github.com/quantopian/zipline)
* [Quantopian](http://www.quantopian.com/)
* [Pandas](http://github.com/pydata/pandas)
* [R-bloggers](http://www.r-bloggers.com/)
* [QSTK](https://github.com/tucker777/QSTK)
* [Coursera](http://www.coursera.org/)
* [Udacity](http://www.udacity.com/)
* [Babypips](http://www.babypips.com/)
* [GLMF](http://www.unixgarden.com/)
