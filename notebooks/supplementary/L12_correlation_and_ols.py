# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "statsmodels>=0.14",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 12: Correlation and ordinary least squares regression

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, October 12, 2026

    **Reading due today:** Bruce et al., *AI-Assisted Statistics for Data Scientists*, ch. 1,
    § *Correlation*, and ch. 4, §§ *Simple Linear Regression* and *Multiple Linear Regression*

    ---

    ### Today you will be able to

    - Compute and read a correlation coefficient, and say what it does not measure
    - Fit a straight line by least squares, and read its slope, its intercept and R²
    - Read the confidence interval for a slope, and say what an interval that includes zero does and
      does not show
    - Say what changes in a coefficient when another predictor is held fixed

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Data | 5 |
    | Correlation | 10 |
    | Least squares | 10 |
    | The slope's confidence interval | 10 |
    | Holding another predictor fixed | 10 |
    | Today's question, in teams | 15 |
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import statsmodels.formula.api as smf

    REMOTE = ("https://raw.githubusercontent.com/"
              "cteplovs/si385-fa2026-student/main/data/")


    def course_csv(name):
        """Read one of the course data files.

        The copy in the course folder is the one to prefer, and it is what you get if you are
        running this the documented way. The fallback to the public repository is there so that
        the notebook also runs on molab, provided you have a network.
        """
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_csv(local)
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as response:
            return pd.read_csv(BytesIO(response.read()))

    return course_csv, mo, np, pd, plt, smf


@app.cell(hide_code=True)
def code_on_its_own_note(mo):
    mo.md(r"""
    ### Sections headed *The code on its own*

    Each technique ends with a section headed *The code on its own*. The dropdowns, sliders and
    plots above it call functions written for this notebook, which you will not have when you work
    on your own data. The code in those sections uses only pandas, NumPy and statsmodels, starts
    from a data frame, and does the computation without any controls, so that you can copy it into
    your project or another notebook. Each code cell starts with a comment listing the imports it
    uses, and its variable names start with `_`, which keeps them local to the cell.
    """)
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## Data

    The file holds FiveThirtyEight's *Ultimate Halloween Candy Power Ranking* (2017). Visitors to the
    site were shown two candies at a time and picked the one they would rather receive, about 269,000
    times in all. There is one row per candy, 85 in all. The data are FiveThirtyEight's, published
    under CC BY 4.0.

    | Column | Description |
    |---|---|
    | `competitorname` | The candy |
    | `chocolate`, `fruity`, `caramel`, `peanutyalmondy`, `nougat`, `crispedricewafer` | 1 if the candy has it, 0 if not |
    | `hard`, `bar`, `pluribus` | 1 if it is a hard candy, a bar, or one of many in a bag or box |
    | `sugarpercent` | The candy's sugar content as a percentile among the 85, from 0 to 1 |
    | `pricepercent` | Its price per unit as a percentile among the 85, from 0 to 1 |
    | `winpercent` | The percentage of its matchups that it won: the value to explain |
    """)
    return


@app.cell
def load_candy(course_csv):
    candy = course_csv("candy-data.csv")
    COLUMNS = [_c for _c in candy.columns if _c != "competitorname"]
    candy.sort_values("winpercent", ascending=False).head()
    return COLUMNS, candy


@app.cell(hide_code=True)
def correlation_intro(mo):
    mo.md(r"""
    ---
    ## Correlation

    The *correlation coefficient* r measures how closely two columns move together along a straight
    line. To compute it, put each column in standard units (subtract its mean and divide by its
    standard deviation), multiply the two standard-unit values for each candy, and average the
    products, dividing by *n* − 1:

    $$r = \frac{1}{n - 1} \sum z_x \, z_y$$

    A candy above average on both columns, or below average on both, contributes a positive
    product, and a candy above on one and below on the other contributes a negative one. In the
    scatterplot below, the first kind are drawn in blue and the second in orange, so r is positive
    when blue points dominate and negative when orange ones do. It runs from −1 to 1, and it has no
    units, so it does not change if a column is rescaled.

    Please choose two columns. A column of 0s and 1s, such as `chocolate`, also has a correlation:
    it measures how far the candies with the feature sit above or below the ones without.
    """)
    return


@app.cell
def correlation_controls(COLUMNS, mo):
    # mo.ui.dropdown is a marimo function that makes a drop-down menu; its .value is the choice.
    x_pick = mo.ui.dropdown(options=COLUMNS, value="pricepercent", label="Across")
    y_pick = mo.ui.dropdown(options=COLUMNS, value="winpercent", label="Up")
    # mo.hstack is a marimo function that puts outputs side by side.
    mo.hstack([x_pick, y_pick], justify="start", gap=2)
    return x_pick, y_pick


@app.cell
def correlation_plot(candy, mo, np, plt, x_pick, y_pick):
    _x, _y = candy[x_pick.value], candy[y_pick.value]
    _zx, _zy = (_x - _x.mean()) / _x.std(), (_y - _y.mean()) / _y.std()
    _r = (_zx * _zy).sum() / (len(candy) - 1)
    _jitter = np.random.default_rng(385).normal(0, 0.015, len(candy))
    _spread_x = _x + _jitter * (_x.max() - _x.min()) * (_x.nunique() <= 2)

    _fig, _ax = plt.subplots(figsize=(7, 4.5))
    _ax.scatter(_spread_x, _y, c=np.where(_zx * _zy >= 0, "#1f4e79", "#c2410c"), alpha=0.8)
    _ax.axvline(_x.mean(), color="#9ca3af", linewidth=1)
    _ax.axhline(_y.mean(), color="#9ca3af", linewidth=1)
    _ax.set_xlabel(x_pick.value)
    _ax.set_ylabel(y_pick.value)
    _ax.set_title(f"r = {_r:.2f}; the grey lines are the two means")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def correlation_table_intro(mo):
    mo.md(r"""
    The table gives every column's correlation with `winpercent`, from the most negative to the most
    positive. Correlation measures only straight-line association, and a few unusual points can move
    it a long way, as Anscombe's quartet showed in session 4, so it is worth looking at the
    scatterplot for any correlation you intend to rely on.
    """)
    return


@app.cell
def correlation_table(candy):
    candy.drop(columns="competitorname").corr()["winpercent"].drop("winpercent").sort_values().round(2)
    return


@app.cell(hide_code=True)
def practice_r_intro(mo):
    mo.md(r"""
    ### Practice: r by hand

    Please type this one yourself. Replace `None` in the cell below with the correlation between
    `sugarpercent` and `winpercent`, computed from the formula above: put both columns in standard
    units, multiply, sum, and divide by 84. Then check it against
    `candy["sugarpercent"].corr(candy["winpercent"])`.
    """)
    return


@app.cell
def practice_r():
    my_r = None
    my_r
    return


@app.cell(hide_code=True)
def correlation_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the correlation between one pair of columns, and then the
    correlation of every numeric column with one of them, sorted. `numeric_only=True` leaves out
    text columns such as the candy's name.
    """)
    return


