if (!suppressPackageStartupMessages(require(RJSONIO))) {
    stop("This app requires the rjsonio package. To install it, run 'install.packages(\"RJSONIO\")'.\n")
}

if (!suppressPackageStartupMessages(require(rzmq))) {
    stop("This app requires the rzmq package. To install it, run 'install.packages(\"rzmq\")'.\n")
}

remoteRun <- function(socket, cmd, debug=TRUE)
{
    if (!is.character(cmd))
        stop("User name must be a string")
    write.socket(socket, cmd)
    output <- character(0)
    #FIXME Loop until no data availbable (block at the moment)
    output <- read.socket(socket)
    if (debug) print(output)
    invisible(output)
}

remoteNodeWorker <- function(request, host='localhost', port=5555, debug=FALSE)
{
    socket <- make.socket(host, port)
    on.exit(close.socket(socket))
    output <- read.socket(socket)
    if (debug) print(output)
    # Check here if are indeed correctly connected
    output <- remoteRun(socket, toJSON(request), debug=debug)
    # Check here if we have 'done:0'
    if (debug) print(output)
    close.socket(socket)
    return(output)
}

#FIXME set.identity(socket, 'name') not available + broker can't read message
# Use ZMQ messaging to pass a json order to backend process, through machine's broker interface
zmqSend <- function(request,                  # Json request to remote or local broker
                    config='default.json',    # Common network configuration
                    debug=FALSE)
{
    # Configuration is stored in ./config/default.json, used by node.js broker
    config <- fromJSON(file(paste(Sys.getenv('NODE_CONFIG_DIR'), config, sep='/'), 'r')) 

    # Connects to broker (frontport) and sends request
    context = init.context()
    socket  = init.socket(context,'ZMQ_DEALER')
    print('Connecting to socket: ')
    print(config$network['frontport'])
    connect.socket(socket, config$network['frontport'][[1]])

    send.socket(socket, data=toJSON(request))
    print(toJSON(request, , pretty=TRUE))
    # Waits for ackwnoledgment 
    #answer <- receive.socket(socket)
    if (debug) 
    {
        print('Server sent back: ')
        #print(answer)
    }

    #NOTE Euhh close ?
    #return(answer)
}
