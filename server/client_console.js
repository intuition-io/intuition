#!/usr/bin/env node

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
            value: "DualMA" 
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
    configuration: {
        algorithm: {
            debug: 1,
            window_length: 30
        },
        manager: {
            max_weight: 0.5,
            connected: 1,
            buy_amount: 200, 
            sell_amount: 100
        }
    },
    monitor: "notImplemented",
};

var opt_config = {
    type: "fork",
    script: "backtester/optimization/genetic_function.py",
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
    log_redirection: "dashboard",
    verbose: argv.verbose
};

var zmq = require('zmq')
    , ui = require('client_ui')
    , broker_uri = 'tcp://127.0.0.1:5555'
    , logger_uri = 'tcp://127.0.0.1:5540';
    
function createClient (port, channel) {
    client_ui.write_log('Log window setup done.');
    client_ui.write_msg('Message window setup done.');

    var socket = zmq.socket('dealer');

    socket.identity = channel;

    socket.on('message', function(data) {
        json_data = JSON.parse(data);
        if (json_data.type == 'portfolio') {
            client_ui.write_msg(json_data.time + ' Portfolio:', json_data.msg['value']);
        }
        else if (json_data.type == 'acknowledgment') {
            client_ui.write_msg(json_data.time + 'Worker returned: ' + json_data.msg);
            socket.send(JSON.stringify({type: 'acknowledgment', statut: 0}));
        }
        else if (json_data.type == 'optimization') {
            client_ui.write_msg(json_data.msg['iteration'] + ' ' + json_data.msg['progress'] + '% | ' + json_data.msg['best'] + ' (' + json_data.msg['mean'] +')');
        }
        else {
            //NOTE Should be dedicated to unexpected message, for now it's for logging
            //NOTE could configure a channel_log_filter in addition to the type filter, or merge them
            //NOTE msg can be json object, detect and parse it
            client_ui.write_log(json_data.time + ' ' + json_data.func_name + ': ' + json_data.msg +' (' + json_data.level + ')');
        }
    });

    socket.connect(port);
    client_ui.write_msg('[Node:Client] ' + socket.identity + ' connected');

    this.send_json = function(msg) {
        socket.send(JSON.stringify(msg));
    }
}    


var client_ui = new ui.UI_interface(test);  

var client_be = new createClient(broker_uri, 'dashboard');
//if (argv.log) {
    //createClient(broker_uri, 'ZMQ Messaging');
//}

function test(msg) {
    if (msg == 'configure') {
        client_be.send_json(fd_config);
    }
    else if (msg == 'backtest') {
        client_be.send_json(bt_config);
    }
    else if (msg == 'optimize') {
        client_be.send_json(opt_config);
    }
}


process.on('uncaughtException', function (err) {
    nc.cleanup()
    console.error('[Node:worker] An uncaught error occurred!');
    console.error(err.stack);
    process.exit(0)
});