@app.cell
def correlation_code(candy):
    print("price and winning:", round(candy["pricepercent"].corr(candy["winpercent"]), 3))
    print()
    print(candy.corr(numeric_only=True)["winpercent"].drop("winpercent").sort_values().round(2))
    return


@app.cell(hide_code=True)
def least_squares_intro(mo):
    mo.md(r"""
    ---
    ## Least squares

    A correlation measures how closely two columns follow a line, and a regression finds the line. Simple
    linear regression predicts one column from another with

    $$\hat{y} = b_0 + b_1 x$$

    where $b_0$ is the *intercept* (the prediction when x is 0) and $b_1$ is the *slope* (how much the
    prediction rises when x rises by one unit). Each candy's *residual* is the gap between its actual
    `winpercent` and the line's prediction. *Ordinary least squares* finds the line that makes the
    sum of the squared residuals as small as possible.

    Please use the two sliders to find a line through the candies, and try to make the sum of squared
    residuals, shown in the title, as small as you can. Then switch on the least squares line to see
    how close you came.
    """)
    return


@app.cell
def line_controls(mo):
    # mo.ui.slider is a marimo function that makes a slider; its .value is the chosen setting.
    intercept_slider = mo.ui.slider(start=20, stop=70, step=0.5, value=50, label="Intercept, b₀",
                                    show_value=True)
    slope_slider = mo.ui.slider(start=-20, stop=50, step=0.5, value=0, label="Slope, b₁",
                                show_value=True)
    # mo.ui.switch is a marimo function that makes an on-off switch.
    show_fit = mo.ui.switch(value=False, label="Show the least squares line")
    mo.hstack([intercept_slider, slope_slider, show_fit], justify="start", gap=2)
    return intercept_slider, show_fit, slope_slider


