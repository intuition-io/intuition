var net = require('net');
var worker = require('./workerNode')

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
            value: '30/1/2001'
        },
        end: {
            prefix: '-e',
            value: '30/7/2012'
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

net.createServer(function (socket) {
    console.log('Client connected: ' + socket.remoteAddress + ':' + socket.remotePort);
    
    socket.on('close', function() {
        console.log('Client disconnected')
    })

    socket.on('data', function(data) {
        console.log('Got data from ' + socket.remoteAddress + ':' + socket.remotePort + ':\n' + data);
        console.log('Initializing subprocess')
        worker.run_worker(data)
        console.log('Done.')
        socket.write('DONE')
    })

    socket.write('connected:backtester\r\n');
    // Pipe redirects incoming stram on destination
    //socket.pipe(socket);
}).listen(8124, '127.0.0.1', function() {
    console.log('Server listening on 127.0.0.1:8124')
});

