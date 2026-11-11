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

    ## Session 11, the code on its own: contingency tables and the chi-square test

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L11_chi_square.py`. The session notebook uses a
    dropdown written for it, which you will not have when you work on your own data. Each section
    below does one of the session's computations with only pandas and NumPy, starting from a data
    frame, so that you can copy it into your project or another notebook. The data are the 2018
    Central Park Squirrel Census from session 11, with one row for each sighting.

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
def load_squirrels(course_csv):
    squirrels = (course_csv("nyc_squirrels.csv")
                 .dropna(subset=["primary_fur_color"])
                 .reset_index(drop=True))
    squirrels["primary_fur_color"].value_counts()
    return (squirrels,)


@app.cell(hide_code=True)
def table_intro(mo):
    mo.md(r"""
    ---
    ## A contingency table

    In the cell below, we count the sightings for each combination of fur colour and one
    behaviour with `pd.crosstab`, with the totals in the margins, and then give the same table as
    shares of each row, which is each colour's rate. To use it on other data, you would change the
    two columns.
    """)
    return


@app.cell
def table_code(pd, squirrels):
    # Uses: import pandas as pd
    print(pd.crosstab(squirrels["primary_fur_color"], squirrels["running"], margins=True))
    print()
    print(pd.crosstab(squirrels["primary_fur_color"], squirrels["running"],
                      normalize="index").round(3))
    return


@app.cell(hide_code=True)
def chi_intro(mo):
    mo.md(r"""
    ---
    ## The chi-square statistic and a resampling test

    In the cell below, we compute Pearson's chi-square statistic for the table, with each cell's
    expected count computed from its row and column totals, which works when the groups have
    different sizes. Then, as in the reading, we shuffle the behaviour column among the sightings
    2,000 times, recompute the statistic each time, and report the share of shuffles at least as
    large as the real one, which is the p-value.
    """)
    return


@app.cell
def chi_code(np, pd, squirrels):
    # Uses: import numpy as np
    #       import pandas as pd
    def _chi_square(groups, outcome):
        observed = pd.crosstab(groups, outcome).to_numpy()
        expected = np.outer(observed.sum(axis=1), observed.sum(axis=0)) / observed.sum()
        return float(((observed - expected) ** 2 / expected).sum())

    _groups = squirrels["primary_fur_color"].to_numpy()
    _outcome = squirrels["running"].to_numpy()
    _observed = _chi_square(_groups, _outcome)
    _rng = np.random.default_rng(385)
    _shuffled = np.array([_chi_square(_groups, _rng.permutation(_outcome)) for _ in range(2000)])
    print(f"chi-square {_observed:.2f}, p-value {(_shuffled >= _observed).mean():.3f}")
    return


if __name__ == "__main__":
    app.run()
