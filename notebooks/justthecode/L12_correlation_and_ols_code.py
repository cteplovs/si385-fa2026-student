# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "pandas>=3.0.5",
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

    ## Session 12, the code on its own: correlation and ordinary least squares regression

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L12_correlation_and_ols.py`. The session notebook
    uses dropdowns and plots written for it, which you will not have when you work on your own
    data. Each section below does one of the session's computations with only pandas and
    statsmodels, starting from a data frame, so that you can copy it into your project or another
    notebook. The data are FiveThirtyEight's candy rankings from session 12, with one row per
    candy.

    Each code cell starts with a comment listing the imports it uses, and its variable names start
    with `_`, which keeps them local to the cell, so you can paste a cell anywhere in a marimo
    notebook without a clash with names in other cells.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import pandas as pd
    import statsmodels.formula.api as smf

    return mo, pd, smf


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
def load_candy(course_csv):
    candy = course_csv("candy-data.csv")
    candy.head()
    return (candy,)


@app.cell(hide_code=True)
def correlation_intro(mo):
    mo.md(r"""
    ---
    ## Correlations

    In the cell below, we compute the correlation between every pair of numeric columns, and then
    between one pair. `numeric_only=True` leaves out text columns such as the candy's name.
    """)
    return


@app.cell
def correlation_code(candy):
    _table = candy.corr(numeric_only=True).round(2)
    print(_table[["winpercent", "pricepercent"]])
    print()
    print("price and winning:", round(candy["pricepercent"].corr(candy["winpercent"]), 3))
    return


@app.cell(hide_code=True)
def ols_intro(mo):
    mo.md(r"""
    ---
    ## Fitting a regression

    In the cell below, we fit an ordinary least squares regression with a formula, then print the
    slope, its 95% confidence interval and R², followed by the full summary table. The formula
    `"winpercent ~ pricepercent"` reads "winpercent predicted from pricepercent". To use it on
    other data, you would put your own data frame and column names in the formula.
    """)
    return


@app.cell
def ols_code(candy, smf):
    # Uses: import statsmodels.formula.api as smf
    _model = smf.ols("winpercent ~ pricepercent", data=candy).fit()
    _low, _high = _model.conf_int().loc["pricepercent"]
    print(f"slope {_model.params['pricepercent']:.2f}, 95% CI [{_low:.2f}, {_high:.2f}], "
          f"R² {_model.rsquared:.3f}")
    print()
    print(_model.summary())
    return


@app.cell(hide_code=True)
def control_intro(mo):
    mo.md(r"""
    ---
    ## Adding a predictor

    A predictor is added with `+ name` on the right-hand side of the formula. In the cell below, we
    fit price alone and then price with chocolate held fixed, and put price's slope and confidence
    interval from both models side by side, which is how you would check whether a slope changes
    once another column is in the model.
    """)
    return


@app.cell
def control_code(candy, pd, smf):
    # Uses: import pandas as pd
    #       import statsmodels.formula.api as smf
    _rows = {}
    for _formula in ["winpercent ~ pricepercent", "winpercent ~ pricepercent + chocolate"]:
        _model = smf.ols(_formula, data=candy).fit()
        _low, _high = _model.conf_int().loc["pricepercent"]
        _rows[_formula] = {"price slope": _model.params["pricepercent"], "CI low": _low,
                           "CI high": _high, "R²": _model.rsquared}
    pd.DataFrame(_rows).T.round(3)
    return


if __name__ == "__main__":
    app.run()
