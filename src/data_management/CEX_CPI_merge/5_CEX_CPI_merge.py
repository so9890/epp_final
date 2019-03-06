"""Merge price information from CPI to CEX expenditures on monthly level.

First, merge CPI file matched with BLS concordance to the expenditure data. 
All CEX data that does not get merged in that step will be merged to the CPI file 
matched with WC concordance file. Save data set containing all and only merged 
CEX observations as 'CEX_CPI_12_1995' to 'bld/out/data/CEX_CPI_merged'.

"""

import pandas as pd

from bld.project_paths import project_paths_join as ppj


# ------------------------------------------------------------------------
## Read in data.
# ------------------------------------------------------------------------


d_exp_12_1995 = pd.read_pickle(ppj("OUT_DATA_WEIGHTS_AND_EXPENDITURES", "12_1995_expenditures"))
d_CPI = pd.read_pickle(ppj("OUT_DATA_CPI_CON", "CPI_m_BLS"))


# ------------------------------------------------------------------------
## Keep price information for respective month-year of expenditures.
# ------------------------------------------------------------------------


d_CPI_12_1995 = d_CPI[d_CPI["year"] == 1995]
d_CPI_12_1995 = d_CPI_12_1995[["series_id", "value", "UCC"]][
    d_CPI_12_1995.period.str.contains("12")
]


# ------------------------------------------------------------------------
## Merge CPI data set to expenditure data.
# ------------------------------------------------------------------------


# verify UCCs are integers in both files
d_exp_12_1995["UCC"] = d_exp_12_1995["UCC"].astype(int)
d_CPI_12_1995["UCC"] = d_CPI_12_1995["UCC"].astype(int)

d_exp_12_1995 = d_exp_12_1995.merge(
    d_CPI_12_1995, left_on="UCC", right_on="UCC", how="left", validate="m:1", indicator="source"
)


# ------------------------------------------------------------------------
# Split merged expenditure file into a merged and non_merged data set.
# ------------------------------------------------------------------------


not_merged = d_exp_12_1995[["Percentile", "UCC", "Weighted_exp", "CodeDescription"]][
    d_exp_12_1995.source == "left_only"
]
print(len(not_merged.drop_duplicates("UCC")), "UCCs could not be merged with BLS concordance.")

# also keep all merged UCCs that will be used to append data set later.
merged = d_exp_12_1995[
    ["Percentile", "UCC", "Weighted_exp", "CodeDescription", "series_id", "value"]
][d_exp_12_1995.source == "both"]


# ------------------------------------------------------------------------
## Use the concordance file from William Casey to match so far unmatched UCCs.
# ------------------------------------------------------------------------


d_CPI_WC = pd.read_pickle(ppj("OUT_DATA_CPI_CON", "CPI_m_WC"))

# keep relevant periods only
d_CPI_WC_12_1995 = d_CPI_WC[d_CPI_WC["year"] == 1995]
d_CPI_WC_12_1995 = d_CPI_WC_12_1995[["series_id", "value", "UCC"]][
    d_CPI_WC_12_1995.period.str.contains("12")
]

# ensure UCC in d_CPI_WC is integer
d_CPI_WC_12_1995["UCC"] = d_CPI_WC_12_1995["UCC"].astype(int)

# merge
not_merged = not_merged.merge(
    d_CPI_WC_12_1995, left_on="UCC", right_on="UCC", how="left", indicator="source", validate="m:1"
)

# some items are still not merged.
not_mergedII = not_merged[["UCC", "source"]]

# only keep those observations that are not in d_CPI_WC_12_1995
not_mergedII = not_mergedII[not_mergedII.source == "left_only"]

print(
    len(not_mergedII.drop_duplicates("UCC")),
    "UCCs could not be merged after \
additional WS concordance. They are not in the CPI data set for the given month-year \
combination. Thus,",
    len(not_merged.drop_duplicates("UCC")) - len(not_mergedII.drop_duplicates("UCC")),
    "additinal observations merged thanks to WS concordance file.",
)

# only keep observations that got merged
mergedII = not_merged[
    ["Percentile", "UCC", "Weighted_exp", "CodeDescription", "series_id", "value"]
][not_merged.source == "both"]


# ------------------------------------------------------------------------
## Bring both merged data sets together.
# ------------------------------------------------------------------------


exp_cpi_12_1995 = merged.append(mergedII)


# ------------------------------------------------------------------------
## Save file.
# ------------------------------------------------------------------------


def save_cex_cpi_data(file):
    file.to_pickle(ppj("OUT_DATA_CEX_CPI_MERGED", "CEX_CPI_12_1995"))


if __name__ == "__main__":
    data = exp_cpi_12_1995
    save_cex_cpi_data(data)
