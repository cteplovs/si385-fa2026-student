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

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 12: Correlation and ordinary least squares regression

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, October 12, 2026

    **Reading due today:** Bruce et al., *AI-Assisted Statistics for Data Scientists*, ch. 1,
    § *Correlation*, and ch. 4, §§ *Simple Linear Regression* and *Multiple Linear Regression*

    ---

    ### Today you will be able to

    - Fit a regression and read its slope, the slope's confidence interval, and R²
    - Say what changes when a second predictor is held fixed
    - Say what a confidence interval that includes zero does and does not show
    """)
    return


@app.cell
def _():
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
        """Read one of the course CSV files.

        The copy in the course folder is the one to prefer, and it is what you get
        if you are running this the documented way.  The fallback to the public
        repository is there so that the notebook also runs on molab, where there is
        no course folder for it to sit next to, provided you have a network.
        """
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_csv(local)
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as _response:
            return pd.read_csv(BytesIO(_response.read()))

    return course_csv, mo, np, plt, smf


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 · RAT 9

    Canvas gave you your score and your own answers when you submitted, but not the key.
    We will re-poll the items that split the room.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:15 · Application exercise 10

    ## Does pricier candy win?

    The file holds FiveThirtyEight's *Ultimate Halloween Candy Power Ranking* (2017), in which
    visitors to the site were shown two candies at a time and picked the one they would rather
    receive.  There is one row per candy.  `winpercent` is the share of its matchups that a candy
    won, and `pricepercent` and `sugarpercent` are percentiles within the 85, from 0 to 1.  The
    data are FiveThirtyEight's, published under CC BY 4.0.
    """)
    return


@app.cell
def _(course_csv):
    candy = course_csv("candy-data.csv")
    candy.head()
    return (candy,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### How the columns move together

    Each entry is the correlation between two columns, across the 85 candies.
    """)
    return


@app.cell
def _(candy):
    candy.drop(columns="competitorname").corr().round(2)
    return


@app.cell(hide_code=True)
def _(mo):
    features = ["chocolate", "fruity", "caramel", "peanutyalmondy", "nougat",
                "crispedricewafer", "hard", "bar", "pluribus"]
    colour_picker = mo.ui.dropdown(options=features, value="chocolate",
                                   label="Colour the points by")
    mo.md(f"""
    ### Winning against price

    Please pick a feature.  Candies that have it are drawn in one colour and the rest in
    another.

    {colour_picker}
    """)
    return (colour_picker,)


@app.cell
def _(candy, colour_picker, plt):
    _feature = colour_picker.value
    _fig, _ax = plt.subplots(figsize=(7, 4.5))
    for _value, _colour, _label in [(0, "#9aa5b1", f"no {_feature}"),
                                    (1, "#c2410c", _feature)]:
        _rows = candy[candy[_feature] == _value]
        _ax.scatter(_rows["pricepercent"], _rows["winpercent"],
                    color=_colour, label=_label, alpha=0.8)
    _ax.set_xlabel("Price percentile (pricepercent)")
    _ax.set_ylabel("Matchups won, % (winpercent)")
    _ax.legend(frameon=False)
    _ax.spines[["top", "right"]].set_visible(False)
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 0:15 · Part 1: eight minutes, on your own, in silence

    > **Your hall council is buying candy for a Halloween party and wants the candy that people
    > like best.  A council member who has taken a statistics class runs this file and asks you
    > one thing: should the council pay more for pricier candy?  What do you tell them?**

    Take a position and write down which result would change your mind.  Please do not talk to
    your team yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:23 · With your team

    Argue to a decision.

    > **Should the council pay more for pricier candy?**
    >
    > **A.** Pay more.  Pricier candy wins: across the price range the slope is 17.8 points, and
    > its 95% CI, [7.2, 28.3], excludes zero.
    >
    > **B.** Buy chocolate; price is unproven either way.  With chocolate held fixed, price's CI
    > is [-8.4, 11.8]: no evidence that price matters, and too wide to rule out a sizeable effect.
    >
    > **C.** Buy the cheapest chocolate.  With chocolate held fixed, price's CI is [-8.4, 11.8].
    > It includes zero, which shows that price makes no difference to how much people like a
    > candy.
    >
    > **D.** Pay more.  Price belongs in a strong model: price and chocolate together reach
    > R² = 0.41, against 0.12 for price alone.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## The reading's regression, worked on price alone

    The cell below fits winning on price, as in the reading's *Simple Linear Regression*, and
    prints the three numbers the options quote: the slope, its 95% confidence interval, and R².
    The formula `"winpercent ~ pricepercent"` reads "winpercent predicted from pricepercent", and
    adding a predictor means adding `+ name` to the right-hand side.
    """)
    return


@app.cell
def _(candy, smf):
    price_only = smf.ols("winpercent ~ pricepercent", data=candy).fit()
    _low, _high = price_only.conf_int().loc["pricepercent"]
    print(f"slope {price_only.params['pricepercent']:.2f}, "
          f"95% CI [{_low:.2f}, {_high:.2f}], R² {price_only.rsquared:.3f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Your team's code

    Please adapt the worked example into a function that takes a formula and a dataframe, fits
    the model, and returns price's slope with the two ends of its 95% CI.  Then run it on the
    model your answer rests on.  The function returns `None` until you write it.

    **Check it first.**  Run your function on `"winpercent ~ pricepercent"` and all 85 candies
    before anything else.  It should give a slope of 17.78 and a CI of [7.23, 28.33], and if it
    does not, it is not fitting the model the worked example fits.
    """)
    return


@app.cell
def _():
    def price_interval(formula, data):
        """Price's slope and 95% CI, as (slope, low, high), for one model."""
        return None

    return (price_interval,)


@app.cell
def _(candy, price_interval):
    price_interval("winpercent ~ pricepercent", candy)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Not required.**  If your team has time, bootstrap price's slope in the model your answer
    rests on.  Resample the 85 candies with replacement, refit, repeat 10,000 times, and take the
    2.5th and 97.5th percentiles of the slopes, which is the procedure from RAT 5 applied to a
    slope.  Then compare the result with the formula's interval.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Submitting

    **Submit on Canvas first**, to *AE 10: Does pricier candy win?*  One person submits for the
    team, ideally a different person from last time, and includes, in this order, the team name,
    your letter, your code and its CI pasted as code (Format → Code in the Canvas editor), your
    justification, and who is here today.

    The code and the justification are graded together.  Please write three sentences:

    1. **Say which model your answer rests on, and why it holds chocolate fixed or does not.**
    2. **Say what the price slope's CI allows: the smallest and the largest price effect it is
       consistent with.**
    3. **Say which result would have changed your answer.**

    **Then in Sli.do**, click your letter.  Sli.do draws the histogram and is not graded.
    """)
    return


if __name__ == "__main__":
    app.run()
