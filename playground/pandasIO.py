from pandas import ols, DataFrame
from pandas.stats.moments import rolling_std
from pandas.io.data import DataReader
import datetime

sp500 = DataReader("^GSPC", "yahoo", start=datetime.datetime(1990, 1, 1))
print(sp500.head())
sp500_returns = sp500["Adj Close"].shift(-250)/sp500["Adj Close"] - 1

gdp = DataReader("GDP", "fred", start=datetime.datetime(1990, 1, 1))['VALUE']
print(type(gdp))
gdp_returns = (gdp/gdp.shift(1) - 1) 
gdp_std = rolling_std(gdp_returns, 10)
gdp_standard = gdp_returns / gdp_std

gdp_on_sp = ols(y=sp500_returns, x=DataFrame({"gdp": gdp_standard}))
