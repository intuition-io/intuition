require('./node_modules/shiny-server/lib/core/log');

var http = require('http');
http.createServer(function (req, res) {
  res.writeHead(200, {'Content-Type': 'text/plain'});
  res.end('Hello World\n');
}).listen(1337, '127.0.0.1');
logger.info('Server running at http://127.0.0.1:1337/');

// Clean up worker processes on shutdown

function caughtSignal() {
  logger.info('Shutting down worker processes...');
  setTimeout(process.exit, 500);
}

function caughtSignal() {
  logger.info('Shutting down worker processes...');
  setTimeout(process.exit, 500);
}

process.on('SIGINT', caughtSignal);
process.on('SIGTERM', caughtSignal);
process.on('uncaughtException', function(err) {
  logger.error('Uncaught exception: ' + err);
  throw err;
  process.exit(1);
});
process.on('exit', shutdown);
