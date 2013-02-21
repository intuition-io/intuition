// Use of the cluster plugin
// colors, socket.io, jade, stylus, express, websocket

function run_worker(config_txt, socket)
{
    var config = JSON.parse(config_txt);

    var script_args = []
    for (var arg in config.args) {
        script_args.push(config.args[arg].prefix);
        if (config.args[arg].prefix != '--interactive')
            script_args.push(config.args[arg].value);
    };

    //var script = require('path').join(__dirname, config.script);
    var script = require('path').join(process.env.QTRADE, config.script);
    var spawn = require('child_process').spawn,
        child = spawn(script, script_args);
    console.log(script_args)

    child.stdout.on('data', function (data) {
        console.log('[Node:worker:stdout] ' + data);
    });

    child.stderr.on('data', function (data) {
        console.log('[Node:worker:stderr] ' + data);
    });

    child.on('exit', function (code, signal) {
        if (code === 0) {
            console.log('[Node:worker] Child exited normaly ('+code+')')
        } else {
            console.log('[Node:worker] Child process terminated with code ' + code + ', signal: ' + signal);
        }
        child.stdin.end()
        child = undefined
        socket.write('done:' + code)
    });

    console.log(process.pid + ' - ' + process.title + ': Spawned child pid: ' + child.pid);
    console.log('[Node:worker] Running worker: ' + script)
        
    //child.stdin.write(JSON.stringify(config.algo) + '\n')
    //child.stdin.write(JSON.stringify(config.manager) + '\n')
    
    var zmq_client = require('zmq').socket('req');

    zmq_client.on('message', function(reply) {
        console.log('Server replied: ', JSON.parse(reply))
    })

    console.log('Connecting to tcp://localhost:' + config.port);
    zmq_client.connect('tcp://localhost:' + config.port);

    console.log('Sending configuration...');
    zmq_client.send(JSON.stringify({algorithm: config.algorithm, manager: config.manager, done:true}))

    process.on("SIGTERM", function() {
        console.log("[Node:worker] Parent SIGTERM detected");
        zmq_client.close();
        process.exit();
    });

    process.on("SIGINT", function() {
        console.log("[Node:worker] Signal SIGINT detected");
        zmq_client.close();
        process.exit();
    });

    process.on("exit", function() {
        if (child != undefined) {
            console.log("[Node:worker] Killing child");
            child.kill('SIGHUP');
        }
    });

    process.on('uncaughtException', function (err) {
        console.error('[Node:worker] An uncaught error occurred!');
        zmq_client.close();
        console.error(err.stack);
    });
}

exports.run_worker = run_worker;
