# Repeated Donation Analytics

## Summary
In this repository we implement a script that reads donation data according the 
[FEC standard](https://classic.fec.gov/finance/disclosure/metadata/DataDictionaryContributionsbyIndividuals.shtml). It
identifies donations from repeat donors (donors who have contributed in a previous year). For each
donation from a repeated donor, it outputs information about the repeated donations the
recipient has gotten from the same zip code. 


## Implementation Details
Our algorithm uses the following data structures:
1. A dictionary repeaded_donors to store the year of the earliest donation of each donor. We use this dictionary to determine if a donor is a repeated donor.
   The only operations we need are updating, adding and reading. All of these operations run in constant time (amortized) on a dictionary
2. A dictionary recipients to store a sorted list (see next point) of donations. The key is a tuple (recipient CMTE_ID, zipcode, year), so each
   entry collects the donations a recipient has gotten in a given year from a given zipcode by repeated donors.
   A dictionary is a great choice, as we again only use updating, adding and reading.
3. As noted above, each entry in the dictionary recipients contains a sortedlist. This is a public python package (see Dependencies for
   installation details) that implements a fast data structure sortedlist. As the name suggest, it is a list that is always sorted ascendingly.
   As we have to compute percentiles of these lists, a sorted list is ideal for efficient computations. This is especially relevant considering
   that the challenge said that we should assume the data is streaming in and we will compute different percentiles at different times.
   A sortedlist would be very efficient at handling these scenarios.

The approach to the challenge is as follows

1. Read the percentile value
2. Run through every line of the code. If the code contains a valid entry of an individual contribution, then we first check if
   this is the earliest donation of the donor and save this information in repeated_donors.
3. In case the donor has a donation from an earlier year, we then add the amount donated to recipients dictionary under the
   key associated with the recipient, the zipcode of the donor and the year.
4. We now create the ouput strong corresponding to this donation:
   with the information of the recipient, the zip code of the donor, the year of the donation, 
   the percentile value of the donations received this year from this zip code, the total amount of donations from
   this zip code and the total number of donations from this zip code. Note that computing the percentile value
   is efficient as we stored the donations in a sorted list.
5. Once we have processed the whole file, we write our results to the output file

### Some remarks on the performance

Note that all operations performed are in constant (amortized) time except the 
update of the sorted lists of donations. As this is the bottleneck of our
algorithm, we carefully selected the sortedlist datastructure because of
its impressive performance (it even outperforms many compareable implementations
in C). The website [sortedcontainers](http://www.grantjenks.com/docs/sortedcontainers/) contains
more details on this data structure and also provides benchmark results.



## Dependencies
We import three packages

1. sys - a core Python package, no installation needed
2. math - a core Python package, no installation needed
3. datetime - a core Python package, no installation needed
4. re - a core Python package, no installation needed
5. sortedcontainers - can be installed via "pip3 install sortedcontainers" on Python 3. Compare also [sortedcontainers](http://www.grantjenks.com/docs/sortedcontainers/).

## Running instructions

It was developed and tested under Python 3.4, it was also tested under Python 3.6 and should run under Python 3.x.
If the files itcont.txt, percentile.txt are stored in the input folder, then a simple execution of
run.sh suffices to run the script and save the results in repeated_donors.txt in the output folder.

Tests can be run by running run_tests.sh in the insight_testsuite folder.

