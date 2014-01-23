#! /bin/bash

apt-get -y update
apt-get install -y python-pip python-dev g++ make libfreetype6-dev \
  libpng-dev libopenblas-dev liblapack-dev gfortran
pip install --quiet --use-mirrors setuptools distribute flake8 nose
pip install --quiet --use-mirrors numpy

pip install --use-mirrors --upgrade intuition

if [ -n "$FULL_INTUITION" ]; then
  apt-get install -y r-base libssl-dev
  pip install --use-mirrors --upgrade insights
  # Install R libraries
  wget -qO- http://bit.ly/L39jeY | R --no-save
fi
