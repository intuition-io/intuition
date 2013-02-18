#!/usr/bin/env python

import time
import sys
import json
import argparse

parser = argparse.ArgumentParser(description = 'description')
parser.add_argument('-t', '--ticker', action='store', required=True)
parser.add_argument('-s', '--start', action='store', required=True)
args = parser.parse_args()

print('Args, ticker: {} and start: {}'.format(args.ticker, args.start))

print('Child: Starting process')
print('Args: {}'.format(sys.argv))
config_str = raw_input('> ')
print('Child: Received on stdin: {}'.format(config_str.strip()))
try:
    config = json.loads(config_str.strip())
except:
    print('Cannot read json configuration')
    sys.exit(1)
print('Logger level: {}'.format(config['log']))
print('MA configuration: {}'.format(config['ma']))

start = time.time()
elapse = 0
while elapse < 3:
    elapse = time.time() - start
print('Child: process finished to loop')
