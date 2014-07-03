# hivetech/intuition image
# A raring box with Intuition (https://github.com/hackliff/intuition installed
# and ready to use
#   docker run \
#     -e DB_HOST=172.17.0.4 \
#     -e LANG=fr_FR.UTF-8 \
#     -e LOG=info \
#     -e QUANDL_API_KEY=$QUANDL_API_KEY \
#     hivetech/intuition intuition --context insights.contexts.mongodb.MongodbContext://192.168.0.19:27017/intuition/contexts/bt-yahoo --id chuck --bot --showlog
# VERSION 0.1.0

# == Option 1 ==========
# hivetech/pyscience is an ubuntu 12.04 image with most popular python packages
#FROM hivetech/batcave:pyscience
#MAINTAINER Xavier Bruhiere <xavier.bruhiere@gmail.com>
# == Option 2 ==========
#FROM hivetech/batcave:buildstep
# == Option 3 ==========
FROM hivetech/batcave:base
MAINTAINER Xavier Bruhiere <xavier.bruhiere@gmail.com>
ENV LANG fr_FR.UTF-8

# NOTE Removed for dev r-base
RUN apt-get update -y && \
  apt-get install -y --no-install-recommends python-dev \
  libreadline-dev r-base g++ make libfreetype6-dev \
  libpng-dev libopenblas-dev liblapack-dev gfortran
RUN pip install --upgrade numpy dna
# ======================

ADD . /intuition
RUN mkdir -p /root/.intuition/assets /root/.intuition/data /root/.intuition/logs /root/.intuition/R
RUN cd /intuition && python setup.py install

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#CMD ["/usr/local/bin/intuition", "--help"]
