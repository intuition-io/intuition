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

function <- testClient() 
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
