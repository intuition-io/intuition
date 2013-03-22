from sys import argv
script, symbol = argv

import requests
import json


def get_stock_quote(ticker):
    r = requests.get('http://finance.google.com/finance/info?q=%s' % ticker)
    lines = r.text.splitlines()
    return json.loads(''.join([x for x in lines if x not in ('// [', ']')]))

import datetime
quote = get_stock_quote(symbol)
s = {"ticker" : quote['t'],
    "current price" : quote['l_cur'],
    "last trade" : quote['lt'],
    "change" : quote['c'],
    "accessed" : datetime.datetime.utcnow()}

print "Wrote %s to db at %s." % (quote['t'] , datetime.datetime.utcnow())
print s
