#
# Copyright 2012 Xavier Bruhiere
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

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


#TODO Add type column, which will be action, index, obligation, ...?
class Equity(Base):
    """
    Equity informations Table Model
    """
    __tablename__ = 'Equities'

    Ticker   = Column(String(10), primary_key = True)
    Name     = Column(String(128))
    Exchange = Column(String(50))
    Index    = Column(String(128))
    Sector   = Column(String(50))
    Industry = Column(String(50))
    Quotes   = relationship('Quote', cascade  = 'all, delete, delete-orphan')

    def __init__(self, Ticker, Name, Exchange=None, Index=None,
                 Sector=None, Industry=None):
        self.Ticker   = Ticker
        self.Name     = Name
        self.Exchange = Exchange
        self.Index    = Index
        self.Sector   = Sector
        self.Industry = Industry

    def __repr__(self):
        return "<Equity('%s','%s','%s', '%s','%s','%s')>" % (
            self.Ticker, self.Name, self.Exchange, self.Index, self.Sector, self.Industry)


#TODO Relastionship with Quotes
class Index(Base):
    '''
    Index information table
    '''
    __tablename__ = 'Indices'

    Ticker   = Column(String(10), primary_key = True)
    Name     = Column(String(128))
    Exchange = Column(String(50))
    Timezone = Column(String(50))
    Quotes   = relationship('IdxQuote', cascade='all, delete, delete-orphan')
    #Quotes   = relationship('Quote', 
                    #primaryjoin=
                    #'Indices.Ticker==Quotes.Ticker', foreign_keys=['Quotes.Ticker'])

    #NOTE Test of necessary values along with kwargs joker flexibility
    def __init__(self, ticker, **kwargs):
        self.Ticker   = ticker
        self.Name     = kwargs.get('name')
        self.Exchange = kwargs.get('exchange')
        self.Timezone = kwargs.get('timezone')

    def __repr__(self):
        return '<Index(Ticker: %s, name: %s, exchange: %s, timezone: %s)>' % (
                self.Ticker, self.Name, self.Exchange, self.Timezone)


class CurrencyPair(Base):
    '''
    Forex assets table model
    '''
    __tablename__ = 'Forex'

    Id   = Column(Integer, primary_key = True)
    Date = Column(DateTime)
    Pair = Column(String(12))
    Bid  = Column(Float)
    Ask  = Column(Float)
    High = Column(Float)
    Low  = Column(Float)

    def __init__(self, pair, **kwargs):
        self.Date = kwargs.get('date')
        self.Pair = pair
        self.Bid = kwargs.get('bid')
        self.Ask = kwargs.get('ask')
        self.High = kwargs.get('high')
        self.Low = kwargs.get('low')

    def __repr__(self):
        return '<CurrencyPair(date: %s, pair: %s, bid: %f, ask: %f, high: %f, low: %f)' % (
                self.Date, self.Pair, self.Bid, self.Ask, self.High, self.Low)


class Quote(Base):
    """
    Stock Quotes Table Model
    """
    __tablename__ = 'Quotes'

    Id       = Column(Integer, primary_key=True)
    Ticker   = Column(String(10), ForeignKey('Equities.Ticker'))
    Date     = Column(DateTime)
    Open     = Column(Float)
    High     = Column(Float)
    Low      = Column(Float)
    Close    = Column(Float)
    Volume   = Column(Float)
    AdjClose = Column(Float)

    def __init__(self, Ticker, Date, Open, High, Low, Close, Volume, AdjClose):
        self.Ticker   = Ticker
        self.Date     = Date
        self.Open     = Open
        self.High     = High
        self.Low      = Low
        self.Close    = Close
        self.Volume   = Volume
        self.AdjClose = AdjClose

    def __repr__(self):
        return "<Quote(Date: %s,Symbol: %s, Open: %f, High: %f, Low: %f, \
                Close: %f, Volume: %d, Adjusted Close: %f)>" % (self.Date,
                self.Ticker, self.Open, self.High, self.Low, self.Close,
                self.Volume, self.AdjClose)


#TODO Shared child table
class IdxQuote(Base):
    """
    Stock IdxQuotes Table Model
    """
    __tablename__ = 'IdxQuotes'

    Id       = Column(Integer, primary_key=True)
    Ticker   = Column(String(10), ForeignKey('Indices.Ticker'))
    Date     = Column(DateTime)
    Open     = Column(Float)
    High     = Column(Float)
    Low      = Column(Float)
    Close    = Column(Float)
    Volume   = Column(Float)
    AdjClose = Column(Float)

    def __init__(self, Ticker, Date, Open, High, Low, Close, Volume, AdjClose):
        self.Ticker   = Ticker
        self.Date     = Date
        self.Open     = Open
        self.High     = High
        self.Low      = Low
        self.Close    = Close
        self.Volume   = Volume
        self.AdjClose = AdjClose

    def __repr__(self):
        return "<Quote(Date: %s,Symbol: %s, Open: %f, High: %f, Low: %f, \
                Close: %f, Volume: %d, Adjusted Close: %f)>" % (self.Date,
                self.Ticker, self.Open, self.High, self.Low, self.Close,
                self.Volume, self.AdjClose)


