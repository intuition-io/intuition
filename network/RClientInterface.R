if (!suppressPackageStartupMessages(require(RJSONIO))) {
    stop("This app requires the rjsonio package. To install it, run 'install.packages(\"RJSONIO\")'.\n")
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

remoteNodeWorker <- function(request, host='localhost', port=2000, debug=FALSE)
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
