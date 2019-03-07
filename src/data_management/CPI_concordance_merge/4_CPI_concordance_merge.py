"""Merge CPI to concordance files.

Merge CPI file to both concordance files separately. Ensure no duplicates.
Save the two resulting CPI files based on different concordance files to 
'bld/out/data/CPI_and_CON'.

"""

import pandas as pd
import re

from bld.project_paths import project_paths_join as ppj


# -----------------------------------------------------------------------------
## Read in data.
# -----------------------------------------------------------------------------


con_WC = pd.read_pickle(ppj("OUT_DATA_CON_PREP", "WC_con"))
con_BLS = pd.read_pickle(ppj("OUT_DATA_CON_PREP", "BLS_con"))
d_CPI = pd.read_pickle(ppj("OUT_DATA_CPI_CLEARED", "CPI_for_con"))


# -----------------------------------------------------------------------------
## Loop to merge concordance files to CPI 
# -----------------------------------------------------------------------------


dic = {"WC": con_WC, "BLS": con_BLS}

for s in dic:
    con = dic[s]
    # use outer merge to decide how to deal with non-merged UCCs
    d_CPI_test = d_CPI.merge(
        con,
        left_on="concordance_id",
        right_on="item_id",
        how="outer",
        validate="m:m",
        indicator="source",
    )

    # -------------------------------------------------------------------------
    ## Check what concordance_id could not be merged.
    # -------------------------------------------------------------------------

    not_merged_in_CPI = d_CPI_test[["concordance_id", "source"]]
    not_merged_in_CPI = not_merged_in_CPI[not_merged_in_CPI.source == "left_only"]
    not_merged_in_CPI = not_merged_in_CPI.drop_duplicates("concordance_id")

    # Check what item strata did not get merged
    not_merged_in_CPI["item_stratum_non_merged"] = ""

    not_merged_in_CPI.index = range(0, len(not_merged_in_CPI))
    for i in range(0, len(not_merged_in_CPI)):
        if re.search("^\w{2}\d{2}$", not_merged_in_CPI["concordance_id"].iloc[i]):
            not_merged_in_CPI["item_stratum_non_merged"].iloc[i] = True
        else:
            not_merged_in_CPI["item_stratum_non_merged"].iloc[i] = False

    not_merged_item_in_CPI = not_merged_in_CPI[not_merged_in_CPI.item_stratum_non_merged]

    # Non-merged item-strata were coded as an expenditure class in the concordance file.
    # It was not possible to differentate between them as they had the same UCCs
    # in the concordance file.

    # ------------------------------------------------------------------------
    ## Check what CPIs from concordance file are not in CPI file.
    ## Match, if possible, to respective expenditure class.
    # ------------------------------------------------------------------------

    not_merged_in_con = d_CPI_test[["source", "item_id", "UCC"]]  # item_id is from con file
    not_merged_in_con = not_merged_in_con[not_merged_in_con.source == "right_only"]
    # non_merged UCCs can be matched to the expenditure class

    # derive expenditure class
    not_merged_in_con["item_id_new"] = ""
    for i in range(0, len(not_merged_in_con)):
        not_merged_in_con["item_id_new"].iloc[i] = not_merged_in_con.item_id.iloc[i][:2]

    con_exp_class = not_merged_in_con[["item_id_new", "UCC"]]
    con_exp_class.columns = ["item_id_II", "UCC"]

    # update concordance file: replace item_id in concordance file by exp. class id
    con = con.merge(con_exp_class, left_on="UCC", right_on="UCC", how="left", validate="1:1")

    for i in range(0, len(con)):
        if pd.isna(con.item_id_II.iloc[i]) == False:
            con.item_id.iloc[i] = con.item_id_II.iloc[i]
    con = con[["item_id", "UCC"]]

    # test whether UCCs are unique
    assert len(con.UCC.duplicated().unique()) == 1
    print("There are only unique UCCs in the concordance file.")

    # ------------------------------------------------------------------------
    ## Final merge.
    # ------------------------------------------------------------------------

    # check for uniqueness of series_i, year and period combinations in CPI file
    assert len(d_CPI.duplicated(["series_id", "year", "period"]).unique()) == 1
    print(
        "There are only unique series_id-year-month combinations in the CPI file,\
    ie. there is only one value per series/year/month combination."
    )

    d_CPI_con = con.merge(
        d_CPI, left_on="item_id", right_on="concordance_id", how="left", validate="m:m"
    )

    # check for uniqueness of UCC per year and period
    d_CPI_con["dups"] = d_CPI_con.duplicated(["UCC", "year", "period"], keep=False)
    dups_in_con = d_CPI_con[d_CPI_con.dups].sort_values(["UCC", "year", "period"])

    assert len(dups_in_con) == 0
    print(
        "There are",
        len(dups_in_con),
        "duplicates in terms of UCC year and period in the CPI data set.",
    )

    # ------------------------------------------------------------------------
    ## Ensure UCC is a float variable.
    # ------------------------------------------------------------------------


    d_CPI_con.UCC = d_CPI_con.UCC.astype(float)


    # ------------------------------------------------------------------------
    ## Save files.
    # ------------------------------------------------------------------------
    

    def save_con_data(file):
        file.to_pickle(ppj("OUT_DATA_CPI_CON", "CPI_m_" + str(s)))

    if __name__ == "__main__":
        datam = d_CPI_con
        save_con_data(datam)
