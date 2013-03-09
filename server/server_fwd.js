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

/*
 * This module is a bridge between a remote server and the client
 * It uses 0MQ to dispatch bi-directionnal messages to clients according to the channel parameter
 * In addition it can run local program (with futur cluster module, one per core actually)
 * FIXME Prevent him from stopping (forever module ?)
 */

//TODO Use optimist or other cli tools to configure those ugly harcoded uri
var zmq          = require('zmq')
    , nma        = require('android_notify')
    , log        = require('logging')
    , worker     = require('worker')
    , program    = require('commander')
    , config     = require('config')
    , backPort   = config.network.backport
    , frontPort  = config.network.frontport
    , logger_uri = config.network.logger
    
program
    .version('0.0.1')
    .usage('[commands] <args>')
    .description('Forwarder interface for NeuronQuant trading system, server part')
    .option('-v, --verbose <level>', 'verbosity', Number, 2)
    .parse(process.argv);

function createQueueDevice(frontPort, backPort) {
    // Type of data the forwarder will route to the client
    var filters = [];

    // Socket connected to client
    var frontSocket = zmq.socket('router'),
    // Socket connected to local processes
        backSocket = zmq.socket('dealer');

    frontSocket.identity = 'router' + process.pid;
    backSocket.identity = 'dealer' + process.pid;
    
    frontSocket.bind(frontPort, function (err) {
        log('Frontend connection bound to', frontPort);
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
            createZmQLogHandler(logger_uri, frontSocket, json_data.verbose, json_data.log_redirection);
        }

        else if (json_data.type == 'acknowledgment') {
            if (json_data.statut != 0) {
                log('** Error on client side')
            }
        }

        // All other types route to backend socket, not that sophisticated neither
        else {
            log('Routing data to backend socket...')
            backSocket.send(JSON.stringify(json_data))
        }
    });

    backSocket.bind(backPort, function (err) {
        log('Backend connection bound to', backPort);
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
    //createZmQLogHandler(logger_uri, frontSocket);
}

createQueueDevice(frontPort, backPort);
