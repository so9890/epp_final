"""Construct percentiles of income distribution.  
 
Merge CEX data on income ('itbi') and sampling weights ('fmli'), 
test for missing income data and extract pre-tax income for a given month. 
Ensure there is only one year in the resulting data frame. Derive income 
distribution and household-specific percentiles. Save data frame containing
household id, sampling weights and percentile.

Import:
Function 'weights_percentiles' from 'functions.py' to calculate income 
distribution function and assign percentile to households.

"""

import pandas as pd

from src.data_management.data_functions.functions import weights_percentiles
from bld.project_paths import project_paths_join as ppj

# -----------------------------------------------------------------------------
## Load data and merge.
# -----------------------------------------------------------------------------


data = pd.read_csv(ppj("IN_DATA_CEX", "itbi961x.csv"))
weights = pd.read_csv(ppj("IN_DATA_CEX", "fmli961x.csv"))[["NEWID", "FINLWT21"]]

data = data.merge(weights, left_on="NEWID", right_on="NEWID", how="left")


# -----------------------------------------------------------------------------
## Test for missing values.
# -----------------------------------------------------------------------------


if len(data[data["NEWID"].isin(weights["NEWID"])].index) == len(data.index):
    print("Length of data matches. All CUs in data got a sampling weight.")
else:
    print("Error: There are CUs without weight.")


if len(pd.unique(data["NEWID"])) == len(pd.unique(data[data["UCC"] == 980_000]["NEWID"])):
    print("All households reported income")
else:
    s = len(pd.unique(data["NEWID"])) - len(pd.unique(data[data["UCC"] == 980_000]["NEWID"]))
    print(s, " households did not report income and will be missing.")


# -----------------------------------------------------------------------------
## Only keep pre-tax income information for one month.
# -----------------------------------------------------------------------------


income_data_before_tax = data[data["UCC"] == 980_000]
income_12_1995 = income_data_before_tax[income_data_before_tax["REFMO"] == 12]

# -----------------------------------------------------------------------------
## Aplly function to derive cummulative distribution function and percentiles.
# -----------------------------------------------------------------------------


d_percentiles = weights_percentiles(income_12_1995)
d_percentiles_12_1995 = d_percentiles[["NEWID", "FINLWT21", "Percentile"]]


# -----------------------------------------------------------------------------
## Save data set.
# -----------------------------------------------------------------------------


def save(file):
    file.to_pickle(ppj("OUT_DATA_PERCENTILES", "12_1995_percentiles"))


if __name__ == "__main__":
    file = d_percentiles_12_1995
    save(file)
