#!/usr/bin/env Rscript

library("optparse")

source(paste(BASEDIR,"functions/ExpressionAnalysis.R", sep=""))
### LOAD PLOTTING FUNCTIONS
source(paste(BASEDIR,"functions/Graphics.R", sep=""))

ver <- packageDescription('pgfSweave')[['Version']]

suppressPackageStartupMessages(library(optparse))

option_list <- list( 
    make_option(c("-v", "--version"), 
        action="store_true", default=FALSE,
        help="Print version info and exit"),
    make_option(c("-d", "--dvi"), 
        action="store_true", default=FALSE,
        help="dont use texi2dvi() option pdf=T i.e. call plain latex to produce a dvi file instead of a pdf"),
    make_option(c("-p", "--processors"), 
        type="integer", default=2, 
        help="Number of processors to use for graphics externalization [default %default]",
        metavar="number"),
    make_option(c("-n", "--graphics-only"), 
        action="store_true", default=FALSE,
        help="dont do (3), do (1) then (2); ignored if --pgfsweave-only is used"),
    make_option(c("-s", "--pgfsweave-only"), 
        action="store_true", default=FALSE,
        help="dont do (2) or (3), only do (1)")
    )

op.obj <- OptionParser(option_list=option_list, 
    usage = "    R CMD pgfsweave [options] <file>

    A simple front-end for pgfSweave()

    The options below reference the following steps 
      (1) Run Sweave using pgfSweaveDriver
      (2) Run the pgf externalization commands (requires GNU make)
      (3) Compile the resulting tex file using texi2dvi()

    Default behavior (no options) is to do (1), (2) then (3) in that order.

    Package repositories: 
    http://github.com/cameronbracken/pgfSweave (cutting edge development)
    http://r-forge.r-project.org/projects/pgfsweave/ (precompiled dev versions)
    http://cran.r-project.org/web/packages/pgfSweave/index.html (stable release)")
opt <- parse_args(op.obj, positional_arguments = TRUE)

file <- opt$args
opt <- opt$options

### GET VERSION
source(paste(BASEDIR,"config/VERSION.R", sep=""))
### END GET VERSION

args <- commandArgs(trailingOnly = TRUE)
if(length(args)==0){
  print("No arguments supplied.")
  ##supply default values
  a = 1
  b = c(1,1,1)
}else{
  for(i in 1:length(args)){
    print(args[[i]])
    eval(parse(text=args[[i]]))
  }
}
print(a*2)
print(b*3)

q(status=0)
