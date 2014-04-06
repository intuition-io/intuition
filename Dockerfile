# hivetech/intuition image
# A raring box with Intuition (https://github.com/hackliff/intuition installed
# and ready to use
#   docker run \
#     -e DB_HOST=172.17.0.4 \
#     -e LANG=fr_FR.UTF-8 \
#     -e LOG=info \
#     -e QUANDL_API_KEY=$QUANDL_API_KEY \
#     hivetech/intuition --context insights.contexts.mongodb.MongodbContext://192.168.0.19:27017/intuition/contexts/bt-yahoo --id chuck --bot --showlog
# VERSION 0.1.0

# Administration
# hivetech/pyscience is an ubuntu 12.04 image with most popular python packages
FROM hivetech/pyscience
MAINTAINER Xavier Bruhiere <xavier.bruhiere@gmail.com>

#RUN git clone https://github.com/intuition-io/intuition.git -b develop --depth 1 && \
  #cd /intuition && python setup.py install
ADD . /intuition
RUN cd /intuition && python setup.py install

# Install Insights ------------------------------------------
RUN git clone https://github.com/intuition-io/insights.git -b develop --depth 1 && \
  apt-get update && apt-get install -y libreadline-dev && \
  cd insights && python setup.py install

# Install Extras --------------------------------------------
# Install R libraries
RUN wget -qO- http://bit.ly/L39jeY | R --no-save

# TA-Lib support
RUN apt-get install -y libopenblas-dev liblapack-dev gfortran && \
  wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install
# Python wrapper
RUN pip install --use-mirrors TA-Lib==0.4.8

RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV LANG fr_FR.UTF-8
CMD ["/usr/local/bin/intuition"]
