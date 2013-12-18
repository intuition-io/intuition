#
# Copyright 2013 Xavier Bruhiere
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sys
import os

sys.path.append(os.environ['QTRADE'])
from intuition.core.finance import *

# For mathematical stuff, data manipulation...
from pandas import Index, DataFrame

import datetime

# Graphing stuff
import numpy as np
import matplotlib.colors as colors
import matplotlib.finance as finance
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager

#TODO: recarrayToDataframe structure !
# df = DataFrame(quotes) works !
# then, type(df.values) = numpy.ndarray


#TODO: a setProperty method which update the graph configuration dictionnary
class Graph(object):
    def __init__(self, bg='white'):
        plt.rc('axes', grid=True)
        plt.rc('grid', color='0.75', linestyle='-', linewidth=0.5)
        self.axes = list()
        self.fig = plt.figure(facecolor=bg)
        self.textsize = 9
        self.fillcolor = 'darkgoldenrod'

    def plot_candlestick(self, data, width=0.5, colorup='g', colordown='r'):
        finance.candlestick(self.axes[0], data, width=0.5, colorup='g', colordown='r')

    def register_mouse(self, callback, title='motion_notify_event'):
        return self.fig.canvas.mpl_connect(title, callback)

    def add_subplot(self, rect, color='#f6f6f6', sharex=None, copy=False, idx=None):
        if copy:
            self.axes.append(self.axes[idx].twinx())
        else:
            if sharex:
                self.axes.append(self.fig.add_axes(rect, axisbg=color))
            else:
                self.axes.append(self.fig.add_axes(rect, axisbg=color, sharex=sharex))
        return self.axes[-1]

    def add_volume(self, volume, idx=1):
        ax = self.add_subplot(None, copy=True, idx=idx)
        vmax = volume.max()
        #poly = ax.fill_between(quotes.date, volume, 0, label='Volume', facecolor=self.fillcolor, edgecolor=self.fillcolor)
        ax.set_ylim(0, 5 * vmax)
        ax.set_yticks([])

    def plot_RSI(self, quotes, rsi, idx):
        dates = quotes.date
        self.axes[idx].plot(dates, rsi, color=self.fillcolor)
        self.axes[idx].axhline(70, color=self.fillcolor)
        self.axes[idx].axhline(30, color=self.fillcolor)
        self.axes[idx].fill_between(dates, rsi, 70, where=(rsi >= 70), facecolor=self.fillcolor, edgecolor=self.fillcolor)
        self.axes[idx].fill_between(dates, rsi, 30, where=(rsi <= 30), facecolor=self.fillcolor, edgecolor=self.fillcolor)
        self.axes[idx].text(0.6, 0.9, '>70 = overbought', va='top', transform=self.axes[idx].transAxes, fontsize=self.textsize)
        self.axes[idx].text(0.6, 0.1, '<30 = oversold', transform=self.axes[idx].transAxes, fontsize=self.textsize)
        self.axes[idx].set_ylim(0, 100)
        self.axes[idx].set_yticks([30, 70])
        self.axes[idx].text(0.025, 0.95, 'RSI (14)', va='top', transform=self.axes[idx].transAxes, fontsize=self.textsize)
        self.axes[idx].set_title('RSI')

    def plot_2MA(self, quotes, ma20, ma200, idx):
        dx = quotes.adj_close - quotes.close
        low = quotes.low + dx
        high = quotes.high + dx

        deltas = np.zeros_like(quotes.adj_close)
        deltas[1:] = np.diff(quotes.adj_close)
        up = deltas > 0
        self.axes[idx].vlines(quotes.date[up], low[up], high[up], color='green', label='_nolegend_')
        self.axes[idx].vlines(quotes.date[~up], low[~up], high[~up], color='red', label='_nolegend_')
        linema20, = self.axes[idx].plot(quotes.date, ma20, color='blue', lw=2, label='MA (20)')
        linema200, = self.axes[idx].plot(quotes.date, ma200, color='red', lw=2, label='MA (200)')

        #last = quotes[-1]
        #s = '%s O:%1.2f H:%1.2f L:%1.2f C:%1.2f, V:%1.1fM Chg:%+1.2f' % (
            #datetime.date.today().strftime('%d-%b-%Y'),
            #last.open, last.high,
            #last.low, last.close,
            #last.volume * 1e-6,
            #last.close - last.open)

        #t4 = self.axes[idx].text(0.3, 0.9, s, transform=self.axes[idx].transAxes, fontsize=self.textsize)
        props = font_manager.FontProperties(size=10)
        leg = self.axes[idx].legend(loc='center left', shadow=True, fancybox=True, prop=props)
        leg.get_frame().set_alpha(0.5)

    def plot_MACD(self, quotes, macd, ema9, idx):
        self.axes[idx].plot(quotes.date, macd, color='black', lw=2)
        self.axes[idx].plot(quotes.date, ema9, color='blue', lw=1)
        self.axes[idx].fill_between(quotes.date, macd - ema9, 0, alpha=0.5, facecolor=self.fillcolor, edgecolor=self.fillcolor)
        #self.axes[idx].set_yticks([])

    def _DF_to_array(self, df):
        ''' Take a pandas dataframe and make it a numpy array, with floa dates '''

    def _clean_figure(self):
        # turn off upper axis tick labels, rotate the lower ones, etc
        for ax in self.axes:
            if ax != self.axes[-1]:
                for label in ax.get_xticklabels():
                    label.set_visible(False)
            else:
                for label in ax.get_xticklabels():
                    label.set_rotation(30)
                    label.set_horizontalalignment('right')

            ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')

    def draw(self):
        self._clean_figure()
        plt.show()


