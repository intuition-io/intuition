var request = {
    command: "run",
    script: "backtester/backtest.py",
    monitoring:      0,
    args: {
        ticker: {
            prefix: "--ticker",
            value: "random,1" 
        },
        algorithm: {
            prefix: "--algorithm",
            value: "Momentum" 
        },
        delta: {
            prefix: "--delta",
            value:      1 
        },
        manager: {
            prefix: "--manager",
            value: "Equity" 
        },
        start: {
            prefix: "--start",
            value: "2005-01-10" 
        },
        end: {
            prefix: "--end",
            value: "2010-07-03" 
        } 
    },
    algo: {
        debug: false 
    },
    manager: {
        loopback:     50,
        source: "mysql" 
    },
    monitor: "notImplemented"
};

var txt_request = JSON.stringify(request);

var net = require('net');

var HOST = '127.0.0.1';
var PORT = 8124;

var client = new net.Socket();
client.setEncoding('utf8')

client.connect(PORT, HOST, function() {

    console.log('Connected to: ' + HOST + ':' + PORT);
    // Write a message to the socket as soon as the client is connected, the server will receive it as message from the client 
    client.write(txt_request);

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
