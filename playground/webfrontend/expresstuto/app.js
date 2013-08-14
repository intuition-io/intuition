/*
 * Module dependencies
 */
var express = require('express'),
    routes = require('./routes'),
    stylus  = require('stylus'),
    nib     = require('nib')

var app    = express(),
    server = require('http').createServer(app),
    io     = require('socket.io').listen(server)

function compile(str, path) {
    return stylus(str)
        .set('filename', path)
        .use(nib())
}

app.configure(function() {
	app.set('views', __dirname + '/views');
	app.set('view engine', 'jade');
    app.use(express.favicon());
	app.use(express.bodyParser());
	app.use(express.methodOverride());
	app.use(app.router);
    app.use(stylus.middleware(
        { src: __dirname + '/public', 
          compile: compile
        }
    ))
	app.use(express.static(__dirname + '/public'));
});


app.configure('development', function() {
	app.use(express.errorHandler({
		dumpExceptions : true,
		showStack : true
	}));
});

app.configure('production', function() {
	app.use(express.errorHandler());
});

app.get('/', routes.index);

//app.get('/', function (req, res) {
    //res.render('index',
    //{ title : 'Home' }
    //)
//})

app.listen(3000);
console.log("Express server listening on port %d in %s mode", app.get('port'), app.settings.env);

io.sockets.on('connection', function(socket) {
    console.log('[SocketIO] Client connected !')
    socket.emit('news', {hello: 'world'});
});
