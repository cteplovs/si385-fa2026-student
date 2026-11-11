# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 8, the code on its own: sampling, uncertainty and the bootstrap

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L08_sampling_and_uncertainty.py`. The session
    notebook uses a dropdown and functions written for it, which you will not have when you work on
    your own data. Each section below does one of the session's computations with only pandas and
    NumPy, starting from a data frame, so that you can copy it into your project or another
    notebook. The data are the NBA free-throw trips from session 8, with one row for each pair of
    free throws.

    Each code cell starts with a comment listing the imports it uses, and its variable names start
    with `_`, which keeps them local to the cell, so you can paste a cell anywhere in a marimo
    notebook without a clash with names in other cells.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import numpy as np
    import pandas as pd

    return mo, np, pd


@app.cell(hide_code=True)
def data_helper(pd):
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    REMOTE = ("https://raw.githubusercontent.com/"
              "cteplovs/si385-fa2026-student/main/data/")


    def course_parquet(name):
        """Read one of the course Parquet files.

        The copy in the course folder is the one to prefer, and it is what you get if you are
        running this the documented way. The fallback to the public repository is there so that
        the notebook also runs on molab, provided you have a network.
        """
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_parquet(local)
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as response:
            return pd.read_parquet(BytesIO(response.read()))

    return (course_parquet,)


@app.cell
def load_trips(course_parquet):
    trips = course_parquet("nba_free_throw_pairs.parquet")
    trips.head()
    return (trips,)


@app.cell(hide_code=True)
def split_intro(mo):
    mo.md(r"""
    ---
    ## One outcome split by another

    In the cell below, we split the second shot by the result of the first and compute the number
    of trips and the share of second shots made in each group. The mean of a column of `True` and
    `False` values is the share that are `True`.
    """)
    return


@app.cell
def split_code(trips):
    trips.groupby("first_made")["second_made"].agg(trips="size", share_made="mean").round(3)
    return


@app.cell(hide_code=True)
def summary_intro(mo):
    mo.md(r"""
    ---
    ## A summary for each group

    In the cell below, we compute one row for each player: the number of trips, the number of
    first shots missed, and the free-throw percentage over both shots, sorted by the number of
    trips. To use it on other data, you would change the column you group by and the columns you
    summarize.
    """)
    return


@app.cell
def summary_code(trips):
    _by_player = trips.groupby("player").agg(
        trips=("first_made", "size"),
        first_made=("first_made", "sum"),
        second_made=("second_made", "sum"),
    )
    _by_player.assign(
        missed_first=_by_player["trips"] - _by_player["first_made"],
        ft_pct=(100 * (_by_player["first_made"] + _by_player["second_made"])
                / (2 * _by_player["trips"])).round(1),
    ).sort_values("trips", ascending=False).head(10)
    return


@app.cell(hide_code=True)
def bootstrap_intro(mo):
    mo.md(r"""
    ---
    ## A bootstrap interval

    In the cell below, we compute a statistic for one set of rows, here the gap between the
    second-shot percentage after a make and after a miss, then draw the same number of rows with
    replacement 2,000 times, compute the statistic for each resample, and take the 5th and 95th
    percentiles as a 90% interval. To use it on other data, you would change the rows and the
    statistic in `_statistic`.

    This resamples rows, which assumes that the rows are independent of one another. When they
    come in groups, such as several trips by the same player, the resampling has to draw whole
    groups instead, as the session's exercise did.
    """)
    return


@app.cell
def bootstrap_code(np, trips):
    # Uses: import numpy as np
    def _statistic(rows):
        after_make = rows.loc[rows["first_made"], "second_made"].mean()
        after_miss = rows.loc[~rows["first_made"], "second_made"].mean()
        return 100 * (after_make - after_miss)

    _rows = trips[trips["player"] == "LeBron James"]
    _rng = np.random.default_rng(385)
    _resampled = [_statistic(_rows.sample(n=len(_rows), replace=True, random_state=_rng))
                  for _ in range(2000)]
    _low, _high = np.percentile(_resampled, [5, 95])
    print(f"statistic {_statistic(_rows):.1f}, 90% interval {_low:.1f} to {_high:.1f}")
    return


if __name__ == "__main__":
    app.run()
