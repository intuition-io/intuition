#! /bin/bash

modules_requirements_url="https://raw.github.com/hackliff/intuition-modules/develop/requirements.txt"

apt-get -y update
apt-get install -y python-pip python-dev g++ make libfreetype6-dev \
  libpng-dev libopenblas-dev liblapack-dev gfortran
pip install --use-mirrors --upgrade setuptools distribute flake8 nose
pip install --use-mirrors --upgrade numpy

pip install -e git+https://github.com/hackliff/intuition.git@develop#egg=intuition

if [ -n "$FULL_INTUITION" ]; then
  apt-get install r-base
  # Otherwize statsmodel fails:
  pip install --use-mirrors scipy patsy
  wget -qO- ${modules_requirements_url} | xargs pip install --use-mirrors --upgrade
  #FIXME First installation needs to specify lib parameter
  #./scripts/installation/install_r_packages.R
fi
