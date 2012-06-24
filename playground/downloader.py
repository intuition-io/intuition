#!/usr/bin/python
# -*- coding: utf8 -*-

import argparse
import json
import finance

def main():
    ''' Parsing command line args '''
    parser = argparse.ArgumentParser(description='Spyder-quote, the terrific botnet')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.8.1 Licence GPLv3', help='Print program version')
    parser.add_argument('-f', '--file', action='store', required=True, help='Config file path')
    parser.add_argument('-d', '--database', action='store', required=True, help='Config file path')
    args = parser.parse_args()

    ''' Parsing configuration file '''
    config = json.load(open(args.file, 'r'))

    ''' Execute financial stuff '''
    # Initialisation
    q = finance.Quote(config['share']['name'], args.database)
    #q.checkDb(config['share']['days'])
    q.download(config['share']['days'], config['share']['precision'])
    q.updateDb()


if __name__ == '__main__':
    main()

