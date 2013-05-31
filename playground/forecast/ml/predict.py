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


import rpy2.robjects as robjects
#from rpy2.robjects.packages import importr
import datetime
import pandas as pd
import pandas.rpy.common as com

from neuronquant.data.datafeed import DataFeed


r = robjects.r
svmforecast_lib = 'e1071.R'
r('source("%s")' % svmforecast_lib)
#quantmod = importr('quantmod')

symbol = 'GOOG'
history = 500
today = datetime.datetime.now()
start_date = today - pd.datetools.Day(history)

#r('require(quantmod)')
#tt = r('get( getSymbols("{}", from="{}"))'.format(symbol, start_date.strftime(format='%Y-%m-%d')))

returns = DataFeed().quotes(symbol, start_date=start_date, end_date=today)
#returns = data.pct_change().fillna(0.0)
returns = returns.rename(columns={symbol: "Close"})
r_quotes = com.convert_to_r_dataframe(returns)
import ipdb; ipdb.set_trace()
data_matrix = r('svmFeatures')(r_quotes)

#rets = r('na.trim( ROC(Cl({}), type="discrete"))'.format('tt'))

#data_matrix = r('svmFeatures')(tt)

#data_df = pd.rpy.common.convert_robj(data_matrix)
