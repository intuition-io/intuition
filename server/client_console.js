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


var zmq = require('zmq')
    , ui = require('console_ui')
    , program = require('commander')
    , consign = require('commander')
    , config = require('config')
    , broker_uri = config.network.frontport
    , voice = require('vocal');

program
    .version('0.0.1')
    .usage('[commands] <args>')
    .description('Remote client for NeuronQuant trading system')
    .option('-v, --verbose <level>', 'verbosity', Number, 2)
    .option('-c, --channel <name>', 'Channel name of the client', String, 'dashboard')
    .parse(process.argv);


//TODO Move it to default.json, read by config ?
var bt_config = {
    type: "fork",
    script: "backtester/backtest.py",
    port: 5555,
    args: {
        cash: {
            prefix: "-i",
            value: 10000 
        } ,
        ticker: {
            prefix: "--ticker",
            value: "random,2" 
        },
        exchange: {
            prefix: "--exchange",
            value: 'nasdaq'
        } ,
        db: {
            prefix: "--database",
            value: 'test'
        } ,
        algorithm: {
            prefix: "--algorithm",
            value: "BuyAndHold" 
        },
        delta: {
            prefix: "--frequency",
            value: 'minute'
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
            value: "19h20" 
        } ,
        client: {
            prefix: "flag",
            value: "--remote"
        },
        mode: {
            prefix: "flag",
            value: "--live"
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
            name: "Xavier Bruhiere",
            load_backup: 1,
            max_weight: 0.5,
            connected: 1,
            buy_amount: 80, 
            sell_amount: 70
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

var fd_config = {
    type: "configure",
    filters: ["portfolio", "acknowledgment", "optimization", "vocal"],
    log_redirection: program.channel,
    verbose: program.verbose
};

var mega_config = {'backtest': bt_config,
                   'broker': fd_config,
                   'optimization': opt_config};
    
/*
 * ZMQ based client, meant to communicate with the server forwarder 
 * TODO on-the-fly parameters visualisation and edition
 */
function create_client (port, channel) {
    //NOTE Could set a flag to make it talk
    console_ui.write_log('Log window setup done.');
    console_ui.write_msg('Message window setup done.');

    var socket = zmq.socket('dealer');
    
    // Channel is used on the server to route messages
    socket.identity = channel;

    // Main stuff, handle every message sent back
    socket.on('message', function(data) {
        json_data = JSON.parse(data);

        if (json_data.type == 'portfolio') {
            console_ui.write_msg(json_data.time + ' Portfolio:');
            //console_ui.write_msg(JSON.stringify(json_data.msg.portfolio_value));
            console_ui.write_msg(JSON.stringify(json_data.msg));
            
            //FIXME Work only in above line configuration
            //console_ui.write_msg(json_data.time + ' Returns:', json_data.msg['returns']);
            //console_ui.write_msg(json_data.time + ' PNL:', json_data.msg.pnl);
        }

        else if (json_data.type == 'optimization') {
            console_ui.write_msg(json_data.msg['iteration'] + ' ' + json_data.msg['progress'] + '% | ' + json_data.msg['best'] + ' (' + json_data.msg['mean'] +')');
        }

        else if (json_data.type == 'acknowledgment') {
            console_ui.write_msg(json_data.time + ' - Worker returned: ' + json_data.msg);
            socket.send(JSON.stringify({type: 'acknowledgment', statut: 0}));
        }

        //TODO Could be a vocal optimization message -> flag in the message or multiple type possible
        else if (json_data.type == 'vocal') {
            console_ui.write_log(json_data.time + ' ' + json_data.func_name + ': ' + json_data.msg);
            voice.synthetize(json_data.msg, config.vocal.lang);
        }

        else {
            //NOTE Should be dedicated to unexpected message, for now it's for logging
            //NOTE could configure a channel_log_filter in addition to the type filter, or merge them
            //TODO msg can be json object, detect and parse it
            console_ui.write_log(json_data.time + ' ' + json_data.func_name + ': ' + json_data.msg);
        }
    });

    socket.connect(port);
    console_ui.write_msg('[Node:Client] ' + socket.identity + ' connected');
    
    console_ui.write_msg('Initialize the forwarder with default configuration');
    socket.send(JSON.stringify(fd_config));

    this.send_json = function(msg) {
        socket.send(JSON.stringify(msg));
    }
}    


// Because I can
//voice.synthetize('Yo, remote client ready.', config.vocal.lang);

// Define client interfaces, ui for curses graphics, be for backend work
// The test function is a callback called when hitting keyboard
var console_ui = new ui.UI_interface(command),
    client_be = new create_client(broker_uri, program.channel);


function isJsonString(text) {

    try {
        res = JSON.parse(text);
    } catch (e) {
        return false;
    }
    return true;
}

function command(msg) {
    // We're building a command line alike array from msg,
    // i.e. 'node program --flag value ...'
    command_line = msg.split(' ');
    command_line.unshift('client_console.js');
    //FIXME A bad argument crashs the program (and screws up the terminal)
    //FIXME -c doesn't work
    consign
        .option('-p, --property <value>', 'json string, to edit specified json config name accordingly', String, '{}')
        .option('-c, --config <name>', 'Target configuration object', String, 'backtest')
        .parse(command_line);

    if (command_line[1] == 'send') {
        if (consign.config in mega_config) {
            console_ui.write_msg(JSON.stringify(mega_config[consign.config], null, 4))
            client_be.send_json(mega_config[consign.config]);
        }
        else {
            console_ui.write_msg('** Error: ' + consign.config + ' configuration does not exist');
        }
    }

    else if (command_line[1] == 'order') {
        if (isJsonString(consign.property)) {
            console_ui.write_msg('Valid order, sending: ' + consign.property);
            client_be.send_json(consign.property);
        } else {
            console_ui.write_msg('Invalid json string, just pass');
        }
    }

    else if (command_line[1] == 'show') {
        console_ui.write_msg(JSON.stringify(mega_config[consign.config]), null, 4);
    }

    else if (command_line[1] == 'edit') {
        //TODO handle depth 2 at least
        bt_config.monitor = 'pouet';

        if (isJsonString(consign.property)) {
            new_values = JSON.parse(consign.property);
            console_ui.write_msg('Whole: ' + JSON.stringify(new_values))
            for (var key in new_values) {
                console_ui.write_msg('Value: ' + new_values[key])
                mega_config[consign.config][key] = new_values[key]
            }

            console_ui.write_msg('Updating configuration: ');
            console_ui.write_msg(JSON.stringify(mega_config[consign.config], null, 4));
        }
    }
}
