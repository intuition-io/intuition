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

/*
 * This module is a bridge between a remote server and the client
 * It uses 0MQ to dispatch bi-directionnal messages to clients according to the channel parameter
 * In addition it can run local program (with futur cluster module, one per core actually)
 */


// client needs
var zmq = require('zmq'),
    config = require('config'),
    voice = require('./vocal');

//server ones
var nma      = require('./android_notify'),
    worker = require('./worker'),
    log    = require('logging');

    
exports.create_queue_device = function(server_uri_frontend, server_uri_backend, server_uri_logger) {
    // Type of data the forwarder will route to the client
    var filters = [];

    // Socket connected to client
    var frontSocket = zmq.socket('router'),
    // Socket connected to local processes
        backSocket = zmq.socket('dealer');

    frontSocket.identity = 'router' + process.pid;
    backSocket.identity = 'dealer' + process.pid;
    
    frontSocket.bind(server_uri_frontend, function (err) {
        log('Frontend connection bound to', server_uri_frontend);
    });

    // Depending of type, route messages from "envelope" to everybody connected to backsocket
    // Or fork a new process with the configuration received
    // Or use it for its own configuration
    frontSocket.on('message', function(envelope, data) {
        log(frontSocket.identity + ': received from ' + envelope + ' - ' + data.toString());
        json_data = JSON.parse(data);

        // Fork request, use worker node to spawn the process with its configuration, all specified in the message
        if (json_data.type == 'fork') {
            log('Processing fork request...');
            worker.run(json_data, backSocket, frontSocket, envelope);
        }

        // Forwarder conofiguration message
        //NOTE handle only log configuration, and not really sophisticated
        else if (json_data.type == 'configure') {
            log('Configuring forwarder...');
            filters = json_data.filters
            createZmQLogHandler(server_uri_logger, frontSocket, json_data.verbose, json_data.log_redirection);
        }

        else if (json_data.type == 'acknowledgment') {
            if (json_data.msg != 0) {
                log('** Error on client side')
            }
        }

        // All other types route to backend socket, not that sophisticated neither
        else {
            log(JSON.stringify(json_data));
            log('Routing data to backend socket...');
            backSocket.send(JSON.stringify(json_data));
        }
    });

    backSocket.bind(server_uri_backend, function (err) {
        log('Backend connection bound to', server_uri_backend);
    });
    
    // Route every message from clients, connected to backsocket, to clients connected to frontsocket
    // whose identity is json_data.channel.
    backSocket.on('message', function(data) {
        log(backSocket.identity + ': route data to frontend');
        json_data = JSON.parse(data)

        // For android channel use NotifyMyAndroid module
        if (json_data.channel == 'android') {
            //NOTE could use below function to check if send a notification is possible
            //nma.check_key(nma.apikey)
            nma.notify(nma.apikey, json_data.appname, json_data.title, json_data.description, json_data.priority);
        }
        else {
            for (var i=0; i < filters.length; i++) {
                if (json_data.type == filters[i]) {
                    frontSocket.send([json_data.channel, JSON.stringify(json_data)]);
                }
            }
        } 
    });

    // Route logbook zmq messages to clients with json_data.channel identity
    // see notes.rst for message json fields
    function createZmQLogHandler (uri, logSocket, verbose, redirection) {
        log('Setting up ZMQ distributed logger with level, ' + verbose + ', redirected to ' + redirection)

        // Subscriber socker as logbook use publisher socket whith channel ''
        var socket = zmq.socket('sub');
        socket.identity = 'logbooksub' + process.pid;
        socket.subscribe('');

        socket.on('message', function(data) {
            json_data = JSON.parse(data)
            redirection = (typeof redirection == 'undefined') ? json_data.channel : redirection;
            // Sends to 'ZMQ Messaging' client if the level is relevant
            if (json_data.level >= verbose) {
                log('App logged: ' + json_data.msg);
                logSocket.send([redirection, JSON.stringify(json_data)])
            }
        });

        socket.connect(uri, function(err) {
            if (err) throw err;
            log('ZMQ distributed logger connected on ', uri);
        });
    };
}



/*
 * ZMQ based client, meant to communicate with the server forwarder 
 * TODO on-the-fly parameters visualisation and edition
 */
exports.create_client = function(console_ui, server_uri, channel, broker_config) {
    server_uri = server_uri || 'tcp://127.0.0.1:5555';
    channel = channel || 'dashboard';
    
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
            console_ui.write_msg(json_data.time + ' portfolio:');
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
            socket.send(JSON.stringify({type: 'acknowledgment', msg: 0}));
        }

        //TODO Could be a vocal optimization message -> flag in the message or multiple type possible
        else if (json_data.type == 'vocal') {
            console_ui.write_log(json_data.time + ': ' + json_data.msg);
            voice.synthetize(json_data.msg, config.vocal.lang);
        }

        else {
            //NOTE Should be dedicated to unexpected message, for now it's for logging
            //NOTE could configure a channel_log_filter in addition to the type filter, or merge them
            //TODO msg can be json object, detect and parse it
            console_ui.write_log(json_data.time + ' ' + json_data.func_name + ': ' + json_data.msg);
        }
    });

    socket.connect(server_uri);
    console_ui.write_msg('[Node:Client] ' + socket.identity + ' connected');
    
    if (broker_config != undefined) {
        console_ui.write_msg('Initialize the forwarder with default configuration');
        socket.send(JSON.stringify(broker_config));
    }

    this.send_json = function(msg) {
        socket.send(JSON.stringify(msg));
    }
}    
