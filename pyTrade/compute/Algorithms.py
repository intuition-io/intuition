import datetime
import pytz


from zipline.algorithm import TradingAlgorithm
from zipline.transforms import MovingAverage
from zipline.transforms import MovingVWAP
from zipline.transforms import  BatchTransform, batch_transform


class SimpleBuy(TradingAlgorithm):
    '''Simpliest algorithm ever, just buy a stock at the first frame'''
    def initialize(self, properties):
        self.count = 0
        # Otherwise, call the TradingAlgo __init__(capital_base=1000) himself
        #self.capital_base = properties.get('amount', 1000)
    

    def handle_data(self, data):
        if self.count == 0:
            #TODO Find or implement logging system
            print('Starting cach = {}'.format(self.portfolio.starting_cash))
            for ticker in data:
                stocks_n = round(self.amount / data[ticker].price)
                print('Buying {} {} stocks ({})'.format(stocks_n, ticker, data[ticker].price))
                self.order(ticker, stocks_n)

        if self.count == len(data):
            print self.portfolio
            for ticker in data:
                print('Selling {} {} stocks ({})'.format(\
                        self.portfolio.positions[ticker].amount, ticker, data[ticker].price))
                self.order(ticker, -self.portfolio.positions[ticker].amount)
        self.count += 1


class DualMovingAverage(TradingAlgorithm):
    """Dual Moving Average Crossover algorithm.

    This algorithm buys apple once its short moving average crosses
    its long moving average (indicating upwards momentum) and sells
    its shares once the averages cross again (indicating downwards
    momentum).

    """
    def initialize(self, **properties):
        short_window = properties.get('short_window', 200)
        long_window = properties.get('long_window', 400)
        self.amount = properties.get('amount', 10000)
        self.buy_on_event = properties.get('buy_on_event', 100)
        self.sell_on_event = properties.get('sell_on_event', 100)
        self.capital_base = properties.get('capital_base', 1000)

        print('Dual Moving average parameters parameters')
        print('Short: {}, long: {}, amount: {}'.format(short_window, long_window, self.amount))
        print('Buy number: {}, sell number: {}'.format(self.buy_on_event, self.sell_on_event))

        # Add 2 mavg transforms, one with a long window, one
        # with a short window.
        # Add a field in stock object: (function to apply, key in stock dict, keys in previous dict, parameters)
        self.add_transform(MovingAverage, 'short_mavg', ['price'],
                           window_length=short_window)

        self.add_transform(MovingAverage, 'long_mavg', ['price'],
                           window_length=long_window)

        # To keep track of whether we invested in the stock or not
        self.invested = False

        self.short_mavgs = []
        self.long_mavgs = []

    def handle_data(self, data):
        for ticker in data:
            short_mavg = data[ticker].short_mavg['price']
            long_mavg = data[ticker].long_mavg['price']
            if short_mavg > long_mavg and not self.invested:
                self.order(ticker, self.buy_on_event)
                self.invested = True
            elif short_mavg < long_mavg and self.invested:
                self.order(ticker, -self.sell_on_event)
                self.invested = False

        # Save mavgs for later analysis.
        self.short_mavgs.append(short_mavg)
        self.long_mavgs.append(long_mavg)

#https://www.quantopian.com/posts/updated-multi-sid-example-algorithm-1
class VolumeWeightAveragePrice(TradingAlgorithm):
    def initialize(self, properties):
        # Here we initialize each stock.  Note that we're not storing integers; by
        # calling sid(123) we're storing the Security object.
        self.vwap = {}
        self.price = {}
     
        # Setting our maximum position size, like previous example
        self.max_notional = 1000000.1
        self.min_notional = -1000000.0

        # initializing the time variables we use for logging
        utc = pytz.timezone('UTC')
        self.d=datetime.datetime(2008, 6, 20, 0, 0, 0, tzinfo=utc)

    def handle_data(self, data):
        # Initializing the position as zero at the start of each frame
        notional=0
        
        # This runs through each stock.  It computes
        # our position at the start of each frame.
        for stock in data:
            price = data[stock].price 
            notional = notional + self.portfolio.positions[stock].amount * price
            tradeday = data[stock].datetime
            
        # This runs through each stock again.  It finds the price and calculates
        # the volume-weighted average price.  If the price is moving quickly, and
        # we have not exceeded our position limits, it executes the order and
        # updates our position.
        for stock in data:   
            vwap = data[stock].vwap(3)
            price = data[stock].price  

            if price < vwap * 0.995 and notional > self.min_notional:
                order(stock,-100)
                notional = notional - price*100
            elif price > vwap * 1.005 and notional < self.max_notional:
                order(stock,+100)
                notional = notional + price*100

        # If this is the first trade of the day, it logs the notional.
        if (self.d + datetime.timedelta(days=1)) < tradeday:
            log.debug(str(notional) + ' - notional start ' + tradeday.strftime('%m/%d/%y'))
            self.d = tradeday