@app.cell
def line_plot(candy, intercept_slider, np, plt, show_fit, slope_slider):
    _x, _y = candy["pricepercent"], candy["winpercent"]
    _guess = intercept_slider.value + slope_slider.value * _x
    _guess_ss = ((_y - _guess) ** 2).sum()
    _b1 = np.cov(_x, _y)[0, 1] / _x.var()
    _b0 = _y.mean() - _b1 * _x.mean()
    _best_ss = ((_y - _b0 - _b1 * _x) ** 2).sum()

    _fig, _ax = plt.subplots(figsize=(7, 4.5))
    _ax.vlines(_x, _guess, _y, color="#c2410c", alpha=0.4, linewidth=1)
    _ax.scatter(_x, _y, color="#1f4e79", zorder=3)
    _ax.plot([0, 1], [intercept_slider.value, intercept_slider.value + slope_slider.value],
             color="#c2410c", label="your line")
    _title = f"Your line: sum of squared residuals {_guess_ss:,.0f}"
    if show_fit.value:
        _ax.plot([0, 1], [_b0, _b0 + _b1], color="#111827", linestyle="--",
                 label=f"least squares: b₀ = {_b0:.1f}, b₁ = {_b1:.1f}")
        _title += f"; least squares: {_best_ss:,.0f}"
    _ax.set_xlabel("pricepercent")
    _ax.set_ylabel("winpercent")
    _ax.set_title(_title)
    _ax.legend(frameon=False, loc="upper left")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def statsmodels_intro(mo):
    mo.md(r"""
    In practice you let software find the line. Below, we fit it with statsmodels, which the
    reading uses. The formula `"winpercent ~ pricepercent"` reads "winpercent predicted from
    pricepercent", and `.fit()` computes the least squares coefficients. The summary is long; the
    rows to read for now are the coefficients (`coef`), their 95% intervals (`[0.025` and `0.975]`)
    and `R-squared`.
    """)
    return


@app.cell
def fit_price(candy, smf):
    price_model = smf.ols("winpercent ~ pricepercent", data=candy).fit()
    price_model.summary().tables[1]
    return (price_model,)


@app.cell(hide_code=True)
def price_reading(candy, mo, price_model):
    _b0, _b1 = price_model.params
    _r = candy["pricepercent"].corr(candy["winpercent"])
    mo.md(f"""
    The slope is **{_b1:.1f}**. `pricepercent` runs from 0 (the cheapest candy) to 1 (the most
    expensive), so a candy 0.1 higher in the price ranking is predicted to win **{_b1 / 10:.1f}**
    percentage points more of its matchups. The intercept, **{_b0:.1f}**, is the prediction for a
    candy at the very bottom of the price ranking.

    R² is **{price_model.rsquared:.3f}**: the line accounts for about {price_model.rsquared:.0%} of
    the variation in `winpercent` between candies, and the rest is in the residuals. With a single
    predictor, R² is the square of the correlation: {_r:.3f}² = {_r ** 2:.3f}.
    """)
    return


