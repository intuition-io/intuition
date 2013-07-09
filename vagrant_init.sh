#!/bin/bash

# This script will be run by Vagrant to
# set up everything necessary to use Zipline.

# Because this is intended be a disposable dev VM setup,
# no effort is made to use virtualenv/virtualenvwrapper

# It is assumed that you have "vagrant up"
# from the root of the zipline github checkout.
# This will put the zipline code in the
# /vagrant folder in the system.

VAGRANT_LOG="/home/vagrant/vagrant.log"

# Run a full apt-get update first.
echo "Updating apt-get caches..."
apt-get -y update 2>&1 >> "$VAGRANT_LOG"

# Install required packages
echo "Installing required packages..."
apt-get -y install git r-base python-pip python-dev g++ make gfortran libzmq-dev mysql-client libmysqlclient-dev curl 2>&1 >> "$VAGRANT_LOG"

echo "Installing python package dependencies..."
# Ubuntu 12.04 relative hack, i guess...
pip install --upgrade distribute 2>&1 >> "$VAGRANT_LOG"

pip install --use-mirrors -r /vagrant/scripts/installation/requirements.txt 2>&1 >> "$VAGRANT_LOG"
# Add scipy next (if it's not done now, breaks installing of statsmodels for some reason ??)
#echo "Installing zipline"
#pip install scipy==0.12.0 2>&1 >> "$VAGRANT_LOG"

# Setup mysql

echo "Configuring environment"
echo "export QTRADE=/vagrant" >> /home/vagrant/.bashrc
echo "export PYTHONPATH=$PYTHONPATH:$QTRADE" >> /home/vagrant/.bashrc
echo "Done !"
