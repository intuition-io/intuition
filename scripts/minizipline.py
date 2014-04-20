#!/usr/bin/env python
# -*- coding: utf-8 -*-

# NOTE #######################################
# This file is deprecated but the minizipline is an interesting concept
# introduced by Mathieu Dous, worth to explore (although this is not a
# priority). That's why for the time being it remains here.
# ############################################

from neuronquant.algorithmic.strategies import MarkovGenerator
import csv


class MiniZipline(object):
    def __init__(self):

        self.data_source = './csv/INDEX_FCHI_MINI.csv'
        self.algo = MarkovGenerator({})

    def run(self):
        with open(self.data_source, 'rb') as source:
            table = csv.reader(source)
            for row in table:
                self.algo.handle_data(row)

        self.echo()

    def echo(self):
        '''
        Conlusion
        '''
        pass


main = MiniZipline()
main.run()
