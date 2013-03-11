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

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


#TODO Add type column, which will be action, index, obligation, ...?
class Symbol(Base):
    """
    Stock Symbols Table Model
    """
    __tablename__ = 'Symbols'

    Ticker = Column(String(10), primary_key=True)
    Name = Column(String(128))
    Exchange = Column(String(50))
    Sector = Column(String(50))
    Industry = Column(String(50))
    Quotes = relationship('Quote', cascade='all, delete, delete-orphan')

    def __init__(self, Ticker, Name, Exchange=None,
                 Sector=None, Industry=None):
        self.Ticker = Ticker
        self.Name = Name
        self.Exchange = Exchange
        self.Sector = Sector
        self.Industry = Industry

    def __repr__(self):
        return "<Symbol('%s','%s','%s','%s','%s')>" % (
            self.Ticker, self.Name, self.Exchange, self.Sector, self.Industry)


class Quote(Base):
    """
    Stock Quotes Table Model
    """
    __tablename__ = 'Quotes'

    Id       = Column(Integer, primary_key                      = True)
    Ticker   = Column(String(10), ForeignKey('Symbols.Ticker'))
    Date     = Column(Date)
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


class Metrics(Base):
    """
    Backtester monthly metrics
    """
    __tablename__ = 'Metrics'

    Id                  = Column(Integer, primary_key=True)
    Name                = Column(String(50))
    Period              = Column(Date)
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


'''
class Positions(Base):
    """
    Portfolio positions table model
    """
    __tablename__ = 'Positions'

    Id        = Column(Integer, primary_key = True)
    PortfolioName = Column(String(50), ForeignKey('Portfolio.Name'))
    Date      = Column(Date, ForeignKey('Portfolio.Date'))
    # Could be an other relationship to Symbol table
    Ticker = Column(String(10))
    Amount = Column(Integer)

    def __init__(self, name, date, ticker, amount):
        self.PortfolioName = name
        self.Date = date
        self.Ticker = ticker
        self.Amount = amount

    def __repr__(self):
        return "<Positions(Portfolio: %s, Date: %s, ticker: %s, amount: %d)>" % (
                self.PortfolioName, self.Date, self.Ticker, self.Amount)
'''


#TODO Positions table
#NOTE Giving a dico would solve order problem, and make generic save possible
class Portfolio(Base):
    """
    Portfolio tracker table Model
    """
    __tablename__ = 'Portfolio'

    Id             = Column(Integer, primary_key = True)
    Name           = Column(String(50))
    Date           = Column(Date)
    StartDate      = Column(String(50))
    Cash           = Column(Float)
    StartingCash   = Column(Float)
    Returns        = Column(Float)
    Capital        = Column(Float)
    PNL            = Column(Float)
    PortfolioValue = Column(Float)
    PositionsValue = Column(Float)
    #Positions      = relationship('Positions',
                                   #foreign_keys=[Positions.PortfolioName, Positions.Date],
                                   #uselist=False,
                                   #backref='Portfolio', lazy='lazy',
                                   #cascade='all, delete, delete-orphan',
                                   #order_by=Date)

    def __init__(self, **kwargs):
    #def __init__(self, name, date, startdate, cash, startingcash, returns, capital, pnl,
                 #portvalue, posvalue):
        self.Name = kwargs.get('name')
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
        return "<Portfolio(Id: %s, Date: %s, start date: %f, cash: %f, starting cash: %f, Returns: %f, capital: %f, \
                pnl: %f, portfolio value: %d, positions value: %f, Excess return: %f, : %f)>" % (
                self.Name, self.Date, self.StartDate, self.Cash, self.StartingCash, self.Returns, self.Capital, self.PNL,
                self.PortfolioValue, self.PositionsValue)
