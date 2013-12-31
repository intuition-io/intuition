#! /bin/bash

apt-get -y update
apt-get install -y python-pip python-dev g++ make libfreetype6-dev libpng-dev libopenblas-dev liblapack-dev gfortran r-base
pip install setuptools
pip install numpy

pip install intuition
