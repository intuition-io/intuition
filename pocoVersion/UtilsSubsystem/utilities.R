#require("RJSONIO")
library("RJSONIO")

#JSON reader
jsonReader <- function(fileName) {
    config = ""
    connection <- file(fileName, open='r')
    while ( length(line <- readLines(connection, n=1, warn= FALSE)) > 0 ) {
        config <- paste(config, line)
    }
    close(connection)
    return(config)
}

