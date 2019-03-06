"""Test functions used in project 'epp_all'."""

import sys
import pandas as pd
import pytest

from data_function.functions import _cum_distribution, weights_percentiles
from numpy.testing import assert_array_almost_equal, assert_array_equal


###############################################################################

"""1) Test function to derive cummulative distribution function '_cum_distribution'.

This test asserts that the weights and percentages assigned to 
each household are correct. It all derived percentages.

"""

# Fix starting values and expected output.
@pytest.fixture
def setup_fun():

    out = {}
    out["d"] = pd.DataFrame(
        data=[
            [-10, -10, 2, 3, 5, 3, -4, 0, 1, 1, 1, 7, 8.565_564, 8.565_565, 8.565_565, 8.565_565],
            [2, 3.6, 5, 1, 3, 2, 1, 5.4, 2, 2, 2, 2, 3, 4, 3, 4],
        ],
        index=["VALUE", "FINLWT21"],
    ).T

    return out


@pytest.fixture
def expect_fun():

    out = {}
    values = [
        5.6,
        5.6,
        6.6,
        12.0,
        18.0,
        18.0,
        18.0,
        23.0,
        26.0,
        26.0,
        29.0,
        31.0,
        34.0,
        45.0,
        45.0,
        45.0,
    ]
    number_equal_obs = [
        5.6,
        5.6,
        1.0,
        5.4,
        6.0,
        6.0,
        6.0,
        5.0,
        3.0,
        3.0,
        3.0,
        2.0,
        3.0,
        11.0,
        11.0,
        11.0,
    ]
    out["d"] = pd.DataFrame(
        data=[
            values,
            [x / values[-1] for x in values],
            [x / values[-1] for x in number_equal_obs],
            [
                1,
                1,
                0.875_556,
                0.853_333,
                0.733_333,
                0.733_333,
                0.733_333,
                0.6,
                0.488_889,
                0.488_889,
                0.422_222,
                0.355_556,
                0.311_111,
                0.244_444,
                0.244_444,
                0.244_444,
            ],
            [1, 1, 13, 15, 27, 27, 27, 40, 52, 52, 58, 65, 69, 100, 100, 100],
        ],
        index=[
            "Cum_weights",
            "Percentage_below_equal",
            "Percentage_equal",
            "Percentage_equal_above",
            "Percentile",
        ],
    ).T

    return out


# Run tests.
def test_cum_distribution_weights(setup_fun, expect_fun):
    calc_distribution = _cum_distribution(**setup_fun)
    assert_array_equal(
        calc_distribution["Cum_weights"].values, expect_fun["d"]["Cum_weights"].values
    )


def test_cum_distribution_percentage(setup_fun, expect_fun):
    calc_distribution = _cum_distribution(**setup_fun)
    assert_array_equal(
        calc_distribution["Percentage_below_equal"].values,
        expect_fun["d"]["Percentage_below_equal"].values,
    )


def test_cum_distribution_point(setup_fun, expect_fun):
    calc_distribution = _cum_distribution(**setup_fun)
    assert_array_equal(
        calc_distribution["Percentage_equal"].values, expect_fun["d"]["Percentage_equal"].values
    )


def test_cum_distribution_equal_above(setup_fun, expect_fun):
    calc_distribution = _cum_distribution(**setup_fun)
    assert_array_almost_equal(
        calc_distribution["Percentage_equal_above"].values,
        expect_fun["d"]["Percentage_equal_above"].values,
    )


######################################################################


"""2) Test function that assignes percentiles '_percentiles'. 

To do this, it is enough to test the cummulative function 'weights_percentiles'
since it only consists of two functions, '_cum_distribution' and '_percentiles', 
of which the former is tested exhaustively above. 

"""


def test_weights_percentiles(setup_fun, expect_fun):
    calc_percentiles = weights_percentiles(**setup_fun)
    assert_array_equal(calc_percentiles["Percentile"].values, expect_fun["d"]["Percentile"].values)


if __name__ == "__main__":
    status = pytest.main([sys.argv[0]])
    sys.exit(status)
