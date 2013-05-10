/*
 * http_request.js
 * Copyright (C) 2013 xavier <xavier@laptop-300E5A>
 *
 * Distributed under terms of the MIT license.
 */

var http = require('http');

// from http://docs.nodejitsu.com/articles/HTTP/clients/how-to-create-a-HTTP-request
//The url we want is: 'www.random.org/integers/?num=1&min=1&max=10&col=1&base=10&format=plain&rnd=new'
var options = {
    host: '127.0.0.1',
    path: '/auth/xavier',
    port: '8080',
    method: 'GET'
};

callback = function(response) {
  var str = '';

  //another chunk of data has been recieved, so append it to `str`
  response.on('data', function (chunk) {
    str += chunk;
  });

  //the whole response has been recieved, so we just print it out here
  response.on('end', function () {
    console.log(str);
  });
}

http.request(options, callback).end();
