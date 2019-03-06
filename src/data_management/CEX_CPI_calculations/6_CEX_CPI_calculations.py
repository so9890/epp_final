"""Calculate expenditure shares and total expenditures on percentile level.

Save resulting data set as 'final_data_set_12_1995' to 'bld/out/final'.

"""

import pandas as pd

from bld.project_paths import project_paths_join as ppj


# ------------------------------------------------------------------------
## Read in data.
# ------------------------------------------------------------------------


data_12_1995 = pd.read_pickle(ppj("OUT_DATA_CEX_CPI_MERGED", "CEX_CPI_12_1995"))


# ------------------------------------------------------------------------
## Collapse data set on percentile level.
# ------------------------------------------------------------------------


exp_data_12_1995 = data_12_1995.groupby(
    ["Percentile", "UCC", "CodeDescription", "value"], as_index=False
).agg({"Weighted_exp": "sum"})


# ------------------------------------------------------------------------
## Calculate total expenditures by percentiles.
# ------------------------------------------------------------------------


exp_data_12_1995_total = exp_data_12_1995.groupby(["Percentile"], as_index=False).agg(
    {"Weighted_exp": "sum"}
)
exp_data_12_1995_total.columns = ["Percentile", "Total_expenditures"]

exp_data_12_1995 = exp_data_12_1995.merge(
    exp_data_12_1995_total,
    left_on="Percentile",
    right_on="Percentile",
    how="left",
    validate="m:1",
    indicator="source",
)


# ------------------------------------------------------------------------
##  Calculate shares on UCC-Percentile level and sort data set.
# ------------------------------------------------------------------------


exp_data_12_1995["share"] = pd.Series(
    data=exp_data_12_1995["Weighted_exp"].values / exp_data_12_1995["Total_expenditures"].values
)
exp_data_12_1995 = exp_data_12_1995[
    ["Percentile", "UCC", "share", "Total_expenditures", "value", "CodeDescription"]
].sort_values(["Percentile", "UCC"])


# ------------------------------------------------------------------------
##  Save file.
# ------------------------------------------------------------------------


def save_final_data(file):
    file.to_pickle(ppj("OUT_DATA_FINAL", "final_data_set_12_1995"))


if __name__ == "__main__":
    data = exp_data_12_1995
    save_final_data(data)
