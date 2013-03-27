#!/bin/sh

#run shniy app in given directory
#NOTE could host the code on gist and run it with 'shiny::runGist("https://gist.github.com/rbresearch/5081906")'

if [ $# -gt 1 ]; then
    echo "Running shiny server $1 ..."
    R -q -e "shiny::runApp(\"$1\")"
else
    echo "No directory argument, Default shiny app used"
    echo "Running shiny server shiny-backtest ..."
    R -q -e "shiny::runApp(\"./server/shiny-backtest\")"
fi
