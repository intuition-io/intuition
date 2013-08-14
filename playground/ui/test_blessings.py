import blessings

term = blessings.Terminal()
with term.location(2, 5):
    print 'Hello World'
    for x in xrange(10):
        print 'I can do it %i times' % x
