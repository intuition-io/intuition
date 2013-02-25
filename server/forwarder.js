var zmq = require('zmq')
    , nma = require('./android_notify')
    , frontPort = 'tcp://127.0.0.1:5555'
    , backPort = 'tcp://127.0.0.1:5570'
    , logger_uri = 'tcp://127.0.0.1:5540';
    

function createQueueDevice(frontPort, backPort) {
    var frontSocket = zmq.socket('router'),
        backSocket = zmq.socket('dealer');

    frontSocket.identity = 'router' + process.pid;
    backSocket.identity = 'dealer' + process.pid;
    
    frontSocket.bind(frontPort, function (err) {
        console.log('bound', frontPort);
    });

    frontSocket.on('message', function(envelope, data) {
        console.log(frontSocket.identity + ': received from ' + envelope + ' - ' + data.toString());
        backSocket.send(JSON.stringify({statut: 'ok', id: backSocket.identity}))
    });

    backSocket.bind(backPort, function (err) {
        console.log('bound', backPort);
    });
    
    backSocket.on('message', function(data) {
        console.log(backSocket.identity + ': received ' + data.toString());
        json_data = JSON.parse(data)
        if (json_data.channel == 'android') {
            nma.notify(nma.apikey, json_data.appname, json_data.title, json_data.description, json_data.priority);
            //nma.check_key(nma.apikey)
        }
        else {
            frontSocket.send([json_data.channel, JSON.stringify(json_data)]);
        } 
    });

    //TODO level filtrage configured by client
    function createZmQHandler (port, frontSocket) {
        var socket = zmq.socket('sub');

        socket.identity = 'worker' + process.pid;

        socket.subscribe('');
        socket.on('message', function(data) {
            console.log('app logged: ' + data.toString());
            json_data = JSON.parse(data)
            // Sends to 'ZMQ Messaging' client
            frontSocket.send([json_data.channel, JSON.stringify(json_data)])
        });

        socket.connect(port, function(err) {
            if (err) throw err;
            console.log('worker connected!');
        });
    };
    createZmQHandler(logger_uri, frontSocket);
}
createQueueDevice(frontPort, backPort);
