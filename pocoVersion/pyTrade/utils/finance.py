from collections import namedtuple
from decorators import *

class Stock(namedtuple('Stock', 'name value variation volume dataframe')):
    """A stock class example to learn and reuse"""
    __slots__ = ()

    @property
    def isGood(self):
        ''' check % variation of stock '''
        if self.variation < 5:
            return False
        else:
            return True

    def __str__(self):
        ''' for print(stock) '''
        if self.isGood:
            return '%s is good: %f' % (self.name, self.variation)
        else:
            return '%s is bad: %f' % (self.name, self.variation)

    @perf
    def compute(self, value):
        ''' An example of perf decorator use '''
        return value*2000000000 / 2000000000

    @deprecated
    def priceInFranc(self, price):
        print('{0} cost {1}F').fomart(self.name, price)

        
''' Usage 
archos = Stock('archos', {'today' : 3.45, 'yest' : 2.45}, 2.8, 2345, None)
print(archos)
ret, perf = archos.compute(archos.volume)
print('{0} computed in {1}s').format(ret, perf)
#ret = archos.priceInFranc(archos.value['today'])
'''



#Note: DataSubSystem as a singleton ?

# CSV and SQLite wrapper -------------------------------------------------------
#import csv
#for emp in map(EmployeeRecord._make, csv.reader(open("employees.csv", "rb"))):
    #print emp.name, emp.title

#import sqlite3
#conn = sqlite3.connect('/companydata')
#cursor = conn.cursor()
#cursor.execute('SELECT name, age, title, department, paygrade FROM employees')
#for emp in map(EmployeeRecord._make, cursor.fetchall()):
    #print emp.name, emp.title
