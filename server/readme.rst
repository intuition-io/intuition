server
======

Code for webapp frontend and distributed stuff


Shiny-Server
------------
    - https://npmjs.org/package/shiny-server

Run shiny server
----------------
    Notes: One version is in ~/ShinyApp, the other in /var/shiny-server/www
    1. Run 'sudo node_modules/.bin/shiny-server [shiny-server.config]'
    2. Go to http://127.0.0.1:3838/users/xavier/shiny-backtest/ or http://127.0.0.1:3838/shiny-backtest/

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


TODO
----
    1. Env variable access, for db connection (or an other way)
    2. Update.sh to commit changes from ppQuanTrade to ~/ShinyApps/shiny-backtest
    3. Got /var/shiny-server/www/shiny-backtest to work, probably related to R package installation (under user root dir instead of system)


tmp
---
http://www.rinfinance.com/agenda/
http://statsadventure.blogspot.fr/2012/08/minimum-expected-shortfall-portfolio.html
see pdf
