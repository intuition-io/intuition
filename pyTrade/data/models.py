#!/usr/bin/env python

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
#, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Symbol(Base):
    """
    Stock Symbols Table Model
    """
    __tablename__ = 'Symbols'

    Ticker = Column(String(5), primary_key=True)
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

    Id = Column(Integer, primary_key=True)
    Ticker = Column(String(5), ForeignKey('Symbols.Ticker'))
    Date = Column(Date)
    Open = Column(Float)
    High = Column(Float)
    Low = Column(Float)
    Close = Column(Float)
    Volume = Column(Float)
    AdjClose = Column(Float)
    #Features = relationship('Indicator', uselist=False,
                            #backref='Quotes', lazy='lazy',
                            #cascade='all, delete, delete-orphan',
                            #order_by=Date)

    def __init__(self, Ticker, Date, Open, High, Low, Close, Volume, AdjClose):
        self.Ticker = Ticker
        self.Date = Date
        self.Open = Open
        self.High = High
        self.Low = Low
        self.Close = Close
        self.Volume = Volume
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
    Returns             = Column(Float)
    MaxDrawdown         = Column(Float)
    Volatility          = Column(Float)
    Beta                = Column(Float)
    Alpha               = Column(Float)
    ExcessReturn        = Column(Float)
    BenchmarkReturns    = Column(Float)
    BenchmarkVolatility = Column(Float)
    TreasuryReturns     = Column(Float)

    def __init__(self, name, period, sharpe, returns, maxdrawdown, volatility, beta, alpha, excessreturn,
                  benchmarkreturns, benchmarkvolatility, treasuryreturns):
        self.Name                = name
        self.Period              = period
        self.SharpeRatio         = sharpe
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
        return "<Quote(Id: %s, Date: %s, Sharpe ratio: %f, Returns: %f, Max Drawdown: %f, \
                volatility: %f, beta: %d, alpha: %f, Excess return: %f, Benchmark Return: %f,\
                Benchmark volatility: %f, Treasury return: %f)>" % (
                self.Name, self.Period, self.SharpeRatio, self.Returns, self.MaxDrawdown, self.Volatility,
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
        return "<Quote(ID: %s, Sharpe ratio: %f, Returns: %f, Max Drawdown: %f, \
                volatility: %f, beta: %d, alpha: %f, Benchmark Return: %f)>"\
                % (self.Name, self.SharpeRatio, self.Returns, self.MaxDrawdown, self.Volatility,
                self.Beta, self.Alpha, self.BenchmarkReturns)
