"""Calculate weighted expenditure on household level.

Extract expenditures data on household level from 'mtbi' file for one 
month-year combination. Merge to percentiles derived in '1_CEX_DATA_percentiles.py'.
Merge information on UCC from 'CE_dictionary.xlsx' and calculate weighted expenditures.
Save data set containing sampling weights and weighted expenditures. NOTE: this is not
yet agrgegated on percentile level.   

"""

import pandas as pd

from bld.project_paths import project_paths_join as ppj

# -----------------------------------------------------------------------------
## Load data.
# -----------------------------------------------------------------------------


data = pd.read_csv(ppj("IN_DATA_CEX", "mtbi961x.csv"))
data_12_1995 = data[data["REF_MO"] == 12]
data_12_1995 = data_12_1995[["NEWID", "UCC", "COST"]]
data_12_1995.index = range(len(data_12_1995))

d_percentiles = pd.read_pickle(ppj("OUT_DATA_PERCENTILES", "12_1995_percentiles"))


# -----------------------------------------------------------------------------
## Merge percentiles to expenditure data and drop households w/out percentiles.
# -----------------------------------------------------------------------------


data_12_1995 = data_12_1995.merge(
    d_percentiles,
    left_on="NEWID",
    right_on="NEWID",
    how="left",
    validate="m:1",
    indicator="source",
)

data_12_1995 = data_12_1995[["NEWID", "UCC", "COST", "FINLWT21", "Percentile"]][
    data_12_1995["source"] == "both"
]


# ------------------------------------------------------------------------
##  Add UCC code description and only keep those UCC with description.
# ------------------------------------------------------------------------

CE_dic = pd.read_excel(ppj("IN_DATA_CEX", "CE_dictionary.xlsx"), sheet_name=2, usecols="A:E")

CE_dic = CE_dic[CE_dic.File == "MTBI"]  # This is only in the Interview survey.
CE_dic = CE_dic[CE_dic.VariableName == "UCC"]
CE_dic.CodeValue = CE_dic.CodeValue.astype(int)
CE_dic = CE_dic[["CodeValue", "CodeDescription"]]

data_12_1995 = data_12_1995.merge(
    CE_dic, left_on="UCC", right_on="CodeValue", how="left", indicator="source"
)

data_12_1995 = data_12_1995[["UCC", "COST", "FINLWT21", "Percentile", "CodeDescription"]][
    data_12_1995.source == "both"
]


# ------------------------------------------------------------------------
## Calculate weighted expenditures.
# ------------------------------------------------------------------------


data_12_1995["Weighted_exp"] = data_12_1995["COST"] * data_12_1995["FINLWT21"]


# ------------------------------------------------------------------------
## Save data set.
# ------------------------------------------------------------------------


def save(file):
    file.to_pickle(ppj("OUT_DATA_WEIGHTS_AND_EXPENDITURES", "12_1995_weights_and_expenditures"))


if __name__ == "__main__":
    file = data_12_1995
    save(file)
