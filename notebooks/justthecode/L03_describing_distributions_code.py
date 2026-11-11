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

    ## Session 3, the code on its own: describing a distribution

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L03_describing_distributions.py`. The session notebook uses a slider written for it, which you will not have when you work on
    your own data. Each section below does one
    of the session's computations with only pandas and matplotlib, starting from a data frame, so that
    you can copy it into your project or another notebook. The data are the data science salaries from
    session 3, with one row for each reported salary.

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
def load_salaries(course_parquet):
    salaries = course_parquet("ds_salaries.parquet")
    salaries.head()
    return (salaries,)


@app.cell(hide_code=True)
def histogram_intro(mo):
    mo.md(r"""
    ---
    ## A histogram with the mean and median

    In the cell below, we draw a histogram of one column with vertical lines at its mean and its
    median, which shows how far apart the two are when the distribution has a long tail. To use it
    on other data, you would change the column and the labels.
    """)
    return


@app.cell
def histogram_code(plt, salaries):
    # Uses: import matplotlib.pyplot as plt
    _values = salaries["salary_in_usd"]
    _fig, _ax = plt.subplots(figsize=(8, 3.5))
    _ax.hist(_values, bins=40, color="#4c72b0", edgecolor="white")
    _ax.axvline(_values.median(), color="#c44e52", linewidth=2, label="median")
    _ax.axvline(_values.mean(), color="#dd8452", linewidth=2, label="mean")
    _ax.set_xlabel("salary_in_usd")
    _ax.set_ylabel("rows")
    _ax.legend()
    _fig
    return


@app.cell(hide_code=True)
def quantiles_intro(mo):
    mo.md(r"""
    ---
    ## Quantiles and the rows in the tail

    In the cell below, we print a set of quantiles, which describe a skewed distribution better than
    the mean and standard deviation do, and then list the rows above a cutoff so that you can read
    the records that make up the tail before deciding what to say about them.
    """)
    return


@app.cell
def quantiles_code(salaries):
    _values = salaries["salary_in_usd"]
    print(_values.quantile([0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).round(0))
    print()
    _cutoff = 250_000
    salaries[_values >= _cutoff].sort_values("salary_in_usd")
    return


@app.cell(hide_code=True)
def splits_intro(mo):
    mo.md(r"""
    ---
    ## The same summary for each group

    In the cell below, we compute the count, median and maximum separately for each group, first
    for a group made from a condition on one column and then for the values of another column.
    Putting the count beside each median shows how many rows each one comes from.
    """)
    return


@app.cell
def splits_code(salaries):
    _in_us = salaries["employee_residence"].eq("US").map({True: "US", False: "everywhere else"})
    print(salaries.groupby(_in_us)["salary_in_usd"].agg(["count", "median", "max"]))
    print()
    print(salaries.groupby("work_year")["salary_in_usd"].agg(["count", "median", "max"]))
    return


if __name__ == "__main__":
    app.run()
