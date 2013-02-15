// Use of the cluster plugin
// colors, socket.io, jade, stylus, express, websocket

function run_worker(request_txt, socket)
{
    var request = JSON.parse(request_txt);

    var script_args = []
    for (var arg in request.args) {
        script_args.push(request.args[arg].prefix);
        if (request.args[arg].prefix != '--interactive')
            script_args.push(request.args[arg].value);
    };

    //var script = require('path').join(__dirname, request.script);
    var script = require('path').join(process.env.QTRADE, request.script);
    var spawn = require('child_process').spawn,
        child = spawn(script, script_args);

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

    process.on("SIGTERM", function() {
        console.log("[Node:worker] Parent SIGTERM detected");
        process.exit();
    });

    process.on("exit", function() {
        if (child != undefined) {
            console.log("[Node:worker] Kill child");
            child.kill('SIGHUP');
        }
    });

    process.on('uncaughtException', function (err) {
        console.error('[Node:worker] An uncaught error occurred!');
        console.error(err.stack);
    });


    console.log(process.pid + ' - ' + process.title + ': Spawned child pid: ' + child.pid);
    console.log('[Node:worker] Running worker: ' + script)
    child.stdin.write(JSON.stringify(request.algo) + '\n')
    child.stdin.write(JSON.stringify(request.manager) + '\n')
}

exports.run_worker = run_worker;
