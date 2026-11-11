# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
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

    ## Session 5, the code on its own: missing values and implausible values

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L05_missingness.py`. The session notebook uses a dropdown written for it, which you will not have when you work on
    your own data. Each section below does one
    of the session's computations with only pandas, starting from a data frame, so that
    you can copy it into your project or another notebook. The data are the 2014 survey of mental health in the
    technology industry from session 5, with one row for each respondent.

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
def load_survey(course_csv):
    survey = course_csv("survey.csv").drop(columns=["comments"])
    survey.head()
    return (survey,)


@app.cell(hide_code=True)
def blanks_intro(mo):
    mo.md(r"""
    ---
    ## Where the blanks are

    In the cell below, we count the blanks in every column and their share of the rows, keeping the
    columns that have any, and then list one column's values with the blanks counted alongside them
    by `dropna=False`.
    """)
    return


@app.cell
def blanks_code(pd, survey):
    # Uses: import pandas as pd
    _blanks = pd.DataFrame({"blank": survey.isna().sum(),
                            "blank_pct": (100 * survey.isna().mean()).round(1)})
    print(_blanks[_blanks["blank"] > 0].sort_values("blank", ascending=False))
    print()
    print(survey["work_interfere"].value_counts(dropna=False))
    return


@app.cell(hide_code=True)
def by_group_intro(mo):
    mo.md(r"""
    ---
    ## Blanks in one column, for each group in another

    Blanks that are much more common in one group than in another often have an explanation in how
    the data were collected. In the cell below, we compute the share of blanks in one column for each value of another, beside the number
    of rows in each group. To use it on other data, you would change the two columns.
    """)
    return


@app.cell
def by_group_code(pd, survey):
    # Uses: import pandas as pd
    _group = survey["Country"].eq("United States").map({True: "US", False: "not US"})
    pd.DataFrame({
        "rows": survey.groupby(_group).size(),
        "state blank (%)": (100 * survey["state"].isna().groupby(_group).mean()).round(1),
    })
    return


@app.cell(hide_code=True)
def range_intro(mo):
    mo.md(r"""
    ---
    ## Values outside a plausible range

    In the cell below, we list the rows whose age falls outside 16 to 80, with a few other columns
    to help judge each one, and then compute one share two ways: with the blanks left out of the
    denominator and with them counted as "no". The two numbers differ, and which one to report
    depends on what the blanks mean.
    """)
    return


@app.cell
def range_code(survey):
    print(survey.loc[~survey["Age"].between(16, 80), ["Age", "Country", "Gender"]])
    print()
    _yes = survey["work_interfere"].isin(["Often", "Sometimes"]).sum()
    print(f"blanks left out: {_yes / survey['work_interfere'].notna().sum():.1%}")
    print(f"blanks counted as no: {_yes / len(survey):.1%}")
    return


if __name__ == "__main__":
    app.run()
