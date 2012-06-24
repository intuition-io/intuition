## I/O test through RSQLite package
library("RSQLite")

drv <- dbDriver("SQLite")
connection <- dbConnect(drv, "assets.db")

## Checking the connection
dbListTables(connectio)
dbListFields(connection, "stocks")

## Storing it in a dataframe
data <- dbReadTable(connection, "stocks")

## Writing a dataframe in a table, returning true
stats = data.frame(X = c("value", "mean", "max", "min"), Y = c(4.32, 3.6, 5, 2))
dbWriteTable(connection, "test", stats)

## Sending query
rs <- dbSendQuery(connection, 'the query')
data <- fetch(rs,n=3) #3 rows, -1 for all
dbHasCompleted(rs)

## Cleaning up
dbClearResult(rs)
dbDisconnect(connection)
dbUnloadDriver(driver)