'''
https://www.quantopian.com/posts/batch-transform-testing-trailing-window-updated-minutely
#https://www.quantopian.com/posts/code-example-multi-security-batch-transform-moving-average
class MultiMA(TradingAlgorithm):
    # batch transform decorator settings
    R_P = 1 # refresh_period 
    W_L = 1 # window_length

    def initialize(self):  
        self.stocks = [sid(21090),sid(698),sid(6872),sid(4415),sid(6119),\
                sid(8229),sid(39778),sid(14328),sid(630),sid(4313)]

    def handle_data(self, data):  
        
        avgs = get_avg(data, self.stocks)    
        
        event_time = data[self.stocks[0]].datetime
        log.debug(event_time)
        log.debug(avgs)

    @batch_transform(refresh_period=R_P, window_length=W_L)  
    def get_avg(datapanel, sids):  
        avgs = np.zeros(len(sids))  
        for i, s in enumerate(sids):  
            avgs[i] = np.average(datapanel['price'][s].values)  
        return avgs  
'''

#https://www.quantopian.com/posts/this-is-amazing
class Momentum(TradingAlgorithm):
    def initialize(self):
        
        self.spy = sid(8554)
        
        self.max_notional = 200000.1
        self.min_notional = -200000.0

    def handle_data(self, data):

        sma = data[self.spy].mavg(3)

        price = data[self.spy].price
        
        notional = self.portfolio.positions[self.spy].amount * price
        
        cash = self.portfolio.cash
        
        capital_used = self.portfolio.capital_used
                  
        if sma >= price and notional > -0.2 * (capital_used + cash) :
            order(self.spy,-100)
        elif sma <= price and notional < 0.2 * (capital_used + cash):
            order(self.spy,+100)

#https://www.quantopian.com/posts/moving-average-crossover
class MovingAverageCrossover(TradingAlgorithm):
    def initialize(self):    
        #self.stock = sid(26578,24) WORKING
        self.stock = sid(26578)
        
        self.fast = []
        self.slow = []
        self.medium = []
        self.breakoutFilter = 0
        
        self.passedMediumLong = False
        self.passedMediumShort = False
        
        self.holdingLongPosition = False
        self.holdingShortPosition = False
        
        self.entryPrice = 0.0
                   
    def handle_data(data, self):    
        self.fast.append(data[self.stock].price)
        self.slow.append(data[self.stock].price)
        self.medium.append(data[self.stock].price)

        fastMovingAverage = 0.0
        mediumMovingAverage = 0.0
        slowMovingAverage = 0.0
        
        if len(self.fast) > 30:      
           self.fast.pop(0)
           fastMovingAverage = sum(self.fast)/len(self.fast)
            
        if len(self.medium) > 60 * 30:        
           self.medium.pop(0)
           mediumMovingAverage = sum(self.medium)/len(self.medium)        
            
        if len(self.slow) > 60 * 60:
           self.slow.pop(0)
           slowMovingAverage = sum(self.slow)/len(self.slow)   
           
                                   
        if ( (self.holdingLongPosition == False and self.holdingShortPosition == False) and 
                ((mediumMovingAverage > 0.0 and slowMovingAverage > 0.0)        
                 and (mediumMovingAverage > slowMovingAverage))):            
             self.passedMediumLong = True
                
                
        if ( (self.holdingLongPosition == False and self.holdingShortPosition == False)
                 and ((mediumMovingAverage > 0.0 and slowMovingAverage > 0.0)        
                 and (mediumMovingAverage < slowMovingAverage))):            
             self.passedMediumShort = True
                                           
        # Entry Strategies                               
        if (self.holdingLongPosition == False and self.holdingShortPosition == False 
                 and self.passedMediumLong == True
                 and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)        
                 and (fastMovingAverage > mediumMovingAverage))):     
            
             if self.breakoutFilter > 5:
                 log.info("ENTERING LONG POSITION")
                 order(self.stock, 100)   
                    
                 self.holdingLongPosition = True
                 self.breakoutFilter = 0                
                 self.entryPrice = data[self.stock].price        
             else:
                 self.breakoutFilter += 1        
                        
        if (self.holdingShortPosition == False and self.holdingLongPosition == False 
                 and self.passedMediumShort == True
                 and ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0)        
                 and (fastMovingAverage < mediumMovingAverage))):     
            
             if self.breakoutFilter > 5:
                 log.info("ENTERING SHORT POSITION")
                 order(self.stock, -100)  
                 self.holdingShortPosition = True
                 self.breakoutFilter = 0
                 self.entryPrice = data[self.stock].price           
             else:
                 self.breakoutFilter += 1      
                        
        # Exit Strategies                                            
        if (self.holdingLongPosition == True and 
                ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0) 
                 and (fastMovingAverage < mediumMovingAverage))):   
            
            if self.breakoutFilter > 5:
                order(self.stock, -100) 
                self.holdingLongPosition = False  
                self.breakoutFilter = 0
            else:
                self.breakoutFilter += 1
                            
        if (self.holdingShortPosition == True and 
                ((fastMovingAverage > 0.0 and slowMovingAverage > 0.0) 
                 and (fastMovingAverage > mediumMovingAverage))):           
            if self.breakoutFilter > 5:
                order(self.stock, 100)   
                self.holdingShortPosition = False  
                self.breakoutFilter = 0
            else:
                self.breakoutFilter += 1    

class Backtester(object):
    ''' Factory class wrapping zipline Backtester, returns the requested algo '''
    algos = {'DualMA': DualMovingAverage, 'Momentum': Momentum, \
            'VWAP': VolumeWeightAveragePrice, 'SimpleBuy': SimpleBuy}

    def __new__(self, algo, **kwargs):
        if algo not in Backtester.algos:
            raise NotImplementedError('Algorithm {} not available or implemented'.format(algo))
        print('[Debug] Algorithm {} available, getting a reference to it.'.format(algo))
        return Backtester.algos[algo](**kwargs)
