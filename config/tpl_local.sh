#!/bin/bash

#-----------------------------------------------------------------
# Configuration script to set NeuronQuant enviroment variables.
# Edit as required by your enviroment. 
# Be sure to "source config.sh" each time 
#-----------------------------------------------------------------

# Projects path
export QTRADE=$HOME/dev/projects/ppQuanTrade
export ZIPLINE=$HOME/dev/projects/zipline
export QTRADEDATA=$QTRADE/data
export QTRADE_SQLITE=stocks.db
export QTRADE_LOG=$HOME/.quantrade/quantrade.log
export QTRADE_CONFIGURATION=local

# For development: add zipline and neuronquant lib in python path
export PYTHONPATH=$PYTHONPATH:$QTRADE:$ZIPLINE

#NotifyMyAndroid key, check http://www.notifymyandroid.com/index.jsp
export QTRADE_NMA_KEY=

#Node.js stuff
#export NODE_CONFIG_DIR=$QTRADE/config
export NODE_CONFIG_DIR=$HOME/.quantrade
export NODE_ENV=development
