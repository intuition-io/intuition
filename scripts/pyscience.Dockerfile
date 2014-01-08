# hivetech/science image
# A raring box with most common python packages for science installed
# VERSION 0.0.1

# Administration
FROM stackbrew/ubuntu:saucy
MAINTAINER Xavier Bruhiere, xavier.bruhiere@gmail.com

# Enable the necessary sources and upgrade to latest
RUN echo "deb http://archive.ubuntu.com/ubuntu saucy main universe multiverse restricted" > /etc/apt/sources.list && \
  apt-get update && apt-get upgrade -y -o DPkg::Options::=--force-confold

# Local settings
RUN apt-get install -y language-pack-fr wget git-core python-pip python-dev r-base \
  g++ make libfreetype6-dev libpng-dev libopenblas-dev liblapack-dev gfortran ipython

ENV LANGUAGE fr_FR.UTF-8
ENV LANG fr_FR.UTF-8
ENV LC_ALL fr_FR.UTF-8
RUN locale-gen fr_FR.UTF-8 && dpkg-reconfigure locales

RUN pip install -q --use-mirrors --upgrade setuptools flake8 nose cython patsy
RUN pip install -q -e git+https://github.com/numpy/numpy.git@master#egg=numpy
RUN pip install -q -e git+https://github.com/pydata/pandas.git@master#egg=pandas
RUN pip install -q -e git+https://github.com/scipy/scipy.git@master#egg=scipy
#RUN pip install -q --use-mirrors matplotlib sympy rpy2

#FIXME It ends instantly
ENTRYPOINT ["/usr/bin/ipython"]
