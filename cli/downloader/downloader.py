#!/usr/bin/python
# -*- coding: utf8 -*-

"""==================================================
 *  Filename: html_parser.py
 *  
 *  Description: Get an html page passed in command line, and parse it.
 *               Through it, url informations and links are stored.
 *
 *  Version: 0.9
 *  Created: 25/02/2012
 *  Compiler: python interpreter
 *
 *  Author: Xavier Bruhière
=================================================="""

import urllib2
import os
import sys
import re
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt
from ConfigParser import SafeConfigParser
#from PIL import Image

class Quote:
    ''' Quote object - fill everything related:
            name, code, current value, bought value,
            market, actions owned,
            and date, open, close, volume, of asked period'''
    def __init__(self, q_parser, quote, period, precision):
        self.quote = quote
        self.name = q_parser.get(quote, 'name')
        self.code = q_parser.get(quote, 'code')
        self.market = q_parser.get(quote, 'market')
        self.datum = {'date':0, 'open':0, 'close':0, 'volume':0}
        url = 'http://www.google.com/finance/getprices?q=' + self.code + '&x=' + self.market + '&p=' + str(period) + 'd&i=' + str(precision*61)
        try:
            self.data = urllib2.urlopen(url)
        except IOError:
            print '[!!] Bad url: %s' %url
            sys.exit(1)
        #header = self.data.info()

    def get_infos(self, save_quote):
        ''' analyse google finance data asked while initializing
        and store it '''
        cpt = 1
        feed = ''
        if ( save_quote ):
            save_f = './data/' + self.quote + '.data'
            save_fd = open(save_f, 'r+')
            save_fd.write('Date, Close, High, Low, Open, Volume\n')
        while (re.search('^a', feed) == None):
            feed = self.data.readline()
        while ( feed != '' ):
            infos = feed.split(',')
            date = time.strftime("%d/%b/%Y-%H:%M:%S", time.localtime(float(infos[0][1:])))    #see %c also and %m
            close = float(infos[1])
            high = float(infos[2])
            low = float(infos[3])
            first = float(infos[4])
            volume = int(infos[5])
            if ( save_quote ):
                save_fd.write(date + ' ' + str(close) + ' ' + str(high) + ' ' + str(low) + ' ' + str(first) + ' ' + str(volume) + '\n')
            if ( cpt == 1 ):
                #TODO true only if day=1
                self.datum['open'] = first
            feed = self.data.readline()
            cpt += 1
        self.datum['date'] = date
        self.datum['close'] = close
        self.datum['volume'] = volume

    def show_infos(self):
        ''' Plot data from file using R '''
        print self.quote
        os.system('R --slave --args ' + self.quote + ' < ./quantmod.R')
        #os.system('evince ./data/' + company + '.bmp &')
        #print '\t[' + self.datum['date'] + '] ' + self.name
        #print '\t\tOpen: ', self.datum['open']
        #print '\t\tClose: ', self.datum['close']
        #print '\t\tVolume: ', self.datum['volume']

    def treatment(self):
        ''' Compute some statistics treaments '''
        day_variation = (self.datum['close'] - self.datum['open'])/(0.01 * self.datum['open'])
        #total_variation = (self.datum['close'] - self.bought)/(0.01 * self.bought)
        return day_variation

    #def store_quote(self, stock, days, precision):
        #''' save portfolio data, a file for each week (month ?)
        #format: number, date, wallet, event, stock1, stock2, ... '''
        #q = Quote(stock, days, int(precision)) 
        #q.get_infos(True)
        


def main():
    ''' Main function '''
    parser = argparse.ArgumentParser(description='Spyder-quote, the terrific botnet', epilog='Done with help.')
    group_io = parser.add_argument_group('i/o')
    group_io.add_argument('-o', '--output', action='store', default=False, help='Conky or stdin output')
    #group_io.add_argument('-d', '--digit', action='store', default=1, help='Versatil use of a digit')
    #group_io.add_argument('-p', '--precision', action='store', default=5, help='Precision in minute between each quote value')
    args = parser.parse_args()

    q_parser = SafeConfigParser()
    q_parser.read('./data/quotes.ini')
    stocks_list = q_parser.get('general', 'stocks_list').split()
    digit = q_parser.get('general', 'days')
    precision = q_parser.get('general', 'precision')
    stocks = []
    i = 0

    if ( args.output == 'dl' ):
        for stock_name in stocks_list:
            stocks.append(Quote( q_parser, stock_name, int(digit), int(precision) ))
            stocks[i].get_infos(True)
            #stocks[i].show_infos()
            i += 1
    else:
        print 'Usage: ./portfolio.py -o <output>'

if __name__ == '__main__':
    main()

#TODO Use Google rss or others for company specifs news
#TODO Change get_infos place ?
#TODO Add control commands
#TODO Resolve data problem for 30 days 60minutes
