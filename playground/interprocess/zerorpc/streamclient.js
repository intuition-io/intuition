var zerorpc = require("zerorpc");

var client = new zerorpc.Client();
client.connect("tcp://127.0.0.1:4242");

client.invoke("streaming_range", 10, 20, 2, function(error, res, more) {
    console.log(res);
});
