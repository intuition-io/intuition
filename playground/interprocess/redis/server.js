const PORT = 6379;
const HOST = 'localhost';

var redis = require("redis"),
        client = redis.createClient(PORT, HOST),
        msg_count = 0;

    client.on("subscribe", function (channel, count) {
        console.log('Subscribing to ' + channel)
        client.publish(channel, 'Because I am polite')
    });

    client.on("message", function (channel, message) {
        console.log("client channel " + channel + ": " + message);
        msg_count += 1;
        if (msg_count === 3) {
            client.unsubscribe();
            client.end();
        }
    });

    client.incr("did a thing");
    client.subscribe("hello");
