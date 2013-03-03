Misc
====

Zipline data options
--------------------
    - self.add_source(source)   Could provide more informations
    - CustomObject(DataSource)  Implement a custom source 
    - Custom zipline adapter to produce data

Ideas
-----
    - Logbook lib enable logging to twitter, might be a better way than email to remote notify
    - Generate a report that can be fetch from shiny, the webapp, or automatically when pushing a notification to android device

TODO
----
    - Licences
    - Documentation with sphinx, https://readthedocs.org/, tests with pytest, nose
    - A way to keep track of positions before yelling signals, see https://gist.github.com/fawce/1578485 for state machine, monitoring
    - 13/02 posts on r-bloggers !!
    - A load() function importing modules, with @check decorator that can handle exception
    - The save part of backtest results as a generic decorator using database functions ?
    - Decorator for caching data in optimization process ?
    - Replace OLMAR algo with https://github.com/quantopian/zipline/pull/98/files#diff-0 (+check logbook setup)


Ressources
==========

d3.js tutos
-----------
    - http://alignedleft.com/tutorials/d3/using-your-data/
    - http://www.dashingd3js.com/adding-a-dom-element

Most great websites ressource
-----------------------------
    - https://www.sigfig.com/
    - http://timetotrade.eu/
    - http://www.academictrader.org/
    - https://lucenaresearch.com/our-products/
    - http://www.rapidquant.com/
    - https://github.com/trbck    Datafeed and zipline stuffs
    - https://gist.github.com/fawce   One of quantopian contributor
    - https://github.com/quantopian/quantopian-algos    pairs-trade worth a try
    - https://github.com/ravster/pleasance
    - https://github.com/aivgit/aivengo
    - https://github.com/fxmozart/encog-dotnet-core    Encog markte examples
    - http://www.estimize.com/
    - https://www.recordedfuture.com/
    - http://stocktwits.com/
    - http://gekkoquant.com/
    - https://github.com/ermakus/pyquik
    - https://github.com/gbeced/pyalgotrade
    - http://stockcharts.com/school/doku.php?id=chart_school:trading_strategies
    - http://quantsignals.wordpress.com/

Web Dev
-------
    - boostrap, express, jade, stylus, socket.io, , coffeescript
    - https://github.com/socketstream/socketstream (under res/fetcher/quote-stream)
    - http://howtonode.org/heat-tracer
    - https://github.com/Sly777/Chat-Tutorial-with-Node.js--Socket.io-and-Express
    - http://www.danielbaulig.de/socket-ioexpress/
    - https://github.com/haganbt/Datasift-Interaction-Counter
    - http://www.aerotwist.com/tutorials/getting-started-with-three-js/
    - http://processingjs.org/learning/
    - http://knockoutjs.com/examples/twitter.html
    - http://backbonejs.org/

Openstack: hosting and distributed platform
-------------------------------------------
    - http://wiki.openstack.org/StartingPage

Econometric tools, R
--------------------
    - http://braverock.com/brian/R/PerformanceAnalytics/html/PerformanceAnalytics-package.html

Github
------
    - Coursera dude, some repos about comput. Invest: https://github.com/thinklancer
    - OpenQuant, strategie lab: https://github.com/maihde/quant (under res/quant)
    - High performance trading and execution engine: https://github.com/danielflam/Mervin
    - Simulation and live trading, but seems obscure: https://github.com/kpnolan/stock_db_capture
    - Automated trading in r, recommended with socketstream or std: https://github.com/yiransheng/rTrader (under res/rTrader)
    - std, for shaky trading desk. Real time: https://github.com/yiransheng/std (under res/fetcehr/std)
    - SQL Database environment for stocks: https://github.com/hamiltonkibbe/stocks (under res/stocks, tested once, problem with indicators, otherwise work !)

Portfolio optimization on r-bloggers
------------------------------------
    http://www.r-bloggers.com/universal-portfolio-part-10/
    http://www.r-bloggers.com/expected-shortfall-portfolio-optimization-in-r-using-nloptr/
    http://www.r-bloggers.com/portfolio-diversity/
    http://www.r-bloggers.com/backtesting-asset-allocation-portfolios/
    http://www.r-bloggers.com/adaptive-asset-allocation/
    http://www.r-bloggers.com/portfolio-optimization-specify-constraints-with-gnu-mathprog-language/
    http://www.r-bloggers.com/portfolio-optimization-%E2%80%93-why-do-we-need-a-risk-model/
    http://www.r-bloggers.com/the-most-diversified-or-the-least-correlated-efficient-frontier/
    http://www.r-bloggers.com/minimum-investment-and-number-of-assets-portfolio-cardinality-constraints/
    http://www.r-bloggers.com/2-dimensions-of-portfolio-diversity/
    http://www.r-bloggers.com/the-top-7-portfolio-optimization-problems/ 

Quantopian
----------
    - Added sortino and informations ration as risk metrics
    - http://www.investopedia.com/terms/s/sortinoratio.asp#axzz2KUJ6ZYyV
    - http://www.investopedia.com/terms/i/informationratio.asp#axzz2KUJ6ZYyV
