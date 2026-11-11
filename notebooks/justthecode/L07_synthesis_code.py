# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
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

    ## Session 7, the code on its own: a first look at an unfamiliar dataset

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L07_synthesis.py`. Each section below does one
    of the session's computations with only pandas, starting from a data frame, so that
    you can copy it into your project or another notebook. The data are the College Scorecard's figures
    for bachelor's degrees from session 7, with one row for each field of study at each institution.

    Each code cell starts with a comment listing the imports it uses, and its variable names start
    with `_`, which keeps them local to the cell, so you can paste a cell anywhere in a marimo
    notebook without a clash with names in other cells.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import pandas as pd

    return mo, pd


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
def load_degrees(course_parquet):
    degrees = course_parquet("college_scorecard_bachelors.parquet")
    degrees.head()
    return (degrees,)


@app.cell(hide_code=True)
def overview_intro(mo):
    mo.md(r"""
    ---
    ## Size, types and blanks

    In the cell below, we print the number of rows and columns, then one row for each column with
    its type, its number of distinct values and its share of blanks, which is a first check on
    what each column contains.
    """)
    return


@app.cell
def overview_code(degrees, pd):
    # Uses: import pandas as pd
    print(degrees.shape)
    pd.DataFrame({
        "type": degrees.dtypes.astype(str),
        "distinct": degrees.nunique(),
        "blank_pct": (100 * degrees.isna().mean()).round(1),
    })
    return


@app.cell(hide_code=True)
def status_intro(mo):
    mo.md(r"""
    ---
    ## Why a value is missing

    In this file, each figure has a `_status` column that records why a value is blank, for
    example because too few graduates were counted. In the cell below, we count the values of one
    status column, and then describe the figure only for the rows where it was reported.
    """)
    return


@app.cell
def status_code(degrees):
    print(degrees["earn_median_1yr_status"].value_counts(dropna=False))
    print()
    degrees["earn_median_1yr"].describe().round(0)
    return


@app.cell(hide_code=True)
def compare_intro(mo):
    mo.md(r"""
    ---
    ## A comparison with its counts

    In the cell below, we compute the median of one figure for each value of a categorical column,
    with the number of rows that have the figure beside it, and sort by the median.
    """)
    return


@app.cell
def compare_code(degrees):
    (degrees.groupby("control")["earn_median_1yr"]
     .agg(rows="count", median="median")
     .sort_values("median", ascending=False)
     .round(0))
    return


if __name__ == "__main__":
    app.run()
