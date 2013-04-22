Misc
====

Zipline data options
--------------------

* self.add_source(source)   Could provide more informations
* CustomObject(DataSource)  Implement a custom source 
* Custom zipline adapter to produce data

Ideas
-----

* Logbook lib enable logging to twitter, might be a better way than email to remote notify
* Generate a report that can be fetched from shiny, the webapp, or automatically when pushing a notification to android device

TODO
----

[x] Licence
[ ] Documentation with sphinx, https://readthedocs.org/, tests with pytest, nose, doctest
[ ] A way to keep track of positions before yelling signals, see https://gist.github.com/fawce/1578485 for state machine, monitoring
[ ] 13/02 posts on r-bloggers !!
[ ] A load() function importing modules, with @check decorator that can handle exception
[ ] The save part of backtest results as a generic decorator using database functions ?
[ ] Decorator for caching data in optimization process ?
[x] Replace OLMAR algo with https://github.com/quantopian/zipline/pull/98/files#diff-0 (+check logbook setup)
[ ] googlegroups 
[ ] Android app with C2DM push notification (and node.js module)
[ ] node tests with nodeunit, jscoverage, http://visionmedia.github.com/mocha/, or jasmine 
[ ] Study msgpack for more efficient messages passing with zmq


Ressources
==========

financial area
--------------

* google api https://gist.github.com/border/1321781
* https://openexchangerates.org/about
* http://josscrowcroft.github.com/money.js/
* datasets http://www.infochimps.com/documentation


d3.js tutos
-----------

* http://alignedleft.com/tutorials/d3/using-your-data/
* http://www.dashingd3js.com/adding-a-dom-element

Most great websites ressource
-----------------------------

* https://www.sigfig.com/
* http://timetotrade.eu/
* http://www.academictrader.org/
* https://lucenaresearch.com/our-products/
* http://www.rapidquant.com/
* https://github.com/trbck    Datafeed and zipline stuffs
* https://gist.github.com/fawce   One of quantopian contributor
* https://github.com/quantopian/quantopian-algos    pairs-trade worth a try
* https://github.com/ravster/pleasance
* https://github.com/aivgit/aivengo
* https://github.com/fxmozart/encog-dotnet-core    Encog markte examples
* http://www.estimize.com/
* https://www.recordedfuture.com/
* http://stocktwits.com/
* http://gekkoquant.com/
* https://github.com/ermakus/pyquik
* https://github.com/gbeced/pyalgotrade
* http://stockcharts.com/school/doku.php?id=chart_school:trading_strategies
* http://quantsignals.wordpress.com/

Web Dev
-------

* boostrap, express, jade, stylus, socket.io, , coffeescript
* https://github.com/socketstream/socketstream (under res/fetcher/quote-stream)
* http://howtonode.org/heat-tracer
* https://github.com/Sly777/Chat-Tutorial-with-Node.js--Socket.io-and-Express
* http://www.danielbaulig.de/socket-ioexpress/
* https://github.com/haganbt/Datasift-Interaction-Counter
* http://www.aerotwist.com/tutorials/getting-started-with-three-js/
* http://processingjs.org/learning/
* http://knockoutjs.com/examples/twitter.html
* http://backbonejs.org/

Openstack + other cloud stuff
-----------------------------

* http://wiki.openstack.org/StartingPage
* http://www.rackspace.com/
* https://developers.google.com/appengine/docs/python/datastore/?hl=fr
* https://cloudant.com/
* http://xeround.com/cloud-database-comparison/

Econometric tools, R
--------------------

* http://braverock.com/brian/R/PerformanceAnalytics/html/PerformanceAnalytics-package.html

Graphics
--------

* Polycde

Github
------

* Coursera dude, some repos about comput. Invest: https://github.com/thinklancer
* OpenQuant, strategie lab: https://github.com/maihde/quant (under res/quant)
* High performance trading and execution engine: https://github.com/danielflam/Mervin
* Simulation and live trading, but seems obscure: https://github.com/kpnolan/stock_db_capture
* Automated trading in r, recommended with socketstream or std: https://github.com/yiransheng/rTrader (under res/rTrader)
* std, for shaky trading desk. Real time: https://github.com/yiransheng/std (under res/fetcehr/std)
* SQL Database environment for stocks: https://github.com/hamiltonkibbe/stocks (under res/stocks, tested once, problem with indicators, otherwise work !)
* https://github.com/albertosantini/node-finance
* https://github.com/albertosantini/node-conpa (http://conpa.jit.su/) 
* https://github.com/fearofcode/bateman
* https://github.com/usablica/intro.js
* https://github.com/cantino/huginn
* https://github.com/saoj/options-lib
* https://github.com/klen/python-mode
* https://github.com/Valloric/YouCompleteMe
* https://github.com/Mic92/python-mpd2
* https://github.com/docopt/docopt
* https://github.com/samuraisam/pyapns
* https://github.com/kennethreitz/clint 
* http://www.clips.ua.ac.be/pages/pattern
* https://github.com/tweepy/tweepy
* https://github.com/progrium/localtunnel
* http://www.git-legit.org/
* http://www.tidesdk.org/

Portfolio optimization on r-bloggers
------------------------------------

* http://www.r-bloggers.com/universal-portfolio-part-10/
* http://www.r-bloggers.com/expected-shortfall-portfolio-optimization-in-r-using-nloptr/
* http://www.r-bloggers.com/portfolio-diversity/
* http://www.r-bloggers.com/backtesting-asset-allocation-portfolios/
* http://www.r-bloggers.com/adaptive-asset-allocation/
* http://www.r-bloggers.com/portfolio-optimization-specify-constraints-with-gnu-mathprog-language/
* http://www.r-bloggers.com/portfolio-optimization-%E2%80%93-why-do-we-need-a-risk-model/
* http://www.r-bloggers.com/the-most-diversified-or-the-least-correlated-efficient-frontier/
* http://www.r-bloggers.com/minimum-investment-and-number-of-assets-portfolio-cardinality-constraints/
* http://www.r-bloggers.com/2-dimensions-of-portfolio-diversity/
* http://www.r-bloggers.com/the-top-7-portfolio-optimization-problems/ 

Co-working
----------

* http://letank.spintank.fr/
* http://www.studios-singuliers.fr/offre/
* http://www.dojocrea.fr/nos_lieux.html
* http://www.lelaptop.com/
* http://www.mozaik-coworking.com/
* http://www.soleillescowork.com/59-0-SERVICES.html
* http://propulseurs.com/des-references-qui-decollent/
* http://lamutinerie.org

Start-up
--------
* http://www.swnext.co/about/
* http://www.amazon.fr/Business-Model-G%C3%A9n%C3%A9ration-Alexander-Osterwalder/dp/2744064874/ref=sr_1_1?ie=UTF8&qid=1366105065&sr=8-1&keywords=Business+Model+Generation
* http://www.amazon.fr/Startup-Owners-Manual-Step---step/dp/0984999302/ref=sr_1_1?ie=UTF8&qid=1366105081&sr=8-1&keywords=The+Startup+Owner%27s+Manual
* https://launchpadcentral.com/
* https://strategyzer.com/
* http://www.businessmodelgeneration.com/

Knowledge management
--------------------

* https://github.com/mikedeboer/node-github
* https://github.com/christkv/node-git/tree/master/test
* https://github.com/qrpike/NodeJS-Git-Server

* https://codenvy.com/features
* http://ace.ajax.org/#nav=about

* http://www.openstack.org/
* http://devstack.org/
