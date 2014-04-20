#! /bin/bash
#
# fetch-nasdaq-list.sh
# Copyright (C) 2013 Xavier Bruhiere
#
# Distributed under terms of the MIT license.


function usage {
  echo "usage : ${1} NASDAQ | NYSE | AMEX"
  exit 1
}


function download() {
  exchange=$1
  destination="${OUTPUT}/${exchange}.csv"

  wget -qO- ${destination} \
    "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=${exchange}&render=download"
}

[ $# -ne 1 ] && usage $0
[ -z ${OUTPUT} ] && export OUTPUT=$HOME/.intuition/data
download $1
