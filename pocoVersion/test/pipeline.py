#!/usr/bin/python
# -*- coding: utf8 -*-

import argparse
import json
import sys, os
import numpy

sys.path.append( '../pyTrade' )
from data.QuoteRetriever import QuoteDL
from data.RssRetriever import Rss
from compute.QuantSubSystem import Quantitative
from Utilities import LogSubSystem

def main():
    ''' Parsing command line args '''
    #TODO: the module allows many improvements
    parser = argparse.ArgumentParser(description='Spyder-quote, the terrific botnet')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.8.1 Licence GPLv3', help='Print program version')
    parser.add_argument('-f', '--file', action='store', default='',required=False, help='Config file path')
    parser.add_argument('-l', '--last', type=int, action='store', default=1,required=False, help='Last in days to retrieve informations')
    parser.add_argument('-p', '--precision', type=int, action='store', default=5,required=False, help='Precision in minutes for quotes download')
    parser.add_argument('-i', '--information', type=int, action='store', default=0,required=False, help='Level of information for Rss downloader')
    parser.add_argument('-b', '--database', action='store', default='assets.db' ,required=False, help='Database location')
    parser.add_argument('-t', '--target', action='store', required=True, help='target name to process')
    args = parser.parse_args()

    logSys = LogSubSystem('Downloader', 'info')
    log = logSys.getLog()

    if args.file == '': 
      ''' ugly way to keep json configuration compatibility '''
      try:
        if args.information == 0:
          description = "off"
          link = "off"
          update = "off"
        if args.information == 1:
          description = "on"
          link = "off"
          update = "off"
        if args.information == 2:
          description = "on"
          link = "on"
          update = "off"
        if args.information == 3:
          description = "on"
          link = "on"
          update = "on"
        jsonConfig = '{"assetsdb" : "%s", "days" : %d, "precision" : %d, "update" : "%s", "description" : "%s", "link" : "%s"}' \
            % ( args.database, args.last, args.precision, update, description, link )
        log.debug('JsonConfig: %s' % jsonConfig)
      except:
        log.exception('Incorrect argument')
        sys.exit(1)
      try:
        config = json.loads(jsonConfig)
      except:
        log.error('** Could not generate json configuration')
        sys.exit(2)
    else:
      ''' Parsing configuration file '''
      try:
        config = json.load(open(args.file, 'r'))
      except:
        log.exception('Can\'t load configuration file')
        sys.exit(1)


    ''' Execute financial stuff '''
    q = QuoteDL(args.target, config['assetsdb'])
    data = q.download(int(config['days']), int(config['precision']))
    q.updateDb()

    ''' Execute rss stuff '''
    log.info('Retrieving rss news from %s' % q.rss)
    channel = Rss(args.target, q.rss_source, q.rss)
    rval = channel.getFeeds(config['description'], config['link'], config['update'])
    #TODO: Does not handle above link, and description flag, in the meantime:
    if args.information == 3:
      log.info("Updating database")
      channel.updateDb(config['assetsdb'])
      #for i in range(0, len(channel.title)):
          #print '\t', channel.title[i], '-', channel.update[i]
          #print '\t', channel.description[i].strip()


    ''' Computation stuff '''
    log.info('Computational phase')
    compute = Quantitative(data) 
    compute.variation()



if __name__ == '__main__':
    main()

