## I/O test through RSQLite package
library("RSQLite")

drv <- dbDriver("SQLite")
connection <- dbConnect(drv, "assets.db")

## Checking the connection
dbListTables(connection)
dbListFields(connection, "google")

## Storing it in a dataframe
data <- dbReadTable(connection, "google")

## Writing a dataframe in a table, returning true
#stats = data.frame(X = c("value", "mean", "max", "min"), Y = c(4.32, 3.6, 5, 2))
#dbWriteTable(connection, "test", stats)

## Sending query
var <- "value"
query <- paste("SELECT", var)
query <- paste(query, "from stocks")
rs <- dbSendQuery(connection, query)
data <- fetch(rs,n=3) #3 rows, -1 for all
print(data)
dbHasCompleted(rs)

## Cleaning up
dbClearResult(rs)
dbDisconnect(connection)
dbUnloadDriver(drv)
