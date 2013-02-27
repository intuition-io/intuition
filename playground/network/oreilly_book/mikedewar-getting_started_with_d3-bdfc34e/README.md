Getting Started with D3
=======================

This is the code repository for the book "Getting Started With D3". Here you will find both the code for downloading and cleaning data from the MTA and code for drawing the visualisations.

* the code for cleaning up the data from the MTA lives in /cleaning_code 
* the code for the visualisations lives in /visulalisations and the cleaned up data lives in /visualisations/data

Cleaning Code
=============

If you want to run through the code that converts the raw MTA data to JSON, you should have a look in this folder. You will need Pandas for some of the examples:

* http://pandas.pydata.org/

The data lives in a mish-mash of text, XML and CSV files. Each python script takes one or more of these data files and converts them into a JSON file. The JSON files live in /visulalisations/data. 

*It should be noted that the files stored in this repository are for posterity only!*. You will probably have more fun downloading the most recent data files stored on the brilliant MTA website:

* http://www.mta.info/developers/

The MTA data is being constantly updated and refined, which means that the cleaning scripts here may no longer work on future MTA data. Please do report any problems with these files!

Visualisation Code
==================

The visualisations are self-sustained, so all you need do is to navigate to the /visualisations folder (in a terminal) and type:

* python -m SimpleHTTPServer 8000

and then navigate to http://localhost:8000.
