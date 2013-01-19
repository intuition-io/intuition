require(RJSONIO)

remoteCmd <- function(socket, cmd, print=TRUE)
{
    print(cmd)
    if (!is.character(cmd))
        stop("user name must be a string")
    write.socket(socket, cmd)
    output <- character(0)
    #FIXME Loop until no data availbable (block at the moment)
    output <- read.socket(socket)
    if (print) print(output)
    invisible(output)
}

remoteJsonCmd <- function(socket, keys, values, print=TRUE)
{
    output <- remoteCmd(socket, toJSON(structure(values, names=keys), collapse=""), print=FALSE)
    if (print) print(output)
    return(output)
}

testClient <- function() 
{
    socket <- make.socket('localhost', 1234)
    on.exit(close.socket(socket))
    ouput <- read.socket(socket)
    output <- character(0)
    print(output)

    answer <- remoteCmd(socket, 'state')
    answer <- remoteJsonCmd(socket, 'user', 'xavier')

    close.socket(socket)
}

remoteNodeWorker <- function(request, host='localhost', port=2000, print=TRUE)
{
    socket <- make.socket(host, port)
    on.exit(close.socket(socket))
    output <- read.socket(socket)
    if (print) print(output)
    # Check here if are indeed correctly connected
    output <- remoteCmd(socket, toJSON(request), print=print)
    print(output)
    close.socket(socket)
    return(output)
}