@app.cell(hide_code=True)
def fit_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we fit a least squares line with a formula, print its intercept, slope and
    R², and predict the outcome for new values of the predictor, which have to be given in a data
    frame with the same column name. To use it on other data, you would change the formula and the
    new values.
    """)
    return


@app.cell
def fit_code(candy, pd, smf):
    # Uses: import pandas as pd
    #       import statsmodels.formula.api as smf
    _model = smf.ols("winpercent ~ pricepercent", data=candy).fit()
    print(_model.params.round(2))
    print("R²:", round(_model.rsquared, 3))
    print()
    _new = pd.DataFrame({"pricepercent": [0.1, 0.5, 0.9]})
    _new.assign(predicted=_model.predict(_new).round(1))
    return


@app.cell(hide_code=True)
def interval_intro(mo):
    mo.md(r"""
    ---
    ## The slope's confidence interval

    The 85 candies are one set of candies, and a different set would give a different slope. The
    *confidence interval* for the slope is the range of slopes consistent with these data. The
    summary computes it from a formula, and session 8's bootstrap gives a way to check it that needs
    no formula: resample the 85 candies with replacement, refit the line, repeat many times, and take
    the middle 95% of the slopes.

    Please move the slider to change the number of resamples and compare the bootstrap interval with
    the formula's.
    """)
    return


@app.cell
def define_bootstrap(np, smf):
    def bootstrap(formula, data, term, resamples=2000, seed=385):
        """Bootstrap one coefficient: refit the formula on resampled rows many times."""
        _design = smf.ols(formula, data=data)
        _x, _y = _design.exog, _design.endog
        _column = _design.exog_names.index(term)
        _rng = np.random.default_rng(seed)
        _slopes = []
        for _ in range(resamples):
            _rows = _rng.integers(0, len(_y), len(_y))
            _coef, *_ = np.linalg.lstsq(_x[_rows], _y[_rows], rcond=None)
            _slopes.append(_coef[_column])
        return np.array(_slopes)

    return (bootstrap,)


@app.cell
def resample_control(mo):
    resample_count = mo.ui.slider(steps=[100, 500, 1000, 2000, 5000], value=1000,
                                  label="Resamples", show_value=True)
    resample_count
    return (resample_count,)


@app.cell
def bootstrap_plot(bootstrap, candy, mo, np, plt, price_model, resample_count):
    _slopes = bootstrap("winpercent ~ pricepercent", candy, "pricepercent",
                        resamples=resample_count.value)
    _low, _high = np.percentile(_slopes, [2.5, 97.5])
    _f_low, _f_high = price_model.conf_int().loc["pricepercent"]

    _fig, _ax = plt.subplots(figsize=(7, 3))
    _ax.hist(_slopes, bins=40, color="#9ca3af")
    _ax.axvspan(_low, _high, color="#1f4e79", alpha=0.15, label="bootstrap 95%")
    _ax.axvline(_f_low, color="#c2410c", linestyle="--", label="formula 95%")
    _ax.axvline(_f_high, color="#c2410c", linestyle="--")
    _ax.axvline(0, color="#111827", linewidth=1)
    _ax.set_xlabel("Slope of winpercent on pricepercent")
    _ax.set_yticks([])
    _ax.legend(frameon=False)
    _ax.spines[["top", "right", "left"]].set_visible(False)
    _fig.tight_layout()
    # mo.vstack is a marimo function that stacks outputs one above the other.
    mo.vstack([_fig, mo.md(f"""
    The bootstrap interval is **[{_low:.1f}, {_high:.1f}]** and the formula's is
    **[{_f_low:.1f}, {_f_high:.1f}]**. Neither includes zero, so these data are not consistent with a
    flat line: pricier candies, on the whole, win more.
    """)])
    return


@app.cell(hide_code=True)
def interval_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we take the slope's 95% interval from the formula with `conf_int`, and then
    compute a bootstrap interval by refitting the model on 1,000 resamples of the rows, drawn with
    replacement, and taking the 2.5th and 97.5th percentiles of the slopes.
    """)
    return


@app.cell
def interval_code(candy, np, smf):
    # Uses: import numpy as np
    #       import statsmodels.formula.api as smf
    _formula, _term = "winpercent ~ pricepercent", "pricepercent"
    _low, _high = smf.ols(_formula, data=candy).fit().conf_int().loc[_term]
    print(f"formula 95% interval: [{_low:.1f}, {_high:.1f}]")

    _rng = np.random.default_rng(385)
    _slopes = [smf.ols(_formula, data=candy.sample(n=len(candy), replace=True,
                                                   random_state=_rng)).fit().params[_term]
               for _ in range(1000)]
    _low, _high = np.percentile(_slopes, [2.5, 97.5])
    print(f"bootstrap 95% interval: [{_low:.1f}, {_high:.1f}]")
    return


@app.cell(hide_code=True)
def multiple_intro(mo):
    mo.md(r"""
    ---
    ## Holding another predictor fixed

    *Multiple linear regression* predicts from several columns at once:

    $$\hat{y} = b_0 + b_1 x_1 + b_2 x_2 + \dots$$

    Each coefficient is now the change in the prediction when its column rises by one unit *with the
    other columns held fixed*. That can be very different from the slope of the same column on its
    own, because the columns themselves are related. Chocolate candies tend to be pricier (the
    correlation between `chocolate` and `pricepercent` is 0.50), and chocolate candies win more
    matchups. Some of the price slope above may therefore belong to chocolate.

    Please add predictors alongside `pricepercent` and watch what happens to its coefficient and its
    interval. To add a predictor to a formula, add `+ name` to the right-hand side, as in
    `"winpercent ~ pricepercent + chocolate"`.
    """)
    return


