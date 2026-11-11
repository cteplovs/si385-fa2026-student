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

    ## Session 13, the code on its own: regression diagnostics

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L13_regression_diagnostics.py`. The session
    notebook uses a switch and plots written for it, which you will not have when you work on your
    own data. Each section below does one of the session's computations with only pandas and
    statsmodels, starting from a data frame, so that you can copy it into your project or another
    notebook. The data are the daily traffic on Yandex's network from session 13, which come from
    Cloudflare Radar.

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
def load_traffic(course_csv, pd):
    yandex = course_csv("yandex_bot_traffic.csv")
    yandex["date"] = pd.to_datetime(yandex["date"])
    # t counts the days from 0, so that a regression can fit a time trend.
    yandex["t"] = range(len(yandex))
    yandex.head()
    return (yandex,)


@app.cell(hide_code=True)
def categorical_intro(mo):
    mo.md(r"""
    ---
    ## A trend and a categorical predictor

    Wrapping a column in `C()` in a formula treats it as categories, so the model estimates a
    separate shift for each day of the week, measured from the first day in alphabetical order. In
    the cell below, we fit traffic on a time trend and the day of the week and print the
    coefficients with their 95% confidence intervals.
    """)
    return


@app.cell
def categorical_code(smf, yandex):
    # Uses: import statsmodels.formula.api as smf
    _model = smf.ols("bot_index ~ t + C(day_of_week)", data=yandex).fit()
    _model.params.to_frame("coefficient").join(
        _model.conf_int().rename(columns={0: "CI low", 1: "CI high"})).round(4)
    return


@app.cell(hide_code=True)
def prediction_intro(mo):
    mo.md(r"""
    ---
    ## Fitting to some rows and predicting others

    To predict what a period would have looked like from the days before it, we fit the model to
    the earlier rows only and predict the later ones. In the cell below, `get_prediction` gives
    both intervals: `mean_ci_lower` and `mean_ci_upper` are the confidence interval for the mean
    on that day, and `obs_ci_lower` and `obs_ci_upper` are the prediction interval for a single
    day, which is wider. To use it on other data, you would change the date that divides the two
    sets of rows.
    """)
    return


@app.cell
def prediction_code(smf, yandex):
    # Uses: import statsmodels.formula.api as smf
    _before = yandex[yandex["date"] < "2026-10-08"]
    _after = yandex[yandex["date"] >= "2026-10-08"]
    _model = smf.ols("bot_index ~ t + C(day_of_week)", data=_before).fit()
    _predicted = _model.get_prediction(_after).summary_frame(alpha=0.05)
    _predicted.insert(0, "actual", _after["bot_index"].to_numpy())
    _predicted.index = _after["date"].dt.date
    _predicted.round(3)
    return


@app.cell(hide_code=True)
def influence_intro(mo):
    mo.md(r"""
    ---
    ## Influence and leverage

    In the cell below, we compute Cook's distance, the standardized residuals and the hat-values
    for every row, list the rows with the largest Cook's distance, and print the reading's rules of
    thumb, 4/(n − P − 1) for high influence and 2(P + 1)/n for high leverage, where P counts the
    predictors.
    """)
    return


@app.cell
def influence_code(smf, yandex):
    # Uses: import statsmodels.formula.api as smf
    _model = smf.ols("bot_index ~ t + C(day_of_week)", data=yandex).fit()
    _influence = _model.get_influence()
    _n, _p = int(_model.nobs), int(_model.df_model)
    print(f"n = {_n}, P = {_p}, 4/(n-P-1) = {4 / (_n - _p - 1):.3f}, "
          f"2(P+1)/n = {2 * (_p + 1) / _n:.3f}")
    yandex[["date", "bot_index"]].assign(
        cooks_d=_influence.cooks_distance[0],
        std_resid=_influence.resid_studentized_internal,
        hat=_influence.hat_matrix_diag,
    ).sort_values("cooks_d", ascending=False).head(8).round(3)
    return


if __name__ == "__main__":
    app.run()