#NOTE Performacnes should be linked to Metrics ?
class Metrics(Base):
    """
    Backtester monthly metrics
    """
    __tablename__ = 'Metrics'

    Id                  = Column(Integer, primary_key=True)
    Name                = Column(String(50))
    Period              = Column(DateTime)
    SharpeRatio         = Column(Float)
    SortinoRatio        = Column(Float)
    Information         = Column(Float)
    Returns             = Column(Float)
    MaxDrawdown         = Column(Float)
    Volatility          = Column(Float)
    Beta                = Column(Float)
    Alpha               = Column(Float)
    ExcessReturn        = Column(Float)
    BenchmarkReturns    = Column(Float)
    BenchmarkVolatility = Column(Float)
    TreasuryReturns     = Column(Float)

    def __init__(self, name, period, sharpe, sortino, info, returns, maxdrawdown, volatility,
                 beta, alpha, excessreturn, benchmarkreturns, benchmarkvolatility, treasuryreturns):
        self.Name                = name
        self.Period              = period
        self.SharpeRatio         = sharpe
        self.SortinoRatio        = sortino
        self.Information         = info
        self.Returns             = returns
        self.MaxDrawdown         = maxdrawdown
        self.Volatility          = volatility
        self.Beta                = beta
        self.Alpha               = alpha
        self.ExcessReturn        = excessreturn
        self.BenchmarkReturns    = benchmarkreturns
        self.BenchmarkVolatility = benchmarkvolatility
        self.TreasuryReturns     = treasuryreturns

    def __repr__(self):
        return "<Metrics(Id: %s, Date: %s, Sharpe ratio: %f, Sortino ratio: %f, Information: %f, Returns: %f, Max Drawdown: %f, \
                volatility: %f, beta: %d, alpha: %f, Excess return: %f, Benchmark Return: %f,\
                Benchmark volatility: %f, Treasury return: %f)>" % (
                self.Name, self.Period, self.SharpeRatio, self.SortinoRatio, self.Information, self.Returns, self.MaxDrawdown, self.Volatility,
                self.Beta, self.Alpha, self.ExcessReturn, self.BenchmarkReturns, self.BenchmarkVolatility, self.TreasuryReturns)


#NOTE Could link to Metrics
class Performances(Base):
    """
    Backtester metrics Table Model
    """
    __tablename__ = 'Performances'

    Name                = Column(String(50), primary_key = True)
    SharpeRatio         = Column(Float)
    Returns             = Column(Float)
    MaxDrawdown         = Column(Float)
    Volatility          = Column(Float)
    Beta                = Column(Float)
    Alpha               = Column(Float)
    BenchmarkReturns    = Column(Float)

    def __init__(self, name, sharpe, returns, maxdrawdown, volatility, beta, alpha, benchmarkreturns):
        self.Name                = name
        self.SharpeRatio         = sharpe
        self.Returns             = returns
        self.MaxDrawdown         = maxdrawdown
        self.Volatility          = volatility
        self.Beta                = beta
        self.Alpha               = alpha
        self.BenchmarkReturns    = benchmarkreturns

    def __repr__(self):
        return "<Performances(Id: %s, Sharpe ratio: %f, Returns: %f, Max Drawdown: %f, \
                volatility: %f, beta: %d, alpha: %f, Benchmark Return: %f)>"\
                % (self.Name, self.SharpeRatio, self.Returns, self.MaxDrawdown, self.Volatility,
                self.Beta, self.Alpha, self.BenchmarkReturns)


class Portfolio(Base):
    """
    Portfolio tracker table Model
    """
    __tablename__ = 'Portfolios'

    Name           = Column(String(50), primary_key=True)
    Date           = Column(DateTime)
    #NOTE use date ?
    StartDate      = Column(String(50))
    Cash           = Column(Float)
    StartingCash   = Column(Float)
    Returns        = Column(Float)
    Capital        = Column(Float)
    PNL            = Column(Float)
    PortfolioValue = Column(Float)
    PositionsValue = Column(Float)
    Positions      = relationship('Position', backref='Portfolios')

    def __init__(self, **kwargs):
        self.Name           = kwargs.get('name')
        self.Date           = kwargs.get('date')
        self.StartDate      = kwargs.get('startdate')
        self.Cash           = kwargs.get('cash')
        self.StartingCash   = kwargs.get('startingcash')
        self.Returns        = kwargs.get('returns')
        self.Capital        = kwargs.get('capital')
        self.PNL            = kwargs.get('pnl')
        self.PortfolioValue = kwargs.get('portvalue')
        self.PositionsValue = kwargs.get('posvalue')

    def __repr__(self):
        return "<Portfolio(Id: %s, Date: %s, start date: %s, cash: %f, starting cash: %f, Returns: %f, capital: %f, \
                pnl: %f, portfolio value: %f, positions value: %f)>" % (
                self.Name, self.Date, self.StartDate, self.Cash, self.StartingCash, self.Returns, self.Capital, self.PNL,
                self.PortfolioValue, self.PositionsValue)


class Position(Base):
    """
    Portfolio positions table model
    """
    __tablename__ = 'Positions'

    Id        = Column(Integer, primary_key = True)
    PortfolioName = Column(String(50), ForeignKey('Portfolios.Name'))
    #NOTE Could be an other relationship to Symbol table
    Ticker = Column(String(10))
    Amount = Column(Integer)
    LastSalePrice = Column(Float)
    CostBasis = Column(Float)

    def __init__(self, **kwargs):
        self.PortfolioName = kwargs.get('name')
        self.Ticker = kwargs.get('sid')
        self.Amount = kwargs.get('amount')
        self.LastSalePrice = kwargs.get('last_sale_price')
        self.CostBasis = kwargs.get('cost_basis')

    def __repr__(self):
        return "<Positions(Portfolio: %s, ticker: %s, amount: %d, price: %f, cost basis: %f)>" % (
                self.PortfolioName, self.Ticker, self.Amount, self.LastSalePrice, self.CostBasis)
