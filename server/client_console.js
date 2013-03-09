#!/usr/bin/env node
//
// Copyright 2012 Xavier Bruhiere
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

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
            long_window: 200,
            short_window: 100,
            threshold: 0
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
        },
        notify: {
            prefix: "flag",
            value: "--notify"
        }
    }
}


var zmq = require('zmq')
    , ui = require('client_ui')
    , program = require('commander')
    , config = require('config')
    , broker_uri = config.network.frontport;

program
    .version('0.0.1')
    .usage('[commands] <args>')
    .description('Remote client for NeuronQuant trading system')
    .option('-v, --verbose <level>', 'verbosity', Number, 2)
    .option('-c, --channel <name>', 'Channel name of the client', String, 'dashboard')
    .parse(process.argv);

var fd_config = {
    type: "configure",
    filters: ["portfolio", "acknowledgment", "optimization"],
    log_redirection: program.channel,
    verbose: program.verbose
};
    
/*
 * ZMQ based client, meant to communicate with the server forwarder 
 * TODO on-the-fly parameters visualisation and edition
 */
function create_client (port, channel) {
    client_ui.write_log('Log window setup done.');
    client_ui.write_msg('Message window setup done.');

    var socket = zmq.socket('dealer');
    
    // Channel is used on the server to route messages
    socket.identity = channel;

    // Main stuff, handle every message sent back
    socket.on('message', function(data) {
        json_data = JSON.parse(data);

        if (json_data.type == 'portfolio') {
            client_ui.write_msg(json_data.time + ' Portfolio:');
            client_ui.write_msg(JSON.stringify(json_data.msg.value));
            //FIXME Work only in above line configuration
            //client_ui.write_msg(json_data.time + ' Returns:', json_data.msg['returns']);
            //client_ui.write_msg(json_data.time + ' PNL:', json_data.msg.pnl);
        }

        else if (json_data.type == 'optimization') {
            client_ui.write_msg(json_data.msg['iteration'] + ' ' + json_data.msg['progress'] + '% | ' + json_data.msg['best'] + ' (' + json_data.msg['mean'] +')');
        }

        else if (json_data.type == 'acknowledgment') {
            client_ui.write_msg(json_data.time + 'Worker returned: ' + json_data.msg);
            socket.send(JSON.stringify({type: 'acknowledgment', statut: 0}));
        }

        else {
            //NOTE Should be dedicated to unexpected message, for now it's for logging
            //NOTE could configure a channel_log_filter in addition to the type filter, or merge them
            //TODO msg can be json object, detect and parse it
            client_ui.write_log(json_data.time + ' ' + json_data.func_name + ': ' + json_data.msg);
        }
    });

    socket.connect(port);
    client_ui.write_msg('[Node:Client] ' + socket.identity + ' connected');
    
    client_ui.write_msg('Initialize the forwarder with default configuration');
    socket.send(JSON.stringify(fd_config));

    this.send_json = function(msg) {
        socket.send(JSON.stringify(msg));
    }
}    


// Define client interfaces, ui for curses graphics, be for backend work
// The test function is a callback called when hitting keyboard
var client_ui = new ui.UI_interface(test),
    client_be = new create_client(broker_uri, program.channel);

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
