doInstall <- FALSE
toInstall <- c("sna", "igraph", "ggplot2", "Hmisc", "reshape2")
if(doInstall){install.packages(toInstall, repos = "http://cran.r-project.org")}
lapply(toInstall, library, character.only = TRUE)
 
# Empty ggplot2 theme
new_theme_empty <- theme_bw()
new_theme_empty$line <- element_blank()
new_theme_empty$rect <- element_blank()
new_theme_empty$strip.text <- element_blank()
new_theme_empty$axis.text <- element_blank()
new_theme_empty$plot.title <- element_blank()
new_theme_empty$axis.title <- element_blank()
new_theme_empty$plot.margin <- structure(c(0, 0, -1, -1), unit = "lines",
                                         valid.unit = 3L, class = "unit")
 
data(coleman)  # Load a high school friendship network
adjacencyMatrix <- coleman[1, , ]  # Fall semester
layoutCoordinates <- gplot(adjacencyMatrix)  # Get graph layout coordinates
 
adjacencyList <- melt(adjacencyMatrix)  # Convert to list of ties only
adjacencyList <- adjacencyList[adjacencyList$value > 0, ]
 
# Function to generate paths between each connected node
edgeMaker <- function(whichRow, len = 100, curved = TRUE){
  fromC <- layoutCoordinates[adjacencyList[whichRow, 1], ]  # Origin
  toC <- layoutCoordinates[adjacencyList[whichRow, 2], ]  # Terminus
 
  # Add curve:
  graphCenter <- colMeans(layoutCoordinates)  # Center of the overall graph
  bezierMid <- c(fromC[1], toC[2])  # A midpoint, for bended edges
  distance1 <- sum((graphCenter - bezierMid)^2)
  if(distance1 < sum((graphCenter - c(toC[1], fromC[2]))^2)){
    bezierMid <- c(toC[1], fromC[2])
    }  # To select the best Bezier midpoint
  bezierMid <- (fromC + toC + bezierMid) / 3  # Moderate the Bezier midpoint
  if(curved == FALSE){bezierMid <- (fromC + toC) / 2}  # Remove the curve
 
  edge <- data.frame(bezier(c(fromC[1], bezierMid[1], toC[1]),  # Generate
                            c(fromC[2], bezierMid[2], toC[2]),  # X & y
                            evaluation = len))  # Bezier path coordinates
  edge$Sequence <- 1:len  # For size and colour weighting in plot
  edge$Group <- paste(adjacencyList[whichRow, 1:2], collapse = ">")
  return(edge)
  }
 
# Generate a (curved) edge path for each pair of connected nodes
allEdges <- lapply(1:nrow(adjacencyList), edgeMaker, len = 500, curved = TRUE)
allEdges <- do.call(rbind, allEdges)  # a fine-grained path ^, with bend ^
 
zp1 <- ggplot(allEdges)  # Pretty simple plot code
zp1 <- zp1 + geom_path(aes(x = x, y = y, group = Group,  # Edges with gradient
                           colour = Sequence, size = -Sequence))  # and taper
zp1 <- zp1 + geom_point(data = data.frame(layoutCoordinates),  # Add nodes
                        aes(x = x, y = y), size = 2, pch = 21,
                        colour = "black", fill = "gray")  # Customize gradient v
zp1 <- zp1 + scale_colour_gradient(low = gray(0), high = gray(9/10), guide = "none")
zp1 <- zp1 + scale_size(range = c(1/10, 1), guide = "none")  # Customize taper
zp1 <- zp1 + new_theme_empty  # Clean up plot
#print(zp1)
# Looks better when saved as a PNG:
ggsave("ggplotDirectedNetwork.png", zp1, h = 9/2, w = 9/2, type = "cairo-png")
