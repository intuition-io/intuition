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
var io = require('socket.io');

var app = express();
var server = http.createServer(app);
var io = io.listen(server);
io.set('log level', 1);

server.listen(PORT);
console.log('Server listening on port 4000')

var ticker = "";
app.get('/:ticker', function(req, res) {
	ticker = req.params.ticker;
	res.sendfile(__dirname + '/index.html');
});

io.sockets.on('connection', function(socket) {
	var local_ticker = ticker;
	ticker = "";

	//Run the first time immediately
	get_quote(socket, local_ticker);

	//Every N seconds
	var timer = setInterval(function() {
		get_quote(socket, local_ticker)
	}, FETCH_INTERVAL);

	socket.on('disconnect', function () {
		clearInterval(timer);
	});
});

function get_quote(p_socket, p_ticker) {
	http.get({
		host: 'www.google.com',
		port: 80,
		path: '/finance/info?client=ig&q=' + p_ticker
	}, function(response) {
		response.setEncoding('utf8');
		var data = "";
					
		response.on('data', function(chunk) {
			data += chunk;
		});
		
		response.on('end', function() {
			if(data.length > 0) {
				try {
					var data_object = JSON.parse(data.substring(3));
				} catch(e) {
					return;
				}
									
				var quote = {};
				quote.ticker          = data_object[0].t;
				quote.exchange        = data_object[0].e;
				quote.price           = data_object[0].l_cur;
				quote.change          = data_object[0].c;
				quote.change_percent  = data_object[0].cp;
				quote.last_trade_time = data_object[0].lt;
				quote.dividend        = data_object[0].div;
				quote.yield           = data_object[0].yld;
				
				p_socket.emit('quote', PRETTY_PRINT_JSON ? JSON.stringify(quote, true, '\t') : JSON.stringify(quote));
			}
		});
	});
}
