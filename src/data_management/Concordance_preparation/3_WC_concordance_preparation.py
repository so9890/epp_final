"""Prepare concordance file taken from William Casey paper.

Assign UCCs to item ids. Note, the data set is copied from a PDF making additional 
cleaning steps necessary. Derive item id from ELI id. For duplicates in terms of 
item stratum id and UCC use expenditure class. Clean concordance file for potential
duplicates in terms of UCC.

Return concordance file that matches a UCC to one item-stratum/expenditure class
id that is given in the CPI data set, save file to 'bld/out/data/Concordance_prepared'
as 'WC_con'.

"""

import pandas as pd
import re

from bld.project_paths import project_paths_join as ppj


# -----------------------------------------------------------------------------
## Read in data.
# -----------------------------------------------------------------------------


d_CPI = pd.read_pickle(ppj("OUT_DATA_CPI_CLEARED", "CPI_for_con"))
con = pd.read_excel(
    ppj("IN_DATA_CON", "concordance_WC.xlsx"),
    header=None,
    usecols="A:B",
    names=["concordance_sheet", "Drop"],
)


# -----------------------------------------------------------------------------
## Drop nans. Page numbers in con.concordance_sheet are coded as nan.
## Split column containing code into UCC and CPI item_id.
## Note that CPI codes are strings and UCCs are integers.
# -----------------------------------------------------------------------------


con = pd.DataFrame(data=con.concordance_sheet[~pd.isna(con.Drop)], columns=["concordance_sheet"])
con.index = range(0, len(con))


con["UCC"] = ""
con["item_id"] = ""

for i in range(0, len(con)):
    if isinstance(con.concordance_sheet[i], int):
        con.UCC[i] = con.concordance_sheet[i]
    else:
        con.item_id[i] = con.concordance_sheet[i]

con = con[["concordance_sheet", "item_id", "UCC"]]


# -----------------------------------------------------------------------------
## Merge item_id from CPI file. Only keep data that we have in the CPI
## file.
# -----------------------------------------------------------------------------


c_CPI_unique = pd.DataFrame(data=d_CPI["concordance_id"].unique(), columns=["concordance_id"])
con = con.merge(
    c_CPI_unique,
    left_on="item_id",
    right_on="concordance_id",
    how="left",
    indicator="source",
    validate="m:1",
)  # many to one because of missing values


# -----------------------------------------------------------------------------
## Ensure that concordance_id is nan only for non_merged item_ids.
## Necessary for the following cleaning steps.
# -----------------------------------------------------------------------------


con.concordance_id[con.UCC != ""] = ""

con["BoolIII"] = ""
for i in range(0, len(con)):
    if pd.isna(con.concordance_id.iloc[i]):
        if pd.isna(con.concordance_id.iloc[i + 1]) | pd.isna(con.concordance_id.iloc[i - 1]):
            con["BoolIII"][i] = True
        else:
            con["BoolIII"][i] = False
    else:
        con["BoolIII"][i] = ""


# -----------------------------------------------------------------------------
## Drop those observations for which BOOLIII==False. They are ELIs and cannot
## be matched to CPI. By dropping them the corresponding UCC will be assigned the
## item stratum id in the following.
# -----------------------------------------------------------------------------


con = con[con.BoolIII != False]


# -----------------------------------------------------------------------------
## In case BoolIII is True the UCCs should be assigned to the next higher
## category so that we have CPI information. This ensures that all UCC in the
## concordance files will at least have a CPI counterpart. The next higher
## category is always given by two letters. Create a column with the first two
## letters of item_id. All first two letters are followed by numbers.
## These first two letters give the 'expenditure class'.
# -----------------------------------------------------------------------------


# drop the second of the two following item_ids without match in CPI
con["BoolIV"] = ""
for i in range(0, len(con)):
    if con.BoolIII.iloc[i]:
        if con.BoolIII.iloc[i + 1]:
            con.BoolIV.iloc[i + 1] = True

con = con[con.BoolIV != True]

reggae = re.compile("\d+")
con.index = range(0, len(con))

for i in range(0, len(con)):
    if con.BoolIII.iloc[i] == True:
        con["item_id"].iloc[i] = con["item_id"].iloc[i][:2]
    else:
        con["item_id"].iloc[i] = con["item_id"].iloc[i]

# drop superfluous columns
con = con[["item_id", "UCC"]]


# -----------------------------------------------------------------------------
## For concordance, fill up empty cells in column item_id with previous entry.
## This will match item stratum and UCC codes.
# -----------------------------------------------------------------------------


for i in range(0, len(con)):
    if re.search("(\w|\d)", con.item_id.iloc[i]):
        con.item_id.iloc[i] = con.item_id.iloc[i]
    else:
        con.item_id.iloc[i] = con.item_id.iloc[i - 1]

con = con[con.UCC != ""]
con.index = range(0, len(con))


# -----------------------------------------------------------------------------
## Derive item id from ELIs, ie. first 4 digits of ELI.
# -----------------------------------------------------------------------------


con["item_id_new"] = ""
for i in range(0, len(con)):
    con["item_id_new"].iloc[i] = con.item_id.iloc[i][:4]

con = con[["item_id_new", "UCC"]]
con.columns = ["item_id", "UCC"]


# -----------------------------------------------------------------------------
## Clean data set for duplicates.
# -----------------------------------------------------------------------------


UCC_u = pd.DataFrame(data=con.UCC.unique(), columns=["unique_UCCs"])

dups = con[con.UCC.duplicated(keep=False)]  # keep= False marks all duplicates as True
print(
    "There are",
    len(UCC_u) - 1,
    "unique UCCs in the concordance file, and",
    len(dups.UCC.unique()),
    "are reported more than once.",
)


# -----------------------------------------------------------------------------
## Drop dupplicates in terms of item_id and UCC. They exist because
## on ELI level they are indeed no duplicates but as we cannot differentiate
## between them on item-stratum we can pick one randomly.
# -----------------------------------------------------------------------------


con["dup"] = con.duplicated()
con = con[["item_id", "UCC"]][con.dup == False]
con.index = range(0, len(con))


# -----------------------------------------------------------------------------
## For those items where only the UCC is a duplicate match the UCC to the
## respective expenditure class.
# -----------------------------------------------------------------------------


con["dupsII"] = con.UCC.duplicated(keep=False)

reggae = re.compile("\d+")

for i in range(0, len(con)):
    if con.dupsII.iloc[i]:
        con["item_id"].iloc[i] = reggae.split(con["item_id"].iloc[i])[0]

con["dup"] = con[["item_id", "UCC"]].duplicated()
con = con[["item_id", "UCC"]][con.dupsII == False]

assert len(con) == len(con.UCC.unique())
print(
    "There are no UCC duplicates in the WC-concordance file. All expenditures \
will be assigned a unique price level."
)


# ------------------------------------------------------------------------
## Save files
# ------------------------------------------------------------------------


def save_con_data(file):
    file.to_pickle(ppj("OUT_DATA_CON_PREP", "WC_con"))


if __name__ == "__main__":
    data = con
    save_con_data(data)
