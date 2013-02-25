/*
 *This module is a bridge between a remote server and the client
 *It uses 0MQ to dispatch bi-directionnal messages to clients according to the channel parameter
 *In addition it can run local program (with futur cluster module, one per core actually)
 */

var zmq = require('zmq')
    , nma = require('./android_notify')
    , worker = require('./workerNode')
    , frontPort = 'tcp://127.0.0.1:5555'
    , backPort = 'tcp://127.0.0.1:5570'
    , logger_uri = 'tcp://127.0.0.1:5540';
    

function createQueueDevice(frontPort, backPort) {
    // Socket connected to client
    var frontSocket = zmq.socket('router'),
    // Socket connected to local processes
        backSocket = zmq.socket('dealer');

    frontSocket.identity = 'router' + process.pid;
    backSocket.identity = 'dealer' + process.pid;
    
    frontSocket.bind(frontPort, function (err) {
        console.log('bound', frontPort);
    });

    // Route messages from "envelope" to everybody connected to backsocket
    // Or fork a new process with the configuration received
    // Or use it for its own configuration
    frontSocket.on('message', function(envelope, data) {
        console.log(frontSocket.identity + ': received from ' + envelope + ' - ' + data.toString());
        json_data = JSON.parse(data);
        if (json_data.type == 'fork') {
            console.log('Processing fork request...');
            worker.run(json_data, backSocket, frontSocket, envelope);
        }
        else if (json_data.type == 'configure') {
            //TODO ... like channel or logging level filters
            console.log('Configuring forwarder...')
        }
        else {
            console.log('Routing data to backend socket...')
            backSocket.send(JSON.stringify(json_data))
        }
    });

    backSocket.bind(backPort, function (err) {
        console.log('bound', backPort);
    });
    
    // Route every message from clients, connected to backsocket, to clients connected to frontsocket
    // whose identity is json_data.channel.
    backSocket.on('message', function(data) {
        console.log(backSocket.identity + ': received ' + data.toString());
        json_data = JSON.parse(data)
        // For android channel use NotifyMyAndroid module
        if (json_data.channel == 'android') {
            //nma.check_key(nma.apikey)
            nma.notify(nma.apikey, json_data.appname, json_data.title, json_data.description, json_data.priority);
        }
        else {
            frontSocket.send([json_data.channel, JSON.stringify(json_data)]);
        } 
    });

    //TODO level filtrage configured by client
    // Route logbook zmq messages to clients with json_data.channel identity
    // see notes.rst for message json fields
    function createZmQLogHandler (port, frontSocket) {
        // Subscriber socker as logbook use publisher socket whith channel ''
        var socket = zmq.socket('sub');

        socket.identity = 'logbooksub' + process.pid;

        socket.subscribe('');
        socket.on('message', function(data) {
            console.log('app logged: ' + data.toString());
            json_data = JSON.parse(data)
            // Sends to 'ZMQ Messaging' client
            frontSocket.send([json_data.channel, JSON.stringify(json_data)])
        });

        socket.connect(port, function(err) {
            if (err) throw err;
            console.log('Client connected');
        });
    };
    createZmQLogHandler(logger_uri, frontSocket);
}

//TODO Wrap it into a net server
createQueueDevice(frontPort, backPort);