@app.cell
def multiple_controls(COLUMNS, mo):
    # mo.ui.multiselect is a marimo function that makes a list from which several items can be chosen.
    extra_pick = mo.ui.multiselect(
        options=[_c for _c in COLUMNS if _c not in ("winpercent", "pricepercent")],
        value=["chocolate"], label="Add to pricepercent")
    extra_pick
    return (extra_pick,)


@app.cell
def define_coefficients(pd, smf):
    def coefficients(formula, data):
        """The coefficients of a fitted formula with their 95% intervals, and its R²."""
        _fitted = smf.ols(formula, data=data).fit()
        _intervals = _fitted.conf_int()
        _table = pd.DataFrame({"coefficient": _fitted.params, "low": _intervals[0],
                               "high": _intervals[1]}).round(2)
        return _table, _fitted.rsquared

    return (coefficients,)


@app.cell
def multiple_view(candy, coefficients, extra_pick, mo):
    multiple_formula = " + ".join(["winpercent ~ pricepercent", *extra_pick.value])
    _table, _r2 = coefficients(multiple_formula, candy)
    _alone, _ = coefficients("winpercent ~ pricepercent", candy)
    mo.vstack([
        mo.md(f"`{multiple_formula}`, R² = **{_r2:.3f}**"),
        mo.hstack([
            # mo.stat is a marimo function that displays a single number with a label.
            mo.stat(value=f"{_alone.loc['pricepercent', 'coefficient']:.1f}",
                    label="price, on its own",
                    caption=f"[{_alone.loc['pricepercent', 'low']:.1f}, "
                            f"{_alone.loc['pricepercent', 'high']:.1f}]"),
            mo.stat(value=f"{_table.loc['pricepercent', 'coefficient']:.1f}",
                    label="price, with the others fixed",
                    caption=f"[{_table.loc['pricepercent', 'low']:.1f}, "
                            f"{_table.loc['pricepercent', 'high']:.1f}]"),
        ], justify="start", gap=2),
        _table,
    ])
    return


@app.cell(hide_code=True)
def two_lines_intro(mo):
    mo.md(r"""
    The figure shows the model with price and chocolate. Holding chocolate fixed means comparing
    chocolate candies with chocolate candies and the others with the others, so the model draws two
    parallel lines, one for each group, whose common slope is the price coefficient. The gap between
    the lines is the chocolate coefficient.
    """)
    return


@app.cell
def two_lines_plot(candy, plt, smf):
    _fitted = smf.ols("winpercent ~ pricepercent + chocolate", data=candy).fit()
    _b0, _price, _choc = _fitted.params
    _fig, _ax = plt.subplots(figsize=(7, 4.5))
    for _value, _colour, _label in [(0, "#9ca3af", "no chocolate"), (1, "#c2410c", "chocolate")]:
        _rows = candy[candy["chocolate"] == _value]
        _ax.scatter(_rows["pricepercent"], _rows["winpercent"], color=_colour, label=_label)
        _ax.plot([0, 1], [_b0 + _choc * _value, _b0 + _choc * _value + _price], color=_colour)
    _ax.set_xlabel("pricepercent")
    _ax.set_ylabel("winpercent")
    _ax.set_title(f"Slope {_price:.1f} in both groups; gap {_choc:.1f} points")
    _ax.legend(frameon=False)
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def includes_zero(mo):
    mo.md(r"""
    With chocolate held fixed, the price coefficient falls to about 1.7, with an interval of about
    −8.4 to 11.8. An interval that includes zero means that these data cannot tell a small negative
    price effect from a small positive one. It does not show that price makes no difference: the same
    interval is consistent with a candy at the top of the price ranking winning 11 points more than
    one at the bottom, which would be a sizeable effect. "No evidence of an effect" and "evidence of
    no effect" are different claims, and an interval this wide supports only the first.
    """)
    return


@app.cell(hide_code=True)
def practice_formula_intro(mo):
    mo.md(r"""
    ### Practice: your own formula

    Please write a formula yourself in the cell below, with `winpercent` on the left and two or three
    columns of your choice on the right, then rerun it as you add or remove columns, and watch how
    the coefficients and R² change. Each member of your team should start from different columns.
    """)
    return


@app.cell
def practice_formula():
    # Replace the placeholder names with column names from the table at the top of the notebook.
    my_formula = "winpercent ~ SOME_COLUMN + SOME_OTHER_COLUMN"
    return (my_formula,)


