# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
#     "statsmodels>=0.14",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 14, the code on its own: a permutation test and a regression on a log scale

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L14_interview_loop.py`. Each section below does one
    of the session's computations with only pandas, NumPy and statsmodels, starting from a data frame, so that
    you can copy it into your project or another notebook. The data are the data science salaries from
    sessions 3, 6 and 14, with one row for each reported salary.

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
    import statsmodels.formula.api as smf

    return mo, np, pd, smf


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
def permutation_intro(mo):
    mo.md(r"""
    ---
    ## A two-sample permutation test

    In the cell below, we compute the difference between the means of two groups, then put the two
    groups' values together, shuffle them and divide them again into groups of the original sizes
    5,000 times, and report the share of shuffles whose difference is at least as far from zero as
    the observed one, which is the two-tailed p-value. To use it on other data, you would change
    the two arrays `_a` and `_b`.
    """)
    return


@app.cell
def permutation_code(np, salaries):
    # Uses: import numpy as np
    _a = salaries.loc[salaries["work_year"] == 2021, "salary_in_usd"].to_numpy()
    _b = salaries.loc[salaries["work_year"] == 2022, "salary_in_usd"].to_numpy()
    _observed = _b.mean() - _a.mean()
    _pooled = np.concatenate([_a, _b])
    _rng = np.random.default_rng(385)
    _shuffled = []
    for _ in range(5000):
        _mixed = _rng.permutation(_pooled)
        _shuffled.append(_mixed[len(_a):].mean() - _mixed[:len(_a)].mean())
    print(f"difference {_observed:,.0f}, "
          f"two-tailed p-value {(np.abs(_shuffled) >= abs(_observed)).mean():.3f}")
    return


@app.cell(hide_code=True)
def log_intro(mo):
    mo.md(r"""
    ---
    ## A regression on the log of a skewed outcome

    In the cell below, we fit the log of salary on the year as categories and turn the coefficient
    for 2022 and its confidence interval back into a percentage difference from the first year,
    with `exp(b) - 1`. On a log scale, a coefficient is a ratio rather than a difference in dollars,
    which suits an outcome with a long right tail. To use it on other data, you would change the
    formula and the name of the coefficient, which `params` lists.
    """)
    return


@app.cell
def log_code(np, salaries, smf):
    # Uses: import numpy as np
    #       import statsmodels.formula.api as smf
    _model = smf.ols("np.log(salary_in_usd) ~ C(work_year)", data=salaries).fit()
    print(_model.params.round(3))
    print()
    _name = "C(work_year)[T.2022]"
    _low, _high = _model.conf_int().loc[_name]
    print(f"2022 against 2020: {np.exp(_model.params[_name]) - 1:+.0%}, "
          f"95% CI [{np.exp(_low) - 1:+.0%}, {np.exp(_high) - 1:+.0%}]")
    return


if __name__ == "__main__":
    app.run()
