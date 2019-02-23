.. _original_data:

*************
Original data
*************


Documentation of the different datasets in *original_data*.


CPI DATA
========

The folder contains the raw data on item-strata level *consumer price index (CPI)* retrieved from the web page of *Bureau of Labor Statistics (BLS)*, in csv format. 
The data is retrieved from *https://download.bls.gov/pub/time.series/cu/*

CEX DATA
========

The folder contains the raw data on household level expenditures, provided as the *Consumer Expenditure Survey (CEX)* monthly rotating panel data. retrieved from 
*https://www.bls.gov/cex/pumd_data.htm*


Concordance
========

The folder contains the concordance files, *concordance_BLS* and *concordance_WC*, that match item ids (UCC) from the CEX data set to the id in the CPI data set. The files are used to merge the two data sets. The two different concordance files complement each other. *concordance_BLS* was provided by the BLS and *concordance_WC* is taken from *CPI Requirements of CE* by *William Casey* retreived from *https://www.bls.gov/cex/ovrvwcpirequirement.pdf*. The *ELIconcordance_NS* file is necessary to cope with changes in the ids over time in the CPI data. The file is taken from the online appendix to the paper *The Elusive Costs of Inflation: Price Dispersion during the U.S. Great Inflation* by *Nakamura and Steinsson (2018)* retreived from *https://eml.berkeley.edu/~jsteinsson/papers.html*.


for_graph
========

The folder contains the raw data on household level expenditures, provided as the *Consumer Expenditure Survey (CEX)* monthly rotating panel data. retrieved from 
*https://www.bls.gov/cex/pumd_data.htm*