def on_move(event):
    ax = event.inaxes
    if ax is not None:
        # convert x y device coordinates to axes data coordinates
        date_ordinal, y = ax.transData.inverted().transform([event.x, event.y])

        # convert the numeric date into a datetime
        #date = num2date(date_ordinal)
        date = date_ordinal

        # sort the quotes by their distance (in time) from the mouse position
        def sorter(quote):
            return abs(quote[0] - date_ordinal)
        quotes.sort(key=sorter)

        print 'on date %s the nearest 3 openings were %s at %s respectively' % \
                        (date,
                         ', '.join([str(quote[1]) for quote in quotes[:3]]),
                         ', '.join([str(quote[0]) for quote in quotes[:3]]))
        plt.draw()


'''---------------------------------------------------------------------------------------
Usage Exemple
---------------------------------------------------------------------------------------'''


def get_data(ticker, startdate, enddate):
    fh = finance.fetch_historical_yahoo(ticker, startdate, enddate)
    quotes = mlab.csv2rec(fh)                       # or:
    #quotes = finance.parse_yahoo_historical(fh)    # or:
    #quotes = finance.quotes_historical_yahoo('INTC', startdate, today)
    quotes.sort()
    fh.close()
    if len(quotes) == 0:
        raise SystemExit
    return quotes

if __name__ == '__main__':
    ticker = 'SPY'
    startdate = datetime.date(2011, 1, 1)
    enddate = datetime.date.today()
    quotes = get_data(ticker, startdate, enddate)
    prices = quotes.adj_close

    g = Graph()
    #g.candlestickPlot(quotes, width=1)   #FIXME: needs float date (here datetime), date2num
    #g.registerMouse(onMove)
    ax = g.add_subplot([0.1, 0.7, 0.8, 0.2])  # ax1
    g.add_subplot([0.1, 0.3, 0.8, 0.4], sharex=ax)  # ax2
    g.add_subplot([0.1, 0.1, 0.8, 0.2], sharex=ax)  # ax3

    # RSI plot
    rsi = relative_strength(prices)
    g.plot_RSI(quotes, rsi, 0)

    # Plot MAs
    ma20 = moving_average(prices, 20, type='simple')
    ma200 = moving_average(prices, 200, type='simple')
    g.plot_2MA(quotes, ma20, ma200, 1)

    # Plot Quotes and volume
    #TODO: simple plot but if specified idx already exists, overlays it
    volume = (quotes.close * quotes.volume) / 1e6  # dollar volume in millions
    g.add_volume(volume, 1)

    # Compute the MACD indicator
    g.fillcolor = 'darkslategrey'
    nslow = 26
    nfast = 12
    nema = 9
    emaslow, emafast, macd = moving_average_convergence(prices, nslow=nslow, nfast=nfast)
    ema9 = moving_average(macd, nema, type='exponential')
    g.plot_MACD(quotes, macd, ema9, 2)
    g.axes[2].text(0.025, 0.95, 'MACD (%d, %d, %d)' % (nfast, nslow, nema), va='top',
            transform=g.axes[2].transAxes, fontsize=g.textsize)

    g.draw()
