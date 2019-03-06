"""Plot real expenditures for poorest and richest households over time.

Create data set containing time series of expenditures for the richest 10% and 
the poorest 10% (mean) using common deflation method and alternative one based 
on household-specific CPI. The resulting figures are saved to 'bld/out/figures'.

"""

import pandas as pd
import matplotlib.pyplot as plt

from bld.project_paths import project_paths_join as ppj


# ------------------------------------------------------------------------
## Read in data.
# ------------------------------------------------------------------------


real_exp_10_agg_cpi = pd.read_pickle(ppj("IN_DATA_GRAPH", "agg_cpi_exp_series_p10"))
real_exp_90_agg_cpi = pd.read_pickle(ppj("IN_DATA_GRAPH", "agg_cpi_exp_series_p90"))
real_exp_10 = pd.read_pickle(ppj("IN_DATA_GRAPH", "exp_series_p10"))
real_exp_90 = pd.read_pickle(ppj("IN_DATA_GRAPH", "exp_series_p90"))


data = {"real_90_agg": real_exp_90_agg_cpi, "real_10": real_exp_10, "real_90": real_exp_90}


# ------------------------------------------------------------------------
## Sort data and save as one data frame.
# ------------------------------------------------------------------------


df_sorted = real_exp_10_agg_cpi.sort_values(["year", "month"])
for t in data.keys():
    df_sorted = pd.merge(df_sorted, data[t], on=["year", "month"])

df_sorted["time"] = df_sorted[["year", "month"]].apply(lambda x: "/".join(x), axis=1)


# ------------------------------------------------------------------------
## Plot data and save figures:
## 1) compare methods using different CPIs (household-specific vs. aggregate)
## 2) compare rich vs. poor.
# ------------------------------------------------------------------------


# 1) Household-specific vs. aggregate CPI for rich and poor.
def plot_agg_het(df_sorted):
    for t in [2, 3]:
        plt.plot(
            df_sorted["time"],
            df_sorted.T.iloc[t],
            "--",
            label="Aggregate CPI ",
            color="orange",
            linewidth=2,
            scalex=False,
        )
        plt.plot(
            df_sorted["time"],
            df_sorted.T.iloc[t + 2],
            "--",
            label="Heterogeneous CPI",
            color="blue",
        )
        plt.legend(loc=8)
        plt.xticks(df_sorted["time"][::8], rotation=70)
        plt.xlabel("Time")
        plt.ylabel("Real Consumption")

        # save plot and clean figure
        plt.savefig(
            ppj("OUT_FIGURES", "comparison_agg_vs_het_" + df_sorted.columns[t][-7:-4]),
            bbox_inches="tight",
        )
        plt.clf()


# 2) Compare rich vs. poor for aggregate and heterogeneous CPI.
def plot_rich_poor(df_sorted):
    for c in range(2, 5, 2):
        plt.plot(
            df_sorted["time"],
            df_sorted.T.iloc[c],
            "--",
            label="Poor ",
            color="orange",
            linewidth=2,
            scalex=False,
        )
        plt.plot(df_sorted["time"], df_sorted.T.iloc[c + 1], "--", label="Rich", color="blue")
        plt.legend(loc=8)
        plt.xticks(df_sorted["time"][::8], rotation=70)
        plt.xlabel("Time")
        plt.ylabel("Real Consumption")

        # save plot and clean figure
        if c == 2:
            plt.savefig(ppj("OUT_FIGURES", "agg_rich_vs_poor"), bbox_inches="tight")
        else:
            plt.savefig(ppj("OUT_FIGURES", "het_rich_vs_poor"), bbox_inches="tight")
        plt.clf()


if __name__ == "__main__":
    data = df_sorted
    plot_agg_het(data)
    plot_rich_poor(data)
