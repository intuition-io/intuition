#!/bin/bash

clear
echo "-- QuanTrade installation script"

echo "Environment setup"
#TODO Add a test
echo "Creating project configuraiton directory: ~/.quantrade"
mkdir $HOME/.quantrade
echo "Copying configuration file templates..."
echo "Note: do not forget to custom them at the end of the script"
mv ../config/tpl_local.sh $HOME/.quantrade/local.sh
mv ../config/tpl_default.json $HOME/.quantrade/default.json

echo "Writting in ~/.bashrc for permanent automatic environment load"
echo "source $HOME/.quantrade/local.sh" >> $HOME/.bashrc

echo "Sourcing environment setup file."
source ../config/local.sh

echo "installation of debian packages..."

echo "Writing python quantrade dependances"
cat ./qt_*.txt > qt_deps.txt
echo "Installing dependances with pip..."
sudo ./ordered_pip.sh qt_deps.txt

echo "Writing python quantrade dependances"
cat ./z_*.txt > z_deps.txt
echo "Installing dependances with pip..."
sudo ./ordered_pip.sh z_deps.txt

echo "R installation, assuming you already use it at least once"
./scripts/install_r_packages.R

echo "Node.js installation"
echo "Downloading last release..."
wget http://nodejs.org/dist/v0.10.0/node-v0.10.0.tar.gz
tar xvzf node-v0.10.0.tar.gz && cd node-v0.10.0
./configure
make
sudo make install

echo "Node modules for QuanTrade installation, locally"
cd $QTRADE/server
npm install

echo "Now edit ~/.quantrade/local.sh and ~/.quantrade/default.json to suit your environment"
echo "Finally, setup a mysql database"

echo "Cleaning..."
rm *_deps.txt
rm -rf node-v0.10.0*
