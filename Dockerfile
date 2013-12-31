# hivetech/intuition image
# A raring box with Intuition (https://github.com/hackliff/intuition installed
# and ready to use
# VERSION 0.0.1

# Administration
FROM boxcar/raring
MAINTAINER Xavier Bruhiere, xavier.bruhiere@gmail.com

# Make sure the package repository is up to date
RUN echo "deb http://archive.ubuntu.com/ubuntu raring main universe" > /etc/apt/sources.list
RUN apt-get update

# Local settings
# Change eventually fr_FR to us_US
RUN apt-get install -y language-pack-fr
ENV LANGUAGE fr_FR.UTF-8
ENV LANG fr_FR.UTF-8
ENV LC_ALL fr_FR.UTF-8

RUN locale-gen fr_FR.UTF-8
RUN dpkg-reconfigure locales

# Keep upstart from complaining
RUN dpkg-divert --local --rename --add /sbin/initctl
RUN ln -s /bin/true /sbin/initctl

# Common needed stuff for an efficient ansible-ready machine
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y python python-apt \
  python-pip python-dev g++ make libfreetype6-dev libpng-dev \
  libopenblas-dev liblapack-dev gfortran r-base

# Create a normal default user (vagrant / docker images have just vagrant / root)
# #TODO I'm pretty sure there is a smarter way to do that
RUN pip install setuptools numpy
RUN pip install intuition

ENTRYPOINT ["/usr/local/bin/intuition", "--verbose"]
