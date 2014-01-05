'''
Intuition
'''

import os

__author__ = 'Xavier Bruhiere'
__copyright__ = 'Xavier Bruhiere'
__licence__ = 'Apache 2.0'
__version__ = '0.2.9'

default_config = {'algorithm': {}, 'manager': {}}
modules_path = os.environ.get('MODULES_PATH', 'insights')
print('loading modules from {}'.format(modules_path))
print('setting default config to {}'.format(default_config))
