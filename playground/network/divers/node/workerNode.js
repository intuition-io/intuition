// Use of the cluster plugin
// socket.io, jade, stylus, express, websocket

var colors = require('colors');

function run_worker(request_txt)
{
    var request = JSON.parse(request_txt);

    var script_args = []
    for (var arg in request.args) {
        script_args.push(request.args[arg].prefix);
        script_args.push(request.args[arg].value);
    };

    var script = require('path').join(__dirname, request.script);
    var spawn = require('child_process').spawn,
        child = spawn(script, script_args);

    child.stdout.on('data', function (data) {
        console.log('stdout: ' + data);
    });

    child.stderr.on('data', function (data) {
        console.log('stderr: ' + data);
    });

    child.on('exit', function (code, signal) {
        if (code === 0) {
            console.log('Node: Child exited normaly ('+code+')')
        } else {
            console.log('Node: Child process terminated with code ' + code + ', due to receipt of signal ' + signal);
        }
        child.stdin.end()
        child = undefined
    });

    process.on("SIGTERM", function() {
        console.log("Parent SIGTERM detected");
        process.exit();
    });

    process.on("exit", function() {
        if (child != undefined) {
            console.log("Kill child");
            child.kill('SIGHUP');
        }
    });

    process.on('uncaughtException', function (err) {
        console.error('An uncaught error occurred!');
        console.error(err.stack);
    });


    console.log(process.pid + ' - ' + process.title + ': Spawned child pid: ' + child.pid);
    child.stdin.write(JSON.stringify(request.config) + '\n')
}

exports.run_worker = run_worker;
