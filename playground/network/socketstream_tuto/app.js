var http = require('http'),
    ss = require('socketstream');

// Define a Single Page Client

ss.client.define('main', {
    views: 'app.html',
    css: ['app.css']
});

ss.http.route('/', function(req, res) {
    res.serveClient('main');
});

// Start the HTTP server
var server = http.Server(ss.http.middleware);
server.listen(3000);

console.log('Server running at http://127.0.0.1:3000/');
ss.start(server);

