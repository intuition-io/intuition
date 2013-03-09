server
======

Code for webapp frontend and distributed stuff


Shiny server
------------ 

    As this package needs a greater version of node than debian provide, it is not included by default in package.json.
    However it is pretty simple to install it, following instructions at https://npmjs.org/package/shiny-server for installation details (more precisions here to come)

    Notes: One version is in ~/ShinyApp, the other in /var/shiny-server/www
    Run 'sudo node_modules/.bin/shiny-server [shiny-server.config]'
    Go to http://127.0.0.1:3838/users/xavier/shiny-backtest/ or http://127.0.0.1:3838/shiny-backtest/


TODO
----
    * A real node package
    * script to commit changes from ppQuanTrade to ~/ShinyApps/shiny-backtest (unused for now)
    * Got /var/shiny-server/www/shiny-backtest to work, probably related to R package installation (under user root dir instead of system)

Notes
-----
node.js cool logging: logging
                      logule
                      tracer
                      log4js


ZMQ logbook Messaging format
----------------------------

```python
{
     "thread_name": "MainThread",
     "args": [], 
     "exception_name": null, 
     "thread": 139849036379904, 
     "extra": {"ip": "127.0.0.1"}, 
     "process": 420, 
     "func_name": "<module>", 
     "process_name": "MainProcess", 
     "formatted_exception": null, 
     "module": "__main__", 
     "filename": "/home/xavier/dev/projects/ppQuanTrade/neuronquant/network/transport.py", 
     "exception_message": null, 
     "heavy_initialized": true, 
     "kwargs": {}, 
     "lineno": 162, 
     "time": "2013-02-24T12:46:30.398066Z", 
     "msg": "Client working...", 
     "message": "Client working...", 
     "level": 2, 
     "information_pulled": true, 
     "channel": "ZMQ Messaging"
}
```


Ressources
----------
    * http://www.rinfinance.com/agenda/
    * http://statsadventure.blogspot.fr/2012/08/minimum-expected-shortfall-portfolio.html

    * http://tjholowaychuk.com/post/9103188408/commander-js-nodejs-command-line-interfaces-made-easy    (http://www.slalompoint.com/node-command-line-interface-p2/)
    * https://github.com/chriso/cli
    * https://github.com/mscdex/node-ncurses
    * https://github.com/hij1nx/complete
    * https://github.com/dylang/logging
    * https://github.com/baryshev/look

    * http://twitter.github.com/bootstrap/
    * https://github.com/visionmedia/uikit

    * https://github.com/LearnBoost/cli-table
    * https://github.com/substack/node-multimeter   or   https://github.com/visionmedia/node-progress
    * https://github.com/baryon/tracer
    * https://github.com/LearnBoost/console-trace
    * https://github.com/LearnBoost/distribute
    * https://github.com/LearnBoost/knox
    * https://github.com/LearnBoost/engine.io-client

    * https://cliff.readthedocs.org/en/latest/
    * http://cement.readthedocs.org/en/portland

https://github.com/jondot/graphene
http://libsaas.net/
http://jslate.com/
