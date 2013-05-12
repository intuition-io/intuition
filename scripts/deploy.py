#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2013 xavier <xavier@laptop-300E5A>
#
# Distributed under terms of the MIT license.

from IPython.parallel import Client, TimeoutError
from neuronquant.deathstar import trade, mega_configuration
import ipdb
import sys


try:
    c = Client()
except TimeoutError:
    print 'Coonection is down, run some engines along of controller'
    sys.exit(1)

assert len(c.ids) > 0

print '%d node(s) online' % len(c.ids)
node = c[0]

#with node.sync_imports():
    #from neuronquant.gears.engine import Simulation
    #import neuronquant.utils as utils

#ar = node.apply(trade, mega_configuration)
#print ar.result
ipdb.set_trace()
