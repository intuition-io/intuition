var request = {
    command: 'run', 
    script: 'pocoVersion/backtester/backtest.py',
    args: {
        ticker: {
            prefix: '--ticker',
            value: 'starbucks'
        },
        algorithm: {
            prefix: '--algorithm',
            value: 'DualMA'
        },
        level: {
            prefix: '--level',
            value: 'critical'
        },
        level: {
            prefix: '--delta',
            value: 1
        },
        start: {
            prefix: '-s',
            value: '1/1/2001'
        },
        end: {
            prefix: '-e',
            value: '1/7/2012'
        }
    },
    config: {
        short_window: 100, 
        long_window: 200,
        buy_on_event: 120,
        sell_on_event: 80
     },
    monitor: 'notImplemented'
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
