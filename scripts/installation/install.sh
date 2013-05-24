#!/bin/bash

set -e

clear
echo $(date) " -- QuanTrade installation script"

# There is a lot to install, so run it as root
if [ $(whoami) != 'root' ]; then
    echo '** Error: This installation script needs root permissions'
    exit 1
fi


echo "Installation of debian packages..."
apt-get install git libzmq-dev r-base python2.7 mysql-server libmysqlclient-dev npm python-pip planner python-dev
pip install pip-tools

#pip install zipline
#TODO Patch zipline !
# Or in dev style:
echo "Cloning  and installing custom zipline project"
git clone https://github.com/Gusabi/zipline $HOME/dev/pojects/zipline
python $HOME/dev/projects/zipline/setup.py install

echo "Environment setup"
#TODO Improve robustness
echo "Creating project configuraiton directory: ~/.quantrade"
mkdir $HOME/.quantrade
echo "Copying configuration file templates..."
echo "Note: do not forget to custom them at the end of the script"
cp ../config/tpl_local.sh $HOME/.quantrade/local.sh
cp ../config/tpl_default.json $HOME/.quantrade/default.json
cp ../config/tpl_shiny-server.config $HOME/.quantrade/shiny-server.config

echo "Writting in ~/.bashrc for permanent automatic environment load"
echo "source $HOME/.quantrade/local.sh" >> $HOME/.bashrc

echo "Sourcing environment setup file."
source ~/.quantrade/local.sh

echo "Restoring user permission"
chown -R $USER ~/.quantrade
chgrp -R $USER ~/.quantrade

echo "Installing dependances with pip..."
./scripts/installation/ordered_pip.sh ./scripts/installation/requirements.txt

#TODO Check for R libs and skip it if absent
echo "" >> /etc/apt/sources.list
echo "## Last R Release" >> /etc/apt/sources.list
echo "deb http://cran.irsn.fr/bin/linux/ubuntu rarin/" >> /etc/apt/sources.list
apt-get update
apt-get install r-base
echo "R installation, assuming you already use it at least once"
./scripts/installation/install_r_packages.R

#TODO Bad..., use n or nvm to install right version ? or github repos ?
#echo "Node.js installation"
#echo "Downloading last release..."
#wget http://nodejs.org/dist/v0.10.0/node-v0.10.0.tar.gz
#tar xvzf node-v0.10.0.tar.gz && cd node-v0.10.0
#./configure
#make
#make install

# Cool version
git clone git://github.com/creationix/nvm.git $HOME/.nvm
#NOTE Assume bash shell, use $SHELL
echo "source $HOME/.nvm/nvm.sh" >> $HOME/.bashrc
$HOME/nvm/nvm.sh install  0.10
echo "# Node management" >> $HOME/.bashrc
echo "export NODE_PATH=$HOME/.nvm/v0.10.7/lib/node_modules" >> $HOME/.bashrc
echo "nvm use 0.10.7" >> $HOME/.bashrc
echo "[[ -r $NVM_DIR/bash_completion ]] && . $NVM_DIR/bash_completion" >> $HOME/.bashrc

echo "Node modules for QuanTrade installation, locally"
cd $QTRADE/server
npm install -g

echo "Setting up mysql quantrade database"
mysql < ./scripts/installation/createdb.sql
#NOTE Generate the script from a template ? (user and password field)
./scripts/database_manager.py -c
./scripts/database_manager.py -a ./data/dump_mysql.csv
./scripts/database_manager.py -a ./data/cac40.csv

#echo "Cleaning..."
#rm *_deps.txt
#rm -rf node-v0.10.0*

echo "Now edit ~/.quantrade/local.sh and ~/.quantrade/default.json to suit your environment"
