"""Prepar CPI data for merger with concordance files.

Read in data and save into one CPI data set. Clean data to only contain 
US city average information, seasonally unadjusted and monthly data. Derive 
concordance id from variable 'series_id' that will be used to merge concordance 
files. Drop too broad price categories, ie. those with 'SA' in item code. Use 
file 'ELIconcordance_NS.xls' to replace old CPI item codes (from 1988) with 
those that are given in the concordance file which is based on 2015 codes.

Save data set containing CPI data and concordance id as 'CPI_for_con' to 
'bld/out/data/CPI_prepared'.

"""

import pandas as pd
import re

from bld.project_paths import project_paths_join as ppj


# -----------------------------------------------------------------------------
## Create a list for the excel files containing CPI data and merge to one.
# -----------------------------------------------------------------------------


file_names = [
    "food_and_beverages",
    "USApparel",
    "USCommoditiesServicesSpecial",
    "USEducationandCommunication",
    "UShousing",
    "USMedical",
    "USOtherGoodsAndServices",
    "USRecreation",
    "USTransportation",
]

data = pd.read_table(ppj("IN_DATA_CPI", "food_and_beverages.txt"))

for i in file_names[1:]:
    data_helper = pd.read_table(ppj("IN_DATA_CPI", str(i) + ".txt"))
    ## ensure same column names
    data_helper.columns = data.columns
    data = pd.concat([data, data_helper], sort=False)

del data_helper


# -----------------------------------------------------------------------------
## Ensure relevant variables to be of one type.
# -----------------------------------------------------------------------------


data.year = data.year.astype(int)
data.series_id = data.series_id.astype(str)
data.value = data.value.astype(float)


# -----------------------------------------------------------------------------
## Clean data set.
## Only keep US city average prices, ie area_code==0000,
## seasonal code (ie. 3rd letter)==U (not seasonally adjusted)
## periodicity code (ie. 4th letter)==R (monthly level)
# -----------------------------------------------------------------------------


# area-code
data = data[data["series_id"].str.contains("0000")]

# seasonal-code
unique_SID = pd.DataFrame(data=data.series_id.unique(), columns=["series_id"])

unique_SID["Bool_seasonal"] = ""
for i in range(0, len(unique_SID)):
    if unique_SID["series_id"].iloc[i][2] == "U":
        unique_SID["Bool_seasonal"].iloc[i] = True
    else:
        unique_SID["Bool_seasonal"].iloc[i] = False

unique_SID = unique_SID[unique_SID.Bool_seasonal]

# periodicity-code
unique_SID["Bool_period"] = ""
for i in range(0, len(unique_SID)):
    if unique_SID["series_id"].iloc[i][3] == "R":
        unique_SID["Bool_period"].iloc[i] = True
    else:
        unique_SID["Bool_period"].iloc[i] = False

unique_SID = unique_SID[unique_SID.Bool_period]


# -----------------------------------------------------------------------------
## Derive concordance id that can be merged to concordance files from the
## variable series_id.
# -----------------------------------------------------------------------------


regexI = re.compile("[0]{4}")
unique_SID["item_id"] = ""

regexIII = re.compile("^SE{1}?|^SS{1}?")
unique_SID["concordance_id"] = ""

for i in range(0, len(unique_SID)):
    t = regexI.split(unique_SID["series_id"].iloc[i])
    unique_SID["item_id"].iloc[i] = t[1].strip()

    if len(regexIII.split(unique_SID["item_id"].iloc[i])) > 1:
        unique_SID["concordance_id"].iloc[i] = regexIII.split(unique_SID["item_id"].iloc[i])[1]
    else:
        unique_SID["concordance_id"].iloc[i] = ""

# drop item_id with SA, which is too broad a category
unique_SID = unique_SID[unique_SID.concordance_id != ""]


# -----------------------------------------------------------------------------
## Use ELI concordance file from Nakamura and Steinsson to deal with changes in
## the item_id in the CPI files over time:
## The CPI file contains identifiers used in 1988. The concordance files are
## based on 2015 codes.
# -----------------------------------------------------------------------------


NS_concordance = pd.read_excel(
    ppj("IN_DATA_CON", "ELIconcordance_NS.xls"), sheet_name=2, header=0, usecols="A:C"
)
NS_concordance["eli88"] = NS_concordance.eli88.astype(str)

# 4 digit codes in concordance_id have a leading 0 but not in eli88
for i in range(0, len(NS_concordance)):
    if len(NS_concordance.eli88.iloc[i]) == 4:
        NS_concordance["eli88"].iloc[i] = str(0) + NS_concordance["eli88"].iloc[i]

# test for duplicates in NS_concordance file
assert len(NS_concordance.eli88.duplicated().unique()) == 1
NS_concordance["eli98_dups"] = NS_concordance.eli98.duplicated()

print(
    "There are no duplicates in the NS_concordance file in terms of variable\
'eli88', which is the right_on key. But there are",
    len(NS_concordance.eli98[NS_concordance.eli98.duplicated()].unique()),
    " in terms of 'eli98'. Drop duplicates to avoid duplicates in final data set! ",
)

NS_concordance = NS_concordance[NS_concordance["eli98_dups"] == False]

# merge to unique_SID file
unique_SID = unique_SID.merge(
    NS_concordance, left_on="concordance_id", right_on="eli88", how="left", validate="1:1"
)

# replace concordance_id by eli98 if exists
for i in range(0, len(unique_SID)):
    if pd.isna(unique_SID.eli88.iloc[i]):
        unique_SID["concordance_id"].iloc[i] = unique_SID["concordance_id"].iloc[i]
    else:
        unique_SID["concordance_id"].iloc[i] = unique_SID["eli98"].iloc[i]

# -----------------------------------------------------------------------------
## Merge concordance id to main data set.
# -----------------------------------------------------------------------------


data = data.merge(
    unique_SID[["series_id", "concordance_id"]],
    left_on="series_id",
    right_on="series_id",
    how="left",
    validate="m:1",
)

# only keep items in price data set that have a concordance_id
data = data[~pd.isna(data.concordance_id)]

# check for duplicates in terms of concordance_id, year and period
dups = data.duplicated(["concordance_id", "year", "period"], keep=False)

assert len(dups.unique()) == 1
print("There are no duplicates in the final CPI file in terms of concordance_id, year and period.")


# ------------------------------------------------------------------------
## Only keep data for years from 1995/12 onwards. CEX data at the moment not
## available for earlier years.
# ------------------------------------------------------------------------

data = data[data.year.astype(int).isin(range(1995, 2018, 1))]


# ------------------------------------------------------------------------
## Save files.
# ------------------------------------------------------------------------


def save_data(file):
    file.to_pickle(ppj("OUT_DATA_CPI_CLEARED", "CPI_for_con"))


if __name__ == "__main__":
    data_con = data
    save_data(data)
