"""Functions of project."""

# -----------------------------------------------------------------------------
## Percentiles
# -----------------------------------------------------------------------------


def weights_percentiles(d):
    """Calculate the percentile of each household.
    
    First, derive cummulative distribution and probibility distribution functions.
    Second, assign percentiles to each household.
    Return data set that assigns each household id the corresponding percentile.
    
    Inputs:
        builds on functions 'cum_distribution' and 'percentiles'
        
    Arguments:       
        d - data set

    """
    d_distribution = cum_distribution(d)
    d_sorted = percentiles(d_distribution)

    return d_sorted


###############################################################################


def cum_distribution(d):
    """Calculate cummulative distribution function.
    
    Return sorted data set with cummulative weights, the cummulative distribution 
    function, and probability density function.

    
    Arguments:
        d - data set containing sampling weights and income for a given month-year
    
    """
    d_sorted = d.sort_values("VALUE", na_position="first")
    d_sorted.index = range(len(d_sorted))
    d_sorted["Cum_weights"] = ""

    cum_weight = 0.0
    s = 0
    number_skipped = 0
    for i in range(0, len(d_sorted)):
        # If-statement to skip those observations that have
        # had the same value as the previous one.
        if s == 0 and i == 0:
            number_skipped = 0
        else:
            number_skipped += s - 1
        j = i + number_skipped

        # This is the actual loop.
        s = 0
        while d_sorted["VALUE"].iloc[j] == d_sorted["VALUE"].iloc[j + s]:

            cum_weight += d_sorted["FINLWT21"].iloc[j + s]
            s += 1

            if j + s == len(d_sorted):  # If so, the next value to be tested would be out of range.
                break
            else:
                continue

        d_sorted["Cum_weights"].iloc[j : j + s] = cum_weight  # the end value is exlcuded!

        if j + s == len(d_sorted):
            break
        else:
            continue

    n = d["FINLWT21"].sum()
    d_sorted["Percentage_below_equal"] = d_sorted["Cum_weights"] / n

    # Calculate probability distribution and the probability to observe an income equal or bigger.
    Observations_equal = d_sorted.groupby("VALUE").agg({"VALUE": ["min"], "FINLWT21": ["sum"]})
    Observations_equal.columns = ["VALUE", "Percentage_equal"]
    Observations_equal["Percentage_equal"] = Observations_equal["Percentage_equal"] / n
    d_sorted = d_sorted.merge(Observations_equal, left_on="VALUE", right_on="VALUE", how="left")
    d_sorted["Percentage_equal_above"] = (
        1 - d_sorted["Percentage_below_equal"] + d_sorted["Percentage_equal"]
    )

    return d_sorted


###############################################################################


def percentiles(d_sorted):
    """Calculate household-specific percentiles. 
    
    Household-specific percentiles are derived from the cummulative distribution 
    and probability density function.     
    
    Arguments:
        d - data set resulting from the function '_cum_distribution'.
    
    """
    d_sorted["Percentile"] = ""
    start = 0

    for p in range(1, 101, 1):

        for i in range(start, len(d_sorted)):

            if d_sorted["Percentage_below_equal"].iloc[i] < p / 100:
                # All observations with a probability to observe equal or
                # smaller values lower then p/100 fall within the given percentile.
                d_sorted["Percentile"].iloc[i] = p

            elif (
                d_sorted["Percentage_below_equal"].iloc[i] >= p / 100
                and d_sorted["Percentage_equal_above"].iloc[i] >= 1 - p / 100
            ):
                # At the threshold, the second condition says that the
                # probability to observe an equal or higher income
                # is >= 1-p/100. This is required since the data is
                # discrete.
                d_sorted["Percentile"].iloc[i] = p

            else:
                # Since at the point of the break i is the index of the first
                # observation that has not yet been assigned a percentile.
                # This is from where the operation has to start for the next percentile.
                start = i

                break

        print("Percentile", p, "done!")

    return d_sorted
