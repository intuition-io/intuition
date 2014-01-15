#! /bin/bash

apt-get -y update
apt-get install -y python-pip python-dev g++ make libfreetype6-dev \
  libpng-dev libopenblas-dev liblapack-dev gfortran
pip install --quiet --use-mirrors setuptools distribute flake8 nose
pip install --quiet --use-mirrors numpy

pip install --quiet --use-mirrors --upgrade insights

if [ -n "$FULL_INTUITION" ]; then
  apt-get install -y r-base
  pip install --use-mirrors --upgrade insights
  #FIXME First installation needs to specify lib parameter
  #./scripts/installation/install_r_packages.R
fi
