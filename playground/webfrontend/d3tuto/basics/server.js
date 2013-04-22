var io = require('socket.io').listen(3000);
console.log('Server is up, listening on port 300')
 
io.sockets.on('connection', function (socket) {
 
    socket.on('message', function (message) {
        console.log("Got message: " + message);
        io.sockets.emit('pageview', { 'url': message });
    });
 
});
