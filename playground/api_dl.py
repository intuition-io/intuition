import urllib2
import json


# Form: http://digitalpbk.com/stock/google-finance-get-stock-quote-realtime
class GoogleFinanceAPI:
    def __init__(self):
        self.prefix = "http://finance.google.com/finance/info?client=ig&q="

    def get(self, symbol, exchange):
        url = self.prefix + "%s:%s" % (exchange, symbol)
        u = urllib2.urlopen(url)
        content = u.read()

        obj = json.loads(content[3:])
        return obj[0]


if __name__ == "__main__":
    c = GoogleFinanceAPI()

    quote = c.get("MSFT", "NASDAQ")
    print quote
