# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
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

    ## Session 4, the code on its own: a trend, split by group

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L04_visual_reasoning.py`. The session notebook uses a dropdown written for it, which you will not have when you work on
    your own data. Each section below does one
    of the session's computations with only pandas and matplotlib, starting from a data frame, so that
    you can copy it into your project or another notebook. The data are the heights of Summer Olympic
    athletes from session 4, with one row for each athlete's entry in an event.

    Each code cell starts with a comment listing the imports it uses, and its variable names start
    with `_`, which keeps them local to the cell, so you can paste a cell anywhere in a marimo
    notebook without a clash with names in other cells.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd

    return mo, pd, plt


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
def load_olympics(course_parquet):
    olympics = course_parquet("olympic_heights.parquet")
    olympics.head()
    return (olympics,)


@app.cell(hide_code=True)
def coverage_intro(mo):
    mo.md(r"""
    ---
    ## How much of each period was recorded

    Before computing a mean for each decade, we count how many rows in each decade have a value at
    all. In the cell below, we make a decade column from the year and count, for each decade, the
    rows, the rows with a height, and the share recorded. `count` leaves out missing
    values and `size` does not.
    """)
    return


@app.cell
def coverage_code(olympics):
    _decades = olympics.assign(decade=(olympics["year"] // 10) * 10)
    _table = _decades.groupby("decade").agg(rows=("height_cm", "size"),
                                            recorded=("height_cm", "count"))
    _table.assign(recorded_pct=(100 * _table["recorded"] / _table["rows"]).round(1))
    return


@app.cell(hide_code=True)
def trend_intro(mo):
    mo.md(r"""
    ---
    ## A trend for everyone and for each group

    In the cell below, we plot the mean height for each decade, first for everyone together and
    then for each sex separately on the same axes. When the groups' shares of the rows change over
    time, the pooled line can move even where no group's line does. To use it on other data, you
    would change the column you group by.
    """)
    return


@app.cell
def trend_code(olympics, plt):
    # Uses: import matplotlib.pyplot as plt
    _measured = olympics.dropna(subset=["height_cm"]).assign(
        decade=lambda _d: (_d["year"] // 10) * 10)
    _fig, _ax = plt.subplots(figsize=(8, 3.5))
    _pooled = _measured.groupby("decade")["height_cm"].mean()
    _ax.plot(_pooled.index, _pooled.to_numpy(), marker="o", color="black", label="everyone")
    for _group, _rows in _measured.groupby("sex"):
        _line = _rows.groupby("decade")["height_cm"].mean()
        _ax.plot(_line.index, _line.to_numpy(), marker="o", label=_group)
    _ax.set_xlabel("decade")
    _ax.set_ylabel("mean height_cm")
    _ax.legend()
    _fig
    return


@app.cell(hide_code=True)
def share_intro(mo):
    mo.md(r"""
    ---
    ## Each group's share over time

    In the cell below, we compute each group's share of the measured rows in each decade with
    `pd.crosstab` and `normalize="index"`, so that each row of the table adds up to 1.
    """)
    return


@app.cell
def share_code(olympics, pd):
    # Uses: import pandas as pd
    _measured = olympics.dropna(subset=["height_cm"])
    pd.crosstab((_measured["year"] // 10) * 10, _measured["sex"], normalize="index").round(3)
    return


if __name__ == "__main__":
    app.run()
