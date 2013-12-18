#!/bin/bash

clear
set -e

if [ $# -gt 0 ]; then
  choice=$1
else
  #FIXME Change this ugly hardcoded hostname
  if [ $(hostname) != 'laptop-300E5A' ]; then
    # We are on the server, no gui menu, use command line
    echo 'No gui available, Provide a shorcut number [1..3]'
    read choice
  else
    # Quick and dirty zenity menu
    choice=`(
    simulations=("1 Backtest Equities", "2 Live Forex", "3 Live Equities")
    for simu in ${simulations[@]}
    do
      echo $simu
    done
    ) | zenity --list --width=300 --height=200 --title="Simulation Shortcuts" \
      --text="Select the simulation to run" \
      --column="Number" --column="Mode" --column="Assets"`
  fi
fi


# Quick run of usual backtests
echo $(date) " [Debug] Choice: " $choice
echo "C'est parti..."

# Equitie backtest
if [ $choice == 1 ]; then
  #time application/app.py --initialcash 50000 --universe goog,aapl \
  #time application/app.py --initialcash 50000 --universe GOOG/NASDAQ_GOOG,GOOG/NASDAQ_AAPL \
  #time application/app.py --initialcash 50000 --universe quotes_fchi \
  time application/app.py --initialcash 10000 --universe nasdaq,5 \
    --loglevel CRITICAL --algorithm DualMovingAverage --manager Constant --start 2011-05-10 \
    --end 2013-11-10 --frequency daily --exchange nasdaq --source YahooPriceSource
    #--frequency daily --exchange nasdaq --source CSVSource
    #--frequency daily --exchange nasdaq --source QuandlSource
    #--frequency daily --exchange nasdaq --source YahooOHLCSource

  # Forex live test !
elif [ $choice == 2 ]; then
  time application/app.py --initialcash 10000 --universe EUR/USD,EUR/GBP,GBP/USD,USD/CHF,EUR/JPY,EUR/CHF,USD/CAD,AUD/USD,GBP/JPY \
    --algorithm DualMovingAverage --manager Constant --end 23h --loglevel CRITICAL \
    --exchange forex --frequency minute --live --source ForexLiveSource

  # Equitie live test !
elif [ $choice == 3 ]; then
  #time application/app.py --initialcash 50000 --universe jxr,su \
  time application/app.py --initialcash 10000 --universe cac40 \
    --algorithm DualMovingAverage --manager OptimalFrontier --end 16h --loglevel CRITICAL \
    --exchange paris --frequency minute --source EquitiesLiveSource --live

else
  echo '** Error: invalid simulation number provided: ' $choice
fi

#notify-send Simulation "Simulation ended !" --urgency normal --app-name QuanTrade --icon $QTRADE/management/introduction/LaTexSources/images/graph.png
