# -*- coding: utf-8 -*-

import timeit

method = ('d = {}', 'd = dict()')

t = (timeit.Timer(method[0]), timeit.Timer(method[1]))

elapsed = (min(t[0].repeat(100)), min(t[1].repeat(100)))


for i in range(2):
    print '%s executed in %.4fs' % (method[i], elapsed[i])

print 'Ratio: %.4f' % (max(elapsed) / min(elapsed))
