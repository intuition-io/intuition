# hivetech/intuition image
# A raring box with Intuition (https://github.com/hackliff/intuition installed
# and ready to use
# VERSION 0.1.0

# Administration
# hivetech/pyscience is an ubuntu 13.10 image with most popular python packages
FROM hivetech/pyscience
MAINTAINER Xavier Bruhiere <xavier.bruhiere@gmail.com>

# Enable the necessary sources and upgrade to latest
RUN echo "deb http://archive.ubuntu.com/ubuntu saucy main universe multiverse restricted" > /etc/apt/sources.list && \
  apt-get update && apt-get upgrade -y -o DPkg::Options::=--force-confold

# Local settings
RUN apt-get install -y language-pack-fr wget git-core
ENV LANGUAGE fr_FR.UTF-8
ENV LANG fr_FR.UTF-8
ENV LC_ALL fr_FR.UTF-8
RUN locale-gen fr_FR.UTF-8 && dpkg-reconfigure locales

#RUN pip install --use-mirrors intuition
#RUN pip install --use-mirrors insights
RUN git clone https://github.com/hackliff/intuition.git -b develop --depth 1 && \
  cd intuition && python setup.py install

# Install modules
RUN git clone https://github.com/hackliff/insights.git -b develop --depth 1 && \
  cd insights && python setup.py install

ENTRYPOINT ["/usr/local/bin/intuition", "--showlog"]
CMD ["--help"]
