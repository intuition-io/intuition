var net = require('net');
var colors = require('colors')
var worker = require('./workerNode')

var request = {
    command: 'spaw', 
    script: 'test.py',
    args: {
        ticker: {
            prefix: '--ticker',
            value: 'google'
        },
        start: {
            prefix: '-s',
            value: '12-12-2012'
        }
    },
    config: {
        log: 'info', 
        ma: '200'
     },
    monitor: 'notImplemented'
};
var txt_request = JSON.stringify(request);

net.createServer(function (socket) {
    console.log('Client connected: ' + socket.remoteAddress + ':' + socket.remotePort);
    
    socket.on('close', function() {
        console.log('Client disconnected'.red)
    })

    socket.on('data', function(data) {
        console.log('Got data from ' + socket.remoteAddress + ':' + socket.remotePort + ':\n' + data);
        console.log('Initializing subprocess')
        console.log('Json request: ' + txt_request)
        worker.run_worker(txt_request)
    })

    socket.write('connected:backtester\r\n');
    // Pipe redirects incoming stram on destination
    //socket.pipe(socket);
}).listen(8124, '127.0.0.1', function() {
    console.log('Server listening on 127.0.0.1:8124'.blue)
});

