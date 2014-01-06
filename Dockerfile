# hivetech/intuition image
# A raring box with Intuition (https://github.com/hackliff/intuition installed
# and ready to use
# VERSION 0.0.1

# Administration
FROM stackbrew/ubuntu:saucy
MAINTAINER Xavier Bruhiere, xavier.bruhiere@gmail.com

# Enable the necessary sources and upgrade to latest
RUN echo "deb http://archive.ubuntu.com/ubuntu saucy main universe multiverse restricted" > /etc/apt/sources.list && \
  apt-get update && apt-get upgrade -y -o DPkg::Options::=--force-confold

# Local settings
RUN apt-get install -y language-pack-fr
#ENV LANGUAGE fr_FR.UTF-8
#ENV LANG fr_FR.UTF-8
#ENV LC_ALL fr_FR.UTF-8

RUN (locale-gen fr_FR.UTF-8 && dpkg-reconfigure locales)

# Keep upstart from complaining
RUN dpkg-divert --local --rename --add /sbin/initctl && ln -s /bin/true /sbin/initctl

# Finally install intuition itself
# Activate full installation, i.e. with modules dependencies
ENV FULL_INTUITION 1
RUN wget -qO- http://bit.ly/1izVUJJ | bash

ENTRYPOINT ["/usr/local/bin/intuition", "--showlog"]
