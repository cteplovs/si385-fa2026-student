# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    import numpy as np
    import pandas as pd

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

    return course_csv, mo, np, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 10: Hypothesis testing II, ANOVA and the multiplicity problem

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, October 5, 2026

    **Reading due today:** Bruce et al., *AI-Assisted Statistics for Data Scientists*, ch. 3,
    §§ *Multiple Testing*, *Degrees of Freedom* and *ANOVA*

    ---

    ### Today you will be able to

    - Say what a single overall test asks, and what it cannot tell you about which group differs
    - Say why the group that comes out on top is likely to be overrated
    - Tell a real difference among groups from one that chance would produce
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 · RAT 7

    Canvas gave you your score and your own answers when you submitted, but not the key.
    We will re-poll the items that split the room.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:15 · Application exercise 8

    ## Which country grows the best cocoa?

    The file holds 2,530 chocolate bars rated by *Flavors of Cacao* between 2006 and 2021, one
    row per bar, on a scale from 1 (unpleasant) to 4 (outstanding).  Today we work with the 21
    countries of bean origin that have at least 30 bars.
    """)
    return


@app.cell
def _(course_csv, pd):
    bars = course_csv("chocolate.csv")
    bars["cocoa"] = bars["cocoa_percent"].str.rstrip("%").astype(float)
    band_names = ["≤65%", "66–69%", "70–72%", "73–79%", "80%+"]
    bars["band"] = pd.cut(bars["cocoa"], [0, 65, 69, 72, 79, 100],
                          labels=band_names).astype(str)
    bars.head()
    return band_names, bars


@app.cell
def _(bars):
    _counts = bars["country_of_bean_origin"].value_counts()
    origins = sorted(_counts[(_counts >= 30) & (_counts.index != "Blend")].index)
    by_origin = bars[bars["country_of_bean_origin"].isin(origins)]
    return by_origin, origins


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The draft and two lineups

    These are on the screen at the front rather than in this notebook.  First, before you see
    any of the data, please pick in Sli.do the origin you think tops the ratings.  Then, for
    each of two lineups, please vote for the panel you think shows the real data, before you
    talk to anyone.  None of it is graded, and nobody is expected to know.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The 21 origins

    The table shows each origin's number of bars and average rating, sorted from highest to
    lowest.
    """)
    return


@app.cell
def _(by_origin):
    origin_table = (by_origin.groupby("country_of_bean_origin")["rating"]
                    .agg(bars="count", average="mean")
                    .sort_values("average", ascending=False)
                    .round(2))
    origin_table
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 0:25 · Part 1: five minutes, on your own, in silence

    > **A chocolate shop near campus wants to stock the best bars it can.  The owner reads the
    > file and says: "Vietnam grows the best cocoa.  Its bars average 3.29, the highest of the
    > 21 origins, and its lead over the other 20 is 0.07, with a 90% interval of 0.009 to
    > 0.133.  The interval excludes zero."  What do you tell the owner?**

    Take a position and write down what you would want to see before you believed it.  Please do
    not talk to your team yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:30 · With your team

    Argue to a decision.

    > **What do you tell the owner?**
    >
    > **A.** Stock Vietnamese bars.  Vietnam has the highest average of the 21 origins, and its
    > lead is statistically clear.
    >
    > **B.** The file cannot name a best country.  Tested together, the 21 origins differ no
    > more than chance would make them, and the top origin's lead is what chance produces.
    >
    > **C.** Stock the top three, Vietnam, Papua New Guinea and Madagascar.  No single winner is
    > certain, but the leaders are the safest bet.
    >
    > **D.** Stock single-origin bars from any country and skip blends.  That is the one
    > difference the file supports.

    ### The justification

    No code is required today.  Please write three sentences:

    1. **Say which evidence your answer rests on.**  The lineups count as evidence.
    2. **Say what you would expect to see if the owner were right.**
    3. **Say which result would have changed your answer.**

    ### Submitting

    **Submit on Canvas first**, to *AE 8: Which country grows the best cocoa?*  One person
    submits for the team, ideally a different person from last time, and includes, in this
    order, the team name, your letter, your justification, and who is here today.

    **Then in Sli.do**, click your letter.  Sli.do draws the histogram and is not graded.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## If your team wants a test

    This is optional.  The function below is the reading's permutation ANOVA: it records the
    variance among the group averages, shuffles the group labels, and counts how often a shuffle
    produces at least as much variance as the real data.  To run it on the origins, for example,
    call `perm_anova(by_origin["country_of_bean_origin"], by_origin["rating"])`.
    """)
    return


@app.cell
def _(np):
    def perm_anova(groups, values, n_shuffles=5000, seed=385):
        """The reading's permutation ANOVA.  Returns (observed variance, p_value)."""
        rng = np.random.default_rng(seed)
        groups = np.asarray(groups)
        values = np.asarray(values, dtype=float)
        names = sorted(set(groups))

        def spread(labels):
            return np.var([values[labels == g].mean() for g in names], ddof=1)

        observed = spread(groups)
        shuffled = np.array([spread(rng.permutation(groups)) for _ in range(n_shuffles)])
        return observed, float((shuffled >= observed).mean())

    return (perm_anova,)


if __name__ == "__main__":
    app.run()
