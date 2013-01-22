import rpy2.robjects as robj
from rpy2.robjects.packages import importr

vec = robj.r['pi']   # <=>
vec = robj.r('pi')
(vec + 2).r_repr()
''' R vector object, behaves as it
In [x]: vec + 2 
Out[X]: [3.14, 2]  # Still R vector
In [x]: vec[0] + 2 
Out[X]: 5.14       # Float'''

robj.r('''
        f <- function(r, verbose=FALSE) {
            if (verbose) {
                cat("I am calling f().\n")
            }
            2 * pi * r
        }
        f(3)
        ''')

# Accessing global defined variables and functions
r_f = robj.globalenv['f'] # Or even 
r_f = robj.r['f']
res = r_f(3, verbose=True)

# Interpolation
robj.r('paste({}, collapse="-")'.format(robj.r['letters'].r_repr()))

# Vectors
v = robj.FloatVector([1.2, 2.3, 56.0])  # Here <type> = Float
m = robj.r['matrix'](v, nrow=2)
print(m)

# Retrieving r functions
rsort = robj.t['sort']
rsort(robj.IntVector([1, 2, 3]), decreasing=True)

# Import packages
utils = importr('utils')
help_doc = utils.help('help')
str(help_doc)


''' --------------------------------    analysis.py    -- '''
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

r = robjects.r
r('source("global.R")')
analytics = importr('PerformanceAnalytics')

data = getData = r('getTradeData')()
print data.rx(1)  # Get the first line
print data.rx(1, 3)  # Get the first line and the third column (still a matrix, add [0])
print data.rx(1, 'bench_rets')  # Get the first line and the third column (still a matrix, add [0])
print data.rx(-1, 'bench_rets')  # Get the whole column and the third column (still a matrix, add [0])

analytics.chart_TimeSeries(data)
 print(analytics.table_Autocorrelation(algo_rets))


