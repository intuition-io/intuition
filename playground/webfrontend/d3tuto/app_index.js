////
// CONFIGURATION SETTINGS
///
var PORT = 4000;
var FETCH_INTERVAL = 5000;
var PRETTY_PRINT_JSON = true;

///
// START OF APPLICATION
///
var express = require('express');
var http = require('http');

var app = express();
var server = http.createServer(app);

server.listen(PORT);
console.log('Server listening on port 4000')

var ticker = "";
app.get('/', function(req, res) {
	res.sendfile(__dirname + '/index.html');
});

