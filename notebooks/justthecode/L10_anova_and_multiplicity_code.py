# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 10, the code on its own: comparing many groups

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L10_anova_and_multiplicity.py`. Each section below
    does one of the session's computations with only pandas and NumPy, starting from a data frame,
    so that you can copy it into your project or another notebook. The data are the *Flavors of
    Cacao* chocolate ratings from session 10, with one row for each bar.

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


    def course_csv(name, **kwargs):
        """Read one of the course data files, passing any keyword arguments to pd.read_csv.

        The copy in the course folder is the one to prefer, and it is what you get if you are
        running this the documented way. The fallback to the public repository is there so that
        the notebook also runs on molab, provided you have a network.
        """
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_csv(local, **kwargs)
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as response:
            return pd.read_csv(BytesIO(response.read()), **kwargs)

    return (course_csv,)


@app.cell
def load_bars(course_csv):
    bars = course_csv("chocolate.csv")
    bars.head()
    return (bars,)


@app.cell(hide_code=True)
def bins_intro(mo):
    mo.md(r"""
    ---
    ## Cleaning a column and dividing it into bands

    In the cell below, we turn the cocoa percentage, which is stored as text such as `"70%"`, into
    a number, and then divide it into bands with `pd.cut`. Each band includes its upper edge, so
    the band from 65 to 69 contains 66 to 69.
    """)
    return


@app.cell
def bins_code(bars, pd):
    # Uses: import pandas as pd
    _cocoa = bars["cocoa_percent"].str.rstrip("%").astype(float)
    _bands = pd.cut(_cocoa, [0, 65, 69, 72, 79, 100],
                    labels=["65% or less", "66 to 69%", "70 to 72%", "73 to 79%", "80% or more"])
    bars.assign(cocoa=_cocoa, band=_bands).groupby("band", observed=True)["rating"].agg(
        bars="count", average="mean").round(2)
    return


@app.cell(hide_code=True)
def groups_intro(mo):
    mo.md(r"""
    ---
    ## Keeping the groups with enough rows

    In the cell below, we keep the countries of bean origin with at least 30 bars, leaving out
    blends, and compute each one's number of bars and average rating, sorted from highest to
    lowest. To use it on other data, you would change the column, the minimum and the value you
    average.
    """)
    return


@app.cell
def groups_code(bars):
    _counts = bars["country_of_bean_origin"].value_counts()
    _kept = _counts[(_counts >= 30) & (_counts.index != "Blend")].index
    (bars[bars["country_of_bean_origin"].isin(_kept)]
     .groupby("country_of_bean_origin")["rating"]
     .agg(bars="count", average="mean")
     .sort_values("average", ascending=False)
     .round(2))
    return


@app.cell(hide_code=True)
def anova_intro(mo):
    mo.md(r"""
    ---
    ## A permutation ANOVA

    This is the reading's permutation ANOVA. In the cell below, we compute the variance among the
    group averages, shuffle the group labels 5,000 times, and report the share of shuffles that
    give at least as much variance as the real data. That share is the p-value for the hypothesis
    that the group makes no difference to the rating, and a small one does not show which groups
    differ.
    """)
    return


@app.cell
def anova_code(bars, np):
    # Uses: import numpy as np
    _counts = bars["country_of_bean_origin"].value_counts()
    _kept = bars[bars["country_of_bean_origin"].isin(
        _counts[(_counts >= 30) & (_counts.index != "Blend")].index)]
    _groups = _kept["country_of_bean_origin"].to_numpy()
    _values = _kept["rating"].to_numpy(dtype=float)
    _names = sorted(set(_groups))

    def _spread(labels):
        return np.var([_values[labels == _g].mean() for _g in _names], ddof=1)

    _observed = _spread(_groups)
    _rng = np.random.default_rng(385)
    _shuffled = np.array([_spread(_rng.permutation(_groups)) for _ in range(5000)])
    print(f"variance among the averages {_observed:.4f}, p-value {(_shuffled >= _observed).mean():.4f}")
    return


if __name__ == "__main__":
    app.run()
