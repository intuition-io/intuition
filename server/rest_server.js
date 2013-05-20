#!/usr/bin/env node
'use strict';

// Rest lib: http://mcavage.github.io/node-restify/
// Logging: https://github.com/trentm/node-bunyan
// Usage example: curl -is http://localhost:8080/auth/xavier?id=2156
//TODO Log custom widget. Use a static template html file, receive zmq or http_proxy messages 
//and generate page with: https://github.com/zendesk/curly or https://github.com/jlong/radius
var program = require('commander'),
    log = require('logging'),
    mysql = require('mysql'),
    restify = require('restify'),
    config = require('config');

program
  .version('0.0.1')
  .usage('[command] <args>')
  .description('RESTFul server')
  .option('-s, --server <adress>', 'mysql database adress', String, 'localhost')
  .option('-p, --password <chut>', 'mysql password', String, '')
  .parse(process.argv);


function get_dashboard_request(type, table, target, selector, from, to, callback) {
    selector = selector || '';
    from = from || '';
    to = to || Math.floor(Date.now() / 1000);
    var result = undefined;

    if (type === 'graph')
        target += ',Date';
    var statement = 'SELECT ' + target + ' FROM ' + table;
    if (selector != '' || from != '')
        statement += ' WHERE ';
    if (selector != '') {
        selector.value = selector.value.replace('+', ' ')
        statement += selector.field + '=\''+ selector.value + '\'';
        if (from != '')
            statement += ' AND ';
    }
    if (from != '') {
        //FIXME Applications work with utc time, and i am in France
        from -= (2 * 60 * 60);
        to -= (2 * 60 * 60);
        statement += ' Date >= FROM_UNIXTIME(' + from + ') AND Date <= FROM_UNIXTIME(' + to + ')';
    }
    else
        statement += ' ORDER BY Id DESC LIMIT 1';
    log('MySQL request: ' + statement);

    // For now at least, only retrieve last value, and check if it is positive
    // order by Id: well not always indexed by Id ? (date)
    connection.query(statement, function(err, rows, fields) {
        //if (err) throw err;
        if (err || rows.length == 0)
            return;
            
        if (type === 'boolean')
            result = (rows[0][target] > 0 ? true : false);
        else if (type === 'number')
            result = rows[0][target];
        else if (type === 'graph') {
            result = [];
            for (var i=0; i < rows.length; i++) 
                result.push([rows[i][target.split(',')[0]], Math.floor(Date.parse(rows[i].Date) / 1000)])
        }
        else
            result = '** Unknown widget type';
        callback(result);
    });
}

function authentification(req, res, next) {
    log('Name::Received request with params ', req.params);
    if (req.params.name == 'dous')
        return next(new restify.NotAuthorizedError('Dangerous user, will probably crash the system !'));

    if ('id' in req.params) {
        log('Connection credentials: ' + req.params.id)
        res.send({'login ': req.params.name, 'id':  req.params.id});
    } else {
        res.send({'auth ': req.params.name});
        log('No credentials provided')
    }
    return next();
}


function dashboard(req, res, next) {
    // Request: http://127.0.0.1:8080/dashboard/graph?table=Portfolios&data=returns
    log('Widget::Received request with params ', req.params);

    var selector = null;
    if ('field' in req.params && 'value' in req.params) {
        selector = {'field': req.params.field, 'value': req.params.value};
    }
    log('Selector: ', selector);
    
    if (req.params.widget === 'graph') {
        //NOTE For demonstratio purpose, in production, let as is
        var offset = 94608000;
        var from = parseInt(req.params.from);
        var to = parseInt(req.params.to);
        //var targets = req.params.targets[0].split(',')
        var targets = req.params.targets;

        //TODO Multiple target: each parameter could be comma separated, then result would be an array of arrays
        get_dashboard_request('graph', req.params.table, req.params.data, selector, from, to, function (result) {
            res.send([
              {
                "target" : targets[0],
                "datapoints" : result
              }]);
        });
    }

    else if (req.params.widget === 'number') {
        get_dashboard_request('number', req.params.table, req.params.data, selector, null, null, function (result) {
            res.send({ 'value' : result, 'label': req.params.data });
        });
    }

    else if (req.params.widget === 'boolean') {
        get_dashboard_request('boolean', req.params.table, req.params.data, selector, null, null, function (result) {
            res.send({ 'value' : result, 'label': req.params.data });
        });
    }

    else {
        log('** Error::Unknown widget');
    }

    return next();
};


var connection = mysql.createConnection({
    host     : program.server,
    user     : config.mysql.user,
    password : config.mysql.password,
    database : config.mysql.database
});

connection.connect(function(err) {
    if (err) throw err; 
    log('Connected to database');
});

var server = restify.createServer({name: 'R&D test'});

server.use(restify.acceptParser(server.acceptable));
server.use(restify.authorizationParser());
server.use(restify.dateParser());
server.use(restify.queryParser());
server.use(restify.bodyParser());
server.use(restify.throttle({
    burst: 100,
    rate: 50,
    ip: true, // throttle based on source ip address
    overrides: {
        '127.0.0.1': {
        //'192.168.0.12': {
            rate: 0, // unlimited
    burst: 0
        }
    }
}));


server.get('/auth/:name', authentification);
server.head('/auth/:name', authentification);  // Useless ?
server.get('/dashboard/:widget', dashboard);

var port = 8080;
//var port = 4000;
var ip = '127.0.0.1';
//var ip = '192.168.0.12';
server.listen(port, ip, function() {
    log(server.name + ' listening at ' + server.url);
});


process.on('SIGINT', function() {
    console.log('Got SIGINT signal, exiting...');
    process.exit(0);
});


process.on('exit', function() {
    connection.end();
    console.log('Shutting down database and REST server');
});

process.on('uncaughtException', function(err) {
    log('warning: Uncaught error occured')
})
