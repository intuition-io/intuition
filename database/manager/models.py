#!/usr/bin/env python

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, backref
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


class Indicator(Base):
    """
    Financial Indicator table model
    """
    __tablename__ = 'Indicators'

    Id = Column(Integer, ForeignKey('Quotes.Id'), primary_key=True)

    # --------------------------------------------
    # Averages
    # --------------------------------------------

    # Moving Averages
    ma_5_day = Column(Float)
    ma_10_day = Column(Float)
    ma_20_day = Column(Float)
    ma_50_day = Column(Float)
    ma_100_day = Column(Float)
    ma_200_day = Column(Float)

    # Exponentially Weighted Moving Averages
    ewma_5_day = Column(Float)
    ewma_10_day = Column(Float)
    ewma_12_day = Column(Float)
    ewma_20_day = Column(Float)
    ewma_26_day = Column(Float)
    ewma_50_day= Column(Float)
    ewma_100_day = Column(Float)
    ewma_200_day = Column(Float)


    # --------------------------------------------
    # Difference from Averages
    # --------------------------------------------

    #Difference from Moving Averages
    diff_ma_5_day = Column(Float)
    diff_ma_10_day = Column(Float)
    diff_ma_20_day = Column(Float)
    diff_ma_50_day = Column(Float)
    diff_ma_100_day = Column(Float)
    diff_ma_200_day = Column(Float)

    # Difference from EWMA
    diff_ewma_5_day = Column(Float)
    diff_ewma_10_day = Column(Float)
    diff_ewma_12_day = Column(Float)
    diff_ewma_20_day = Column(Float)
    diff_ewma_26_day = Column(Float)
    diff_ewma_50_day = Column(Float)
    diff_ewma_100_day = Column(Float)
    diff_ewma_200_day = Column(Float)

    # Percent Difference from Moving Averages
    pct_diff_ma_5_day = Column(Float)
    pct_diff_ma_10_day = Column(Float)
    pct_diff_ma_20_day = Column(Float)
    pct_diff_ma_50_day = Column(Float)
    pct_diff_ma_100_day = Column(Float)
    pct_diff_ma_200_day = Column(Float)

    # Percent Difference from EWMA
    pct_diff_ewma_5_day = Column(Float)
    pct_diff_ewma_10_day = Column(Float)
    pct_diff_ewma_12_day = Column(Float)
    pct_diff_ewma_20_day = Column(Float)
    pct_diff_ewma_26_day = Column(Float)
    pct_diff_ewma_50_day = Column(Float)
    pct_diff_ewma_100_day = Column(Float)
    pct_diff_ewma_200_day = Column(Float)

    # --------------------------------------------
    # Moving stats
    # --------------------------------------------

    # Percent change
    pct_change = Column(Float)

    # Standard Deviation
    moving_stdev_5_day = Column(Float)
    moving_stdev_10_day = Column(Float)
    moving_stdev_20_day = Column(Float)
    moving_stdev_50_day = Column(Float)
    moving_stdev_100_day = Column(Float)
    moving_stdev_200_day = Column(Float)

    # Variance
    moving_var_5_day = Column(Float)
    moving_var_10_day = Column(Float)
    moving_var_20_day = Column(Float)
    moving_var_50_day = Column(Float)
    moving_var_100_day = Column(Float)
    moving_var_200_day = Column(Float)


    # --------------------------------------------
    # General Momentum Indicators
    # --------------------------------------------

    # Momentum
    momentum_5_day = Column(Float)
    momentum_10_day = Column(Float)
    momentum_20_day = Column(Float)
    momentum_50_day = Column(Float)
    momentum_100_day = Column(Float)
    momentum_200_day = Column(Float)

    # Rate Of Change
    roc_5_day = Column(Float)
    roc_10_day = Column(Float)
    roc_20_day = Column(Float)
    roc_50_day = Column(Float)
    roc_100_day = Column(Float)
    roc_200_day = Column(Float)

    # Velocity
    #velocity_5_day = Column(Float)
    #velocity_10_day = Column(Float)
    #velocity_20_day = Column(Float)
    #velocity_50_day = Column(Float)
    #velocity_100_day = Column(Float)
    #velocity_200_day = Column(Float)

    # Acceleration
    #acceleration_5_day = Column(Float)
    #acceleration_10_day = Column(Float)
    #acceleration_20_day = Column(Float)
    #acceleration_50_day = Column(Float)
    #acceleration_100_day = Column(Float)
    #acceleration_200_day = Column(Float)

    # MACD
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)

    def __init__(self, Id, ma_5_day=None, ewma_5_day=None):
        self.Id = Id
        self.ma_5_day = ma_5_day
        self.ewma_5_day = ewma_5_day


