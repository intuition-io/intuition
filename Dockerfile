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

# Finally install intuition itself
# Activate full installation, i.e. with modules dependencies
ENV FULL_INTUITION 1
RUN wget -qO- https://raw.github.com/hackliff/intuition/develop/scripts/installation/bootstrap.sh | bash

ENTRYPOINT ["/usr/local/bin/intuition", "--showlog"]
