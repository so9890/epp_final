"""Prepare BLS concordance file and merge to the prepared CPI file.

Ensure item id in BLS concordance file 'concordance_BLS.xlsx' is on same 
level as item id used in CPI data, ie. go derive item-stratum id from ELI. 
Ensure that the concordance file does not contain duplicates in terms of UCCs 
and item-stratum id. If UCCs are merged to different item-ids within the same 
expenditure class match UCC to expenditure class. In case UCCs are matched to 
different expenditure classes choose one arbitrarily. Expenditure class is in 
price level hierarchie one step above item_stratum.

Return concordance file that matches each UCC to one item-stratum/expenditure
class id that is given in the CPI data set.

"""

import pandas as pd
import re

from bld.project_paths import project_paths_join as ppj

# -----------------------------------------------------------------------------
## Read in data.
# -----------------------------------------------------------------------------


d_CPI = pd.read_pickle(ppj("OUT_DATA_CPI_CLEARED", "CPI_for_con"))
con_bls = pd.read_excel(ppj("IN_DATA_CON", "concordance_BLS.xlsx"), header=3, usecols="A:D")


# -----------------------------------------------------------------------------
## Extract first 4 digits from ELI which give the item-stratum id.
## Drop duplicates in terms of derived item-stratum id and UCC.
# -----------------------------------------------------------------------------


con_bls["item_id"] = ""
for i in range(0, len(con_bls)):
    con_bls["item_id"].iloc[i] = con_bls.ELI.iloc[i][:4]

con_bls["dup"] = con_bls.duplicated(["UCC", "item_id"])
con_bls = con_bls[~con_bls.dup]
con_bls.index = range(0, len(con_bls))


# -----------------------------------------------------------------------------
## Match UCCs reported more than once in the con_bls file to their expenditure
## class if that is the same. Some UCCs also matched to different exp. classes,
## arbitrarily choose one. Test for remaining duplicates. Stop code from
## runnning if any duplicate in terms of UCC remained.
# -----------------------------------------------------------------------------


UCC_u = pd.DataFrame(data=con_bls.UCC.unique(), columns=["unique_UCCs"])

dups = con_bls[con_bls.UCC.duplicated(keep=False)]  # keep= False marks all duplicates as True
print(
    "There are",
    len(UCC_u),
    "unique UCCs in the concordance file, and",
    len(dups.UCC.unique()),
    "are reported more then once.",
)

con_bls["dupsII"] = con_bls.UCC.duplicated(keep=False)

reggae = re.compile("\d+")
con_bls["exp_class"] = ""
for i in range(0, len(con_bls)):
    if con_bls.dupsII.iloc[i]:
        con_bls["exp_class"].iloc[i] = reggae.split(con_bls["item_id"].iloc[i])[0]


con_bls["Bool"] = con_bls.duplicated(["UCC", "exp_class"], keep=False)

for i in range(0, len(con_bls)):
    if con_bls.Bool.iloc[i]:
        con_bls["item_id"].iloc[i] = con_bls["exp_class"].iloc[i]

# Drop duplicates.
con_bls["dupIII"] = con_bls.duplicated(["UCC", "item_id"])
con_bls = con_bls[~con_bls.dupIII]
con_bls.index = range(0, len(con_bls))

# For all remaining duplicates in terms of UCC.
con_bls["dupsIV"] = con_bls.UCC.duplicated(keep=False)
# there are only 15 UCCs that have duplicates.

# Pick one item stratum randomly.
con_bls = con_bls[~con_bls.UCC.duplicated()]

# Test for remaining duplicates in terms of UCC.
con_bls["dupsV"] = con_bls.UCC.duplicated(keep=False)
s = con_bls[["dupsV", "UCC"]][con_bls.dupsV]

assert len(s.UCC.unique()) == 0
print("There are", len(s.UCC.unique()), "duplicates left in the concordance file.")

# Clean concordance file.
con_bls = con_bls[["item_id", "UCC"]]


# -----------------------------------------------------------------------------
## Save data set.
# -----------------------------------------------------------------------------


def save_con_data(file):
    file.to_pickle(ppj("OUT_DATA_CON_PREP", "BLS_con"))


if __name__ == "__main__":
    data = con_bls
    save_con_data(data)
