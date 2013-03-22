#!/usr/bin/python

# Usage: "python quote.py NASDAQ:FB" scrapes data out of the upper-left
#         price box of http://www.google.com/finance?q=NASDAQ%3AFB
#
# Note: Only to be used for shorting IPOs!  https://fbme.disconnect.me/algorithm

import sys
import lxml.html
import urllib
import urllib2

symbol      = sys.argv[1]
url         = 'http://www.google.com/finance?q=%s' % urllib.quote(symbol)
page        = urllib2.urlopen(url).read()
root        = lxml.html.fromstring(page)
price_panel = root.cssselect('div#price-panel')[0]
raw = [v.text for v in price_panel.iterdescendants('span') if v.text and v.text.strip()]
result = {'price': raw[0],
        'change': raw[1],
        'change_perc': raw[2][1:-1]}

print result

print '\n'.join([v.text for v in price_panel.iterdescendants('span') if v.text and v.text.strip()])
