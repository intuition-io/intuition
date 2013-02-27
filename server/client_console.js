#!/usr/bin/env node

//http://tjholowaychuk.com/post/9103188408/commander-js-nodejs-command-line-interfaces-made-easy
//https://github.com/LearnBoost/cli-table
//https://github.com/substack/node-multimeter
//https://github.com/baryon/tracer
//https://github.com/LearnBoost/console-trace
//https://github.com/LearnBoost/distribute
//https://github.com/LearnBoost/knox
//https://github.com/LearnBoost/engine.io-client

var argv = require('optimist')
            .usage('Usage: $0 --verbose [int] --log')
            .demand(['verbose'])
            .default({ verbose : 2 })
            .alias('v', 'verbose')
            .describe('verbose', 'verbose level')
            .argv;

var bt_config = {
    type: "fork",
    script: "backtester/backtest.py",
    port: 5555,
    args: {
        ticker: {
            prefix: "--ticker",
            value: "google,apple" 
        },
        algorithm: {
            prefix: "--algorithm",
            value: "Momentum" 
        },
        delta: {
            prefix: "--delta",
            value:      '1min'
        },
        manager: {
            prefix: "--manager",
            value: "Constant" 
        },
        start: {
            prefix: "--start",
            value: "2006-01-10" 
        },
        end: {
            prefix: "--end",
            value: "2008-07-03" 
        } ,
        mode: {
            prefix: "flag",
            value: "--remote"
        } 
    },
    configuraton: {
        algorithm: {
            debug: 1,
            window_length: 30
        },
        manager: {
            max_weight: 0.5,
            buy_amount: 200, 
            sell_amount: 100
        }
    },
    monitor: "notImplemented",
};

var opt_config = {
    type: "fork",
    script: "backtester/optimization/evolve_algo.py",
    args: {
        population: {
            prefix: "--popsize",
            value: 5
        },
        elitism: {
            prefix: "--elitism",
            value: 0.2
        },
        step: {
            prefix: "--step",
            value: 2
        },
        iteration: {
            prefix: "--iteration",
            value: 5
        },
        mutation: {
            prefix: "--mutation",
            value: 0.5
        }
        //},
        //notify: {
            //prefix: "flag",
            //value: "--notify"
        //}
    }
}

var fd_config = {
    type: "configure",
    filters: ["portfolio", "acknowledgment", "optimization"],
    level: argv.verbose
};

var zmq = require('zmq')
    , broker_uri = 'tcp://127.0.0.1:5555'
    , logger_uri = 'tcp://127.0.0.1:5540';
    
function createClient (port, channel) {
    var socket = zmq.socket('dealer');

    socket.identity = channel

    socket.on('message', function(data) {
        json_data = JSON.parse(data);
        if (channel == 'ZMQ Messaging') {
            console.log(json_data.time + ' ' + json_data.func_name + ': ' + json_data.msg +' (' + json_data.level + ')');
            //console.log(data.toString())
        }
        if (json_data.type == 'portfolio') {
            console.log(json_data.time + ' Portfolio:', json_data.msg['value']);
        }
        else if (json_data.type == 'acknowledgment') {
            console.log(json_data.time + 'Worker returned: ' + json_data.msg);
            socket.send(JSON.stringify({statut: 0}));
        }
        else if (json_data.type == 'optimization') {
            console.log(json_data.msg['iteration'] + ' ' + json_data.msg['progress'] + '% | ' + json_data.msg['best'] + ' (' + json_data.msg['mean'] +')');
        }
    });

    socket.connect(port);
    console.log('[Node:Client] ' + socket.identity + ' connected');

    if (channel == 'dashboard') {
        // Configure forwarder
        socket.send(JSON.stringify(fd_config));

        // Request to run backtester with this config
        socket.send(JSON.stringify(opt_config));
    }
}    

if (argv.log) {
    createClient(logger_uri, 'ZMQ Messaging');
}
createClient(broker_uri, 'dashboard');
