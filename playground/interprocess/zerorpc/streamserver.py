import zerorpc

class StreamingRPC(object):
    @zerorpc.stream
    def streaming_range(self, fr, to, step):
        return xrange(fr, to, step)

s = zerorpc.Server(StreamingRPC())
s.bind("tcp://0.0.0.0:4242")
s.run()
