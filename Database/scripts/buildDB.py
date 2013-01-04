import sys, os

sys.path.append(str(os.environ['QTRADE']))
from pyTrade.data.QuantDB import QuantSQLite


if __name__ == '__main__':
    db = QuantSQLite('stocks.db')
    #print db.execute('select sqlite_version()')
    db.queryFromScript('scriptBuild.sql')
    db.close()
