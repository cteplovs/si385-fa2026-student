# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
# ]
# ///

import marimo

__generated_with = "0.24.2"
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

    ## Session 11: Categorical data, contingency tables and the chi-square test

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, October 7, 2026

    **Reading due today:** Bruce et al., *AI-Assisted Statistics for Data Scientists*, ch. 3,
    § *Chi-Square Test*

    ---

    ### Today you will be able to

    - Read a contingency table, and say what the chi-square statistic measures in it
    - Run the chi-square test by resampling, with groups of unequal size
    - Say how much a result found by scanning many comparisons can be trusted
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 · RAT 8

    Canvas gave you your score and your own answers when you submitted, but not the key.
    We will re-poll the items that split the room.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:15 · Application exercise 9

    ## Which squirrel fact goes on the tour?

    The file holds the 2018 Central Park Squirrel Census, in which volunteers recorded every
    squirrel they saw between 6 and 20 October 2018, one row per sighting.  We keep the sightings
    with a recorded fur colour, and the cell below shows how many there are of each.
    """)
    return


@app.cell
def _(course_csv):
    behaviours = ["running", "chasing", "climbing", "eating", "foraging",
                  "kuks", "quaas", "moans", "tail_flags", "tail_twitches",
                  "approaches", "indifferent", "runs_from"]
    squirrels = (course_csv("nyc_squirrels.csv")
                 .dropna(subset=["primary_fur_color"])
                 .reset_index(drop=True))
    squirrels["primary_fur_color"].value_counts()
    return behaviours, squirrels


@app.cell(hide_code=True)
def _(behaviours, mo):
    behaviour_picker = mo.ui.dropdown(options=behaviours, value="running",
                                      label="Behaviour")
    mo.md(f"""
    ### Colour against one behaviour

    Please pick a behaviour.  The table counts the sightings of each colour in which the
    volunteer recorded it, and gives each colour's rate.

    {behaviour_picker}
    """)
    return (behaviour_picker,)


@app.cell
def _(behaviour_picker, squirrels):
    _column = behaviour_picker.value
    (squirrels.groupby("primary_fur_color")[_column]
     .agg(yes="sum", sightings="count", rate="mean")
     .round(3))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 0:15 · Part 1: eight minutes, on your own, in silence

    > **A Central Park tour company wants one fact about squirrel colours for its script.  A
    > blogger who scanned the census offers two: "Cinnamon squirrels approach people twice as
    > often as gray squirrels: 11.2% against 5.1%, chi-square p = 0.00001."  And: "Black
    > squirrels sound the quaa alarm three and a half times as often as gray squirrels: 4.9%
    > against 1.4%, chi-square p = 0.018."  Which fact belongs in the script?**

    Take a position and write down what you would want to see before you believed it.  Please do
    not talk to your team yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:23 · With your team

    Argue to a decision.

    > **Which fact belongs in the script?**
    >
    > **A.** Both.  Each p-value is below 0.05.
    >
    > **B.** The black-squirrel fact.  A ratio of three and a half is more striking than two,
    > and the test is significant.
    >
    > **C.** The cinnamon fact only.  It is strong enough to stand after the blogger's search,
    > and the black-squirrel fact is not.
    >
    > **D.** Neither.  The blogger scanned 13 behaviours, so any fact from the scan is suspect
    > until a new census confirms it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## The reading's test, worked on running

    The reading's resampling test puts every sighting's yes or no in one box, deals the box
    into three groups the size of the colour groups, and computes the chi-square statistic for
    the dealt table.  Repeating the deal many times shows how large the statistic gets when
    colour makes no difference, and the p-value is the share of deals at least as large as the
    real one.

    The cell below runs it on running, where the rates are close: about 24%, 26% and 25%.
    The one change from the reading is that the groups here are unequal (2,473 gray, 392
    cinnamon and 103 black), so the expected count for each cell comes from the group's size.
    """)
    return


@app.cell
def _(np, pd, squirrels):
    def chi_square_statistic(colours, yes):
        """Pearson's chi-square statistic for a colour-by-yes/no table."""
        _observed = pd.crosstab(colours, yes).to_numpy()
        _expected = (np.outer(_observed.sum(axis=1), _observed.sum(axis=0))
                     / _observed.sum())
        return float(((_observed - _expected) ** 2 / _expected).sum())

    _rng = np.random.default_rng(385)
    _colours = squirrels["primary_fur_color"].to_numpy()
    _box = squirrels["running"].to_numpy()

    running_observed = chi_square_statistic(_colours, _box)
    _dealt = np.array([chi_square_statistic(_colours, _rng.permutation(_box))
                       for _ in range(2000)])
    running_p = float((_dealt >= running_observed).mean())
    running_observed, running_p
    return (chi_square_statistic,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Your team's code

    Please adapt the worked example into a function that takes the name of a behaviour column
    and returns its resampling p-value, then run it on the fact your answer rests on.  The
    function returns `None` until you write it.

    **Check it first.**  Run your function on `"running"` before anything else.  It should give
    a p-value near 0.66, and if it does not, the function is not dealing the box the way the
    worked example does.
    """)
    return


@app.cell
def _():
    def resampled_p(column, n_deals=2000, seed=385):
        """Resampling chi-square p-value for fur colour against one behaviour."""
        return None

    return (resampled_p,)


@app.cell
def _(resampled_p):
    resampled_p("running")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Not required.**  If your team has time, run the function on all 13 behaviours, list the
    p-values, and mark the cutoff you would use for a scan of 13.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Submitting

    **Submit on Canvas first**, to *AE 9: Which squirrel fact goes on the tour?*  One person
    submits for the team, ideally a different person from last time, and includes, in this
    order, the team name, your letter, your code and its p-value pasted as code (Format → Code
    in the Canvas editor), your justification, and who is here today.

    The code and the justification are graded together.  Please write three sentences:

    1. **Say which evidence your answer rests on.**
    2. **Say what your code deals out, and what it would show if the blogger's fact were true.**
    3. **Say which result would have changed your answer.**

    **Then in Sli.do**, click your letter.  Sli.do draws the histogram and is not graded.
    """)
    return


if __name__ == "__main__":
    app.run()
