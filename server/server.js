/*
 *Simple server waiting for instruction to fork
 */

var net = require('net');
var worker = require('./workerNode')

net.createServer(function (socket) {
    console.log('[Node:server] Client connected: ' + socket.remoteAddress + ':' + socket.remotePort);
    
    process.on('SIGINT', function() {
        console.log('Termination request, shutting down server...')
        process.exit(0)
    })

    socket.on('close', function() {
        console.log('[Node:server] Client disconnected')
    })

    socket.on('data', function(data) {
        console.log('[Node:server] Got data from ' + socket.remoteAddress + ':' + socket.remotePort + ':\n' + data);
        console.log('[Node:server] Initializing subprocess')
        //Here use cluster to eventually run several backtesters
        worker.run_worker(data, socket)
    })

    socket.write('connected:backtester\r\n');
    // Pipe redirects incoming stram on destination
    //socket.pipe(socket);
}).listen(8124, '127.0.0.1', function() {
    console.log('[Node:server] Online - 127.0.0.1:8124')
});

