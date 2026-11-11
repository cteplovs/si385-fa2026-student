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

    ## Session 6, the code on its own: conditioning a comparison

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L06_multivariate.py`. The session notebook uses a dropdown written for it, which you will not have when you work on
    your own data. Each section below does one
    of the session's computations with only pandas, starting from a data frame, so that
    you can copy it into your project or another notebook. The data are the data science salaries from sessions 3
    and 6, with one row for each reported salary.

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
def load_salaries(course_parquet):
    salaries = course_parquet("ds_salaries.parquet")
    salaries.head()
    return (salaries,)


@app.cell(hide_code=True)
def pooled_intro(mo):
    mo.md(r"""
    ---
    ## A pooled comparison

    In the cell below, we compute the number of rows and the median salary for each value of one
    column, with every other column pooled.
    """)
    return


@app.cell
def pooled_code(salaries):
    salaries.groupby("remote_ratio")["salary_in_usd"].agg(rows="size", median="median").round(0)
    return


@app.cell(hide_code=True)
def conditioned_intro(mo):
    mo.md(r"""
    ---
    ## The same comparison, conditioned on a third column

    In the cell below, we compute the median and the number of rows for each combination of the
    column we compare and the column we condition on, with `pivot_table`, and put the two tables
    side by side. A comparison that holds within each group of the third column is stronger
    evidence than the pooled one, and the counts show which cells have too few rows to read. To
    condition on something else, you would change `_condition`.
    """)
    return


@app.cell
def conditioned_code(pd, salaries):
    # Uses: import pandas as pd
    _condition = "company_size"
    _median = salaries.pivot_table(index="remote_ratio", columns=_condition,
                                   values="salary_in_usd", aggfunc="median").round(0)
    _rows = salaries.pivot_table(index="remote_ratio", columns=_condition,
                                 values="salary_in_usd", aggfunc="size")
    pd.concat({"median": _median, "rows": _rows}, axis=1)
    return


@app.cell(hide_code=True)
def derived_intro(mo):
    mo.md(r"""
    ---
    ## Conditioning on a column you make

    In the cell below, we make a two-valued column from a condition on another, US company or not,
    and condition on that instead.
    """)
    return


@app.cell
def derived_code(salaries):
    _with_us = salaries.assign(
        us=salaries["company_location"].eq("US").map({True: "US", False: "not US"}))
    _with_us.pivot_table(index="remote_ratio", columns="us", values="salary_in_usd",
                         aggfunc=["median", "size"]).round(0)
    return


if __name__ == "__main__":
    app.run()
