dl_from_dropbox <- function(x, key) {
    require(RCurl)
    bin <- getBinaryURL(paste0("https://dl.dropboxusercontent.com/s/", key, "/", x),
                        ssl.verifypeer = FALSE)
    con <- file(x, open = "wb")
    writeBin(bin, con)
    close(con)
    message(noquote(paste(x, "read into", getwd())))
}

dlPublicDropboxData <- function(filename)
{
    #https://dl.dropboxusercontent.com/u/90840389/nasdaq100_symbols.csv
    fileurl <- paste("https://dl.dropboxusercontent.com/u/90840389", filename, sep='/')

    # Download data
    FinRegulatorData <- repmis::source_data(fileurl,
                                sep = ",",
                                header = TRUE)
}

# Example:
dl_from_dropbox("nasdaq100_symbols.csv", "90840389")
#shell.exec("nasdaq100_symbols.csv")
