#!/bin/bash

set -e

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

# Quick run of usual backtests
clear
echo $(date) " [Debug] Choice: " $choice
echo "C'est parti..."

if [ $choice == 1 ]; then
    # Equitie backtest 
    time $QTRADE/application/app.py --initialcash 100000 --tickers random,4 \
        --algorithm BuyAndHold --manager Constant --start 2006-01-10 --end 2008-07-03 \
        --frequency daily --database test --exchange nasdaq
elif [ $choice == 2 ]; then
    # Forex live test !
    time $QTRADE/application/app.py --initialcash 10000 --tickers EUR/USD,EUR/GBP,EUR/JPY \
        --algorithm BuyAndHold --manager Constant --end 21h20 \
        --database test --exchange forex --frequency minute --live

elif [ $choice == 3 ]; then
    # Equitie live test !
    time $QTRADE/application/app.py --initialcash 10000 --tickers random,20 \
        --algorithm Momentum --manager OptimalFrontier --end 12h00 \
        --database test --exchange paris --frequency minute --live
fi

notify-send Simulation "Simulation ended !" --urgency normal --app-name QuanTrade --icon $QTRADE/management/introduction/LaTexSources/images/graph.png
