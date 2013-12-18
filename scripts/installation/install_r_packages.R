#!/usr/bin/env Rscript
# Short script to install in one shot R required packages

#TODO lib parameters allow to specifie libs installation location
#install.packages('quantmod', repos='http://cran.univ-paris1.fr/', lib='.')
install.packages('quantmod', repos='http://cran.univ-paris1.fr/')
install.packages('RMySQL', repos='http://cran.univ-paris1.fr/')
install.packages('RSQLite', repos='http://cran.univ-paris1.fr/')
install.packages('PerformanceAnalytics', repos='http://cran.univ-paris1.fr/')
install.packages('shiny', repos='http://cran.univ-paris1.fr/')
install.packages('rzmq', repos='http://cran.univ-paris1.fr/')
install.packages('futile.logger', repos='http://cran.univ-paris1.fr/')
install.packages('optparse', repos='http://cran.univ-paris1.fr/')
install.packages('Quandl', repos='http://cran.univ-paris1.fr/')
install.packages('tseries', repos='http://cran.univ-paris1.fr/')
install.packages('polynom', repos='http://cran.univ-paris1.fr/')
install.packages('fImport', repos='http://cran.univ-paris1.fr/')
