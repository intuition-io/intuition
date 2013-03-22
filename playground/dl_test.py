#!/usr/bin/env python

import urllib2

try:
    import simplejson as json
except ImportError:
    import json
import logging

__author__ = "Steven Holmes"
__copyright__ = "Copyright 2012, Steven Holmes"
__license__ = "MIT"
__version__ = "1.0"

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s [%(levelname)s]: %'\
                                                '(message)s')
logger = logging.getLogger("PyStockQuotes")

class NoInstrumentSymbolException(Exception):
    def __init__(self):
        logger.error("No stock symbol provided.")

class PyStockQuotes(object):

    def get_instrument_data(self, url):
        """ Shortcut method for making a request to an URL with urllib2 """
        try:
            response = urllib2.urlopen(url)
            instrument_data = response.read()
            return instrument_data
        except urllib2.HTTPError, e:
            logger.error("HTTPError: %s, URL: %s " % (e.code, url))
        except urllib2.URLError, e:
            logger.error("URLError: %s, URL: %s " % (e.reason, url))

    def get_json(self, data):
        """ Shortcut method for simplejson.loads """
        return json.loads(data)

    def google_quote(self, *instruments):
        """Get stock quotes from Google Finance. Response is returned in JSON
        format"""

        if not instruments:
            raise NoInstrumentSymbolException()

        GOOGLE_FINANCE_JSON_URL = 'http://www.google.com/finance/info'
        #Allow multiple instruments in *args and make a comma-separated string
        # compatible URL
        instruments = ",".join(instrument for instrument in instruments)
        url = '%s?infotype=infoquoteall&q=%s' % (GOOGLE_FINANCE_JSON_URL,
                                                 instruments)
        instrument_data = self.get_instrument_data(url)
        #Google Finance API returns invalid JSON string, prepended with "// ".
        #Here we slice it off.
        cleaned_instrument_data = instrument_data[3:]
        return self.get_json(cleaned_instrument_data)

    def yahoo_quote(self, *instruments):
        """Get stock quotes from Yahoo Finance. Response is returned in JSON
        format"""

        if not instruments:
            raise NoInstrumentSymbolException()

        YAHOO_FINANCE_JSON_URL = 'http://query.yahooapis.com/v1/public/yql'
        instruments = "%22%2C%22".join(instrument for instrument in instruments)
        url = '%s?q=select%%20*%%20from%%20yahoo.finance.quotes%%20where%%20symbol%%20in%%20(%%22%s%%22)&format=json&diagnostics=false&env=store%%3A%%2F%%2Fdatatables.org%%2Falltableswithkeys' % (YAHOO_FINANCE_JSON_URL, instruments)
        instrument_data = self.get_instrument_data(url)
        return self.get_json(instrument_data)
