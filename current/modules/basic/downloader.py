#!/usr/bin/python
# -*- coding: utf8 -*-

import argparse
import json
import finance
import rss

def main():
    ''' Parsing command line args '''
    parser = argparse.ArgumentParser(description='Spyder-quote, the terrific botnet')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s v0.8.1 Licence GPLv3', help='Print program version')
    parser.add_argument('-f', '--file', action='store', required=True, help='Config file path')
    parser.add_argument('-t', '--target', action='store', required=True, help='target name to process')
    args = parser.parse_args()

    ''' Parsing configuration file '''
    config = json.load(open(args.file, 'r'))

    ''' Execute financial stuff '''
    q = finance.Quote(args.target, config['assetsdb'])
    q.download(int(config['days']), int(config['precision']))
    q.updateDb()

    ''' Execute rss stuff '''
    print '[DEBUG] Retrieving rss news from', q.rss
    channel = rss.Rss(args.target, q.rss_source, q.rss)
    rval = channel.getFeeds(config['description'], config['link'], config['update'])
    channel.updateDb(config['assetsdb'])
    #for i in range(0, len(channel.title)):
        #print '\t', channel.title[i], '-', channel.update[i]
        #print '\t', channel.description[i].strip()



if __name__ == '__main__':
    main()

