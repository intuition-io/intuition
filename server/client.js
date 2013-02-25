var config = {
    command: "run",
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
            value: "2005-01-10" 
        },
        end: {
            prefix: "--end",
            value: "2010-07-03" 
        } ,
        mode: {
            prefix: "--realtime"
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
};


var zmq = require('zmq')
    , broker_uri = 'tcp://127.0.0.1:5555';
    
function createClient (port, channel) {
    var socket = zmq.socket('dealer');

    socket.identity = channel

    socket.on('message', function(data) {
        json_data = JSON.parse(data)
        console.log(json_data.time + ': Incomming data from ' + json_data.channel)
        console.log(json_data.msg);
        socket.send(JSON.stringify({statut: 0}));
    });

    socket.connect(port);
    console.log('client connected');

    socket.send(JSON.stringify(config));
}    

function createClient (port, channel) {
    var socket = zmq.socket('dealer');

    socket.identity = channel

    socket.on('message', function(data) {
        json_data = JSON.parse(data)
        console.log(json_data.time + ': Incomming data from ' + json_data.channel)
        console.log(json_data.msg);
        socket.send(JSON.stringify({statut: 0}));
    });

    socket.connect(port);
    console.log('client connected');

    socket.send(JSON.stringify(config));
};;

createClient(broker_uri, 'ZMQ Messaging');
createClient(broker_uri, 'dashboard');
