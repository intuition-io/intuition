var zerorpc = require("zerorpc");

var server = new zerorpc.Server({
    hello: function(name, reply) {
        reply(null, "Hello, " + name);
    },

    streaming_range: function(from, to, step, reply) {
        for(i=from; i<to; i+=step) {
            reply(null, i + step < to, true);
        }
        reply();
    }
});

server.bind("tcp://0.0.0.0:4242");
