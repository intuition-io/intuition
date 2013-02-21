var zmq = require('zmq');

var config = {
    command: "run",
    script: "backtester/backtest.py",
    args: {
        ticker: {
            prefix: "--ticker",
            value: "random,1" 
        },
        algorithm: {
            prefix: "--algorithm",
            value: "Momentum" 
        },
        delta: {
            prefix: "--delta",
            value:      'D'
        },
        manager: {
            prefix: "--manager",
            value: "Constant" 
        },
        start: {
            prefix: "--start",
            value: "2005-01-10" 
        },
        end: {
            prefix: "--end",
            value: "2010-07-03" 
        } 
    },
    algorithm: {
        debug: 1,
        window_length: 30
    },
    manager: {
        max_weight: 0.5,
        buy_amount: 200, 
        sell_amount: 100
    },
    monitor: "notImplemented",
    done: true
};

var termination = {end: 'stop'};

// socket to talk to server
console.log("Connecting to hello world server...");
var requester = zmq.socket('req');

requester.on("message", function(reply) {
    console.log("Received reply: [", reply.toString(), ']');
    }
);

//requester.connect("tcp://localhost:5556");
requester.connect("tcp://localhost:5555");

console.log('Sending request...');
requester.send(JSON.stringify(config));
//requester.send(JSON.stringify(termination));

process.on('SIGINT', function() {
  requester.close();
});
