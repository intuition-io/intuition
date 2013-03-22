#!/usr/bin/env node

var program = require('commander'),
    feedparser = require('feedparser'),
    log = require('logging'),
    mysql = require('mysql'),
    config = require('config');

program
  .version('0.0.1')
  .usage('[command] <args>')
  .description('RSS feeds checker')
  .option('-u, --url <url>', 'specify the rss feed url', String, 'example')
  .option('-s, --server <adress>', 'mysql database adress', String, 'localhost')
  .option('-p, --password <chut>', 'mysql password', String, '')
  .parse(process.argv);

  /*
if (program.password == '') {
    log('** Error: You must provide MySQL password');
    process.exit(1);
}

var connection = mysql.createConnection({
    host     : program.server,
    user     : config.db.user,
    password : program.password,
    database : config.db.name
});

connection.connect(function(err) {
    if (err) throw err; 
    log('Connected to database');
});

log('Testing mysql api')
connection.query('show tables', function(err, rows, fields) {
    if (err) throw err;
    log(rows[0].Tables_in_stock_data);
});

connection.query('select * from Symbols limit 3', function(err, rows, fields) {
    if (err) throw err;
    log(rows[0].Name);
});

connection.end();
*/

log('Parsing required page: ', config.sources[program.url]);

feedparser.parseUrl(config.sources[program.url])
    .on('response', function(response) {
        //log(response);
    })
    .on('article', function callback (article) {
        //TODO Store some stuff here in mysql
        log(article.date, ' - ', article.title);
        //log(article.date, ' - ', article.title, ' (', article.link, ')');
        //log(article.description)
    })
    .on('end', function() {
        log('Parsing completed');
    })
    .on('error', function(error) {
        throw error;
    })

