#! /bin/bash
#
# fetch-nasdaq-list.sh
# Copyright (C) 2013 Xavier Bruhiere
#
# Distributed under terms of the MIT license.


function usage {
  program=$1
  echo "usage : ${program} NASDAQ | NYSE | AMEX"
  exit 1
}


function download() {
  exchange=$1
  output="${QTRADE}/data/${exchange}.csv"

  wget -q -O ${output} \
    "http://www.nasdaq.com/screening/companies-by-industry.aspx?exchange=${exchange}&render=download"
}

[ $# -ne 1 ] && usage $0
[ -z ${QTRADE} ] && export QTRADE=/tmp
download $1
