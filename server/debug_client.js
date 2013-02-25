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

var txt_config = JSON.stringify(config);

var net = require('net');

var HOST = '127.0.0.1';
var PORT = 8124;

var client = new net.Socket();
client.setEncoding('utf8')

client.connect(PORT, HOST, function() {

    console.log('Connected to: ' + HOST + ':' + PORT);
    // Write a message to the socket as soon as the client is connected, the server will receive it as message from the client 
    client.write(txt_config);

});

// Add a 'data' event handler for the client socket
// data is what the server sent to this socket
client.on('data', function(data) {
    
    console.log('Incoming data: ' + data);
    // Close the client socket completely
    if (data.substr(0, 4) == 'done') 
    {
        console.log('Worker is done, destroying connection...')
        client.destroy()
    }
    
});

// Add a 'close' event handler for the client socket
client.on('close', function() {
    console.log('Connection closed');
});