@app.cell
def practice_fit(candy, coefficients, mo, my_formula):
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder values.
    mo.stop("SOME_" in my_formula,
            # mo.md is a marimo function that displays Markdown text.
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md("Replace the placeholder names in the cell above with column names.")
            .callout(kind="info"))
    _table, _r2 = coefficients(my_formula, candy)
    mo.vstack([mo.md(f"R² = **{_r2:.3f}**"), _table])
    return


@app.cell(hide_code=True)
def multiple_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we fit the outcome on one predictor alone and then with another column held
    fixed, and put the first predictor's coefficient, its 95% interval and each model's R² side by
    side, which shows how much the coefficient changes once the other column is in the model.
    """)
    return


@app.cell
def multiple_code(candy, pd, smf):
    # Uses: import pandas as pd
    #       import statsmodels.formula.api as smf
    _rows = {}
    for _formula in ["winpercent ~ pricepercent", "winpercent ~ pricepercent + chocolate"]:
        _model = smf.ols(_formula, data=candy).fit()
        _low, _high = _model.conf_int().loc["pricepercent"]
        _rows[_formula] = {"price coefficient": _model.params["pricepercent"], "low": _low,
                           "high": _high, "R²": _model.rsquared}
    pd.DataFrame(_rows).T.round(3)
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    Your hall council is buying candy for a Halloween party and wants the candy people like best. It
    has asked you what to look for.

    > **Use correlation and regression to say what makes a candy win its matchups, and how sure you
    > can be of each part of your answer.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. The correlations in the *Correlation* section, to say which features go with winning on their
       own, and how strongly.
    2. The coefficients of a multiple regression you fitted yourself, with their intervals and R², to
       say how much each feature adds with the others held fixed, and which of those you can be sure
       of.
    3. One limitation of your explanation: something the regression cannot tell the council, or a
       coefficient that is difficult to interpret.

    Then compare your results with your teammates', who started from different columns, and say what
    their results showed that yours did not, and whether that changes your explanation.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each
    prompt, in your own words and with the numbers from your own runs. Each of you should then
    upload your own copy of this notebook to *AE 10* on Canvas, by 23:59 on Tuesday.

    | Part of your answer | Points |
    |---|---:|
    | Your explanation: the correlations, the coefficients with their intervals and R², and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop rather than watching one
    screen, and start from different columns from your teammates, then compare what you find. Your
    team may agree on an explanation, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholder formula in Step 1,
    run the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_formula():
    # Step 1: write a formula with winpercent on the left and the columns you want on the right,
    # different from your teammates' at first. Replace the placeholder names.
    answer_formula = "winpercent ~ SOME_COLUMN + SOME_OTHER_COLUMN"
    return (answer_formula,)


@app.cell
def step2_fit(answer_formula, candy, coefficients, mo):
    # Step 2: fit the formula and list the coefficients with their 95% intervals, and R².
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder values.
    mo.stop("SOME_" in answer_formula,
            mo.md("Replace the placeholder names in Step 1 with column names.").callout(kind="info"))
    _table, _r2 = coefficients(answer_formula, candy)
    mo.vstack([mo.md(f"R² = **{_r2:.3f}**"), _table])
    return


@app.cell
def step3_bootstrap(answer_formula, bootstrap, candy, mo, np):
    # Step 3: bootstrap the coefficient you are least sure of, and compare its interval with the
    # formula's in Step 2. Replace the placeholder with one of the columns in your formula.
    answer_term = "SOME_COLUMN"
    mo.stop("SOME_" in answer_formula + answer_term)
    _slopes = bootstrap(answer_formula, candy, answer_term)
    {"term": answer_term, "bootstrap 95% interval": np.percentile(_slopes, [2.5, 97.5]).round(2)}
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L12_correlation_and_ols.py` to *AE 10* on Canvas by 23:59 on Tuesday. We will cross-reference
    your claims about evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_correlations(mo):
    mo.md(r"""
    **The features that go with winning on their own, and how strongly**
    """)
    return


@app.cell
def step4_answer_correlations(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_coefficients(mo):
    mo.md(r"""
    **What each feature adds with the others held fixed, and which of those you can be sure of**
    """)
    return


@app.cell
def step4_answer_coefficients(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_limitation(mo):
    mo.md(r"""
    **One limitation of your explanation**
    """)
    return


@app.cell
def step4_answer_limitation(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_teammates(mo):
    mo.md(r"""
    **Your teammates' results, and what they add to yours**
    """)
    return


@app.cell
def step4_answer_teammates(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


if __name__ == "__main__":
    app.run()
