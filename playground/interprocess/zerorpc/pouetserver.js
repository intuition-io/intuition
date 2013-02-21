var zerorpc = require("zerorpc");

var server = new zerorpc.Server({
    addMan: function(sentence, reply) {
        reply(null, sentence + ", man!");
    },

    add42: function(n, reply) {
        reply(null, n + 42);
    },

    iter: function(from, to, step, reply) {
        for(i=from; i<to; i+=step) {
            reply(null, i, true);
        }

        reply();
    }
});

server.bind("tcp://0.0.0.0:4242");

server.on("error", function(error) {
    console.error("RPC server error:", error);
});
