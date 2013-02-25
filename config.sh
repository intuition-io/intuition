#!/bin/bash

#-----------------------------------------------------------------
# Configuration script to set QuantTrade enviroment variables.
# Edit the first few uncommented lines below, then copy this file 
# to localconfig.sh. Be sure to "source localconfig.sh" each time 
# you use QuanTrade


#-----------------------------------------------------------------
export QTRADE=$HOME/dev/projects/ppQuanTrade
export ZIPLINE=$HOME/dev/projects/zipline
export QTRADEDATA=$QTRADE/database
export QTRADEDB=stocks.db
export QTRADE_LOG=$QTRADE/quantrade.log
export QTRADE_CONFIGURATION=local
export QTRADE_MODE=dev
export QTRADE_NMA_KEY=95ea3f34f891fc3963047c70bdcdc01627cc120a46f06960
