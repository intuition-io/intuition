'''
QuanTrade
'''

__author__    = 'Xavier Bruhiere'
__copyright__ = 'Xavier Bruhiere'
__licence__   = 'Apache 2.0'
__version__   = '0.4'

import algorithmic
import gears
import data
import utils
import os

os.system('. $HOME/.quantrade/local.sh')

__all__ = [
        'algorithmic',
        'gears',
        'data',
        'utils'
]
