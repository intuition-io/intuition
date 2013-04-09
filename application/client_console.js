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


var ui      = require('../server/console_ui')
    voice   = require('../server/vocal'),
    utils = require('../server/utils'),
    messenger = require('../server/messenger'),
    program = require('commander'),
    consign = require('commander'),
    config  = require('config');

program
    .version('0.0.1')
    .usage('[commands] <args>')
    .description('Remote client for NeuronQuant trading system')
    .option('-v, --verbose <level>', 'verbosity', Number, 2)
    .option('-l, --local', 'Make it fork server broker and work in local')
    .option('-s, --speak', 'Allows the program to synthetize voice')
    .option('-c, --channel <name>', 'Channel name of the client', String, 'dashboard')
    .parse(process.argv);



//TODO Move it to default.json, read by config ? built from config directory with others ?
var bt_config = {
    type: "fork",
    script: "application/app.py",
    port: 5555,
    args: {
        cash: {
            prefix: "-i",
            value: 10000 
        } ,
        ticker: {
            prefix: "--ticker",
            value: "random,3" 
        },
        exchange: {
            prefix: "--exchange",
            value: 'paris'
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
            value: "Fair" 
        },
        start: {
            prefix: "--start",
            value: "2006-01-10" 
        },
        end: {
            prefix: "--end",
            value: "15h50" 
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
            max_weight: 0.3,
            connected: 1,
            android: 1,
            loopback: 60,
            source: "mysql",
            perc_sell: 1.0,
            buy_amount: 80, 
            sell_amount: 70
        }
    },
    monitor: "notImplemented",
};

var opt_config = {
    type: "fork",
    script: "application/optimization/genetic_function.py",
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
        if (utils.isJsonString(consign.property)) {
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

        if (utils.isJsonString(consign.property)) {
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
    

// Because I can
if (program.speak) {
    voice.synthetize('Yo, remote client ready.', config.vocal.lang);
    require('sleep').sleep(5)
}

//TODO Should be after with the right socket. Reshape worker module
//     workers logs swrew ncurses ui and sleeps are annoying
//TODO Automatic detection from frontend and backend uris
if (program.local) {
    if (program.speak) {
        voice.synthetize('Running on local machine, forking broker process...', config.vocal.lang);
    }
    require('../server/worker').run({script: './application/server_fwd.js'}, null, null, program.channel);
}

// Define client interfaces, ui for curses graphics, be for backend work
// The test function is a callback called when hitting keyboard
var console_ui = new ui.UI_interface(command),
    client_be = new messenger.create_client(console_ui,
            config.network.frontport,
            program.channel,
            mega_config['broker']);
