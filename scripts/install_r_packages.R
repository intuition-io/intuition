#!/usr/bin/env Rscript
# Short script to install in one shot R required packages

#TODO lib parameters allow to specifie libs installation location
#However should detect if user did not already setup it, and if not
install.packages('quantmod', repos='http://cran.univ-paris1.fr/')
install.packages('RMySQL', repos='http://cran.univ-paris1.fr/')
install.packages('PerformanceAnalytics', repos='http://cran.univ-paris1.fr/')
install.packages('shiny', repos='http://cran.univ-paris1.fr/')
install.packages('rzmq', repos='http://cran.univ-paris1.fr/')
