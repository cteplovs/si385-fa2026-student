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

    return course_csv, mo, pd, plt, smf


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 13: Regression diagnostics

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, October 14, 2026

    **Reading due today:** Bruce et al., *AI-Assisted Statistics for Data Scientists*, ch. 4,
    § *Regression Diagnostics*

    ---

    ### Today you will be able to

    - Tell an outlier from an influential observation, and read Cook's distance and the hat-value
    - Say what a rule of thumb for influence can and cannot decide
    - Choose a baseline for a prediction and say why it represents normal
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 · RAT 10

    Canvas gave you your score and your own answers when you submitted, but not the key.
    We will re-poll the items that split the room.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:15 · Application exercise 11

    ## How much did the strikes take offline?

    The file holds twelve weeks of daily traffic from the network that Yandex uses for its own
    services, from Cloudflare Radar, July 20 to October 11, 2026 (UTC).  `bot_index` counts
    requests classified as automated, as a fraction of the busiest day in the file, and
    `human_index` counts the rest on the same scale.  Human traffic is about 1% of the total, so
    `bot_index` stands for the network's traffic.  The data are Cloudflare Radar's, published
    under CC BY-NC 4.0.

    Yandex shut down its data centre in Sasovo after a drone strike late on October 7 (UTC), and
    news reports describe further strikes on its data centres over the following days.
    """)
    return


@app.cell
def _(course_csv, pd):
    yandex = course_csv("yandex_bot_traffic.csv")
    yandex["date"] = pd.to_datetime(yandex["date"])
    yandex["t"] = range(len(yandex))
    yandex.tail(8)
    return (yandex,)


@app.cell(hide_code=True)
def _(mo):
    shade_strikes = mo.ui.switch(value=False, label="Shade October 8 to 11")
    mo.md(f"""
    ### The whole series

    Please look at all twelve weeks before fitting anything.

    {shade_strikes}
    """)
    return (shade_strikes,)


@app.cell
def _(pd, plt, shade_strikes, yandex):
    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(yandex["date"], yandex["bot_index"], marker="o", markersize=3,
             color="#1f4e79", linewidth=1)
    if shade_strikes.value:
        _ax.axvspan(pd.Timestamp("2026-10-07 12:00"), pd.Timestamp("2026-10-11 12:00"),
                    color="#c2410c", alpha=0.15)
    _ax.set_ylim(0, 1.05)
    _ax.set_ylabel("Traffic, fraction of the busiest day (bot_index)")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 0:15 · Part 1: eight minutes, on your own, in silence

    > **News reports said traffic from Yandex's network fell to less than one percent of its peak
    > after the strikes.  A journalist writing a follow-up wants a figure a reader can trust: over
    > October 8 to 11, what share of Yandex's normal traffic did the strikes take offline?**

    Take a position on what "normal" should mean, and write down which result would change your
    mind.  Please do not talk to your team yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:23 · With your team

    Argue to a decision.

    > **Over October 8 to 11, what share of Yandex's normal traffic did the strikes take
    > offline?**
    >
    > **A.** About 55%.  Normal is the busiest day in the file, and the four days averaged 45% of
    > it.
    >
    > **B.** About 37%.  Normal is the same weekday one week earlier, a comparison any reader can
    > check.
    >
    > **C.** About 46%.  Normal is what a regression on day of week and trend, fitted to July 20
    > to October 7, predicts for October 8 to 11.
    >
    > **D.** About 41%.  Normal is what the same regression predicts when it is fitted to all 84
    > days, so that no data are thrown away.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## A worked example, fitted to all 84 days

    The cell below fits traffic on a time trend `t` and the day of the week, using every row in
    the file, and predicts October 8 to 11 with 95% prediction intervals.  In the reading's terms,
    a prediction interval is the one for a single value, which is wider than a confidence interval
    for the mean.  The last line is the share of the predicted traffic that did not arrive.
    """)
    return


@app.cell
def _(smf, yandex):
    all_days = smf.ols("bot_index ~ t + C(day_of_week)", data=yandex).fit()
    _strike_days = yandex[yandex["date"] >= "2026-10-08"]
    _frame = all_days.get_prediction(_strike_days).summary_frame(alpha=0.05)
    _frame = _frame[["mean", "obs_ci_lower", "obs_ci_upper"]].round(3)
    _frame.insert(0, "actual", _strike_days["bot_index"].round(3).values)
    _frame.index = _strike_days["date"].dt.strftime("%b %d")
    print(_frame)
    print(f"share lost: {1 - _strike_days['bot_index'].sum() / _frame['mean'].sum():.1%}")
    return (all_days,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Influence in the worked example

    Cook's distance, standardized residuals and hat-values for the model above, for the eight days
    with the largest Cook's distance.  The reading's rule of thumb for high influence is
    4/(n − P − 1), and for high leverage it is 2(P + 1)/n, where P counts the predictors.
    """)
    return


@app.cell
def _(all_days, yandex):
    _influence = all_days.get_influence()
    _n, _p = int(all_days.nobs), int(all_days.df_model)
    _table = yandex[["date", "bot_index"]].assign(
        cooks_d=_influence.cooks_distance[0],
        std_resid=_influence.resid_studentized_internal,
        hat=_influence.hat_matrix_diag,
    )
    print(f"n = {_n}, P = {_p}, 4/(n-P-1) = {4 / (_n - _p - 1):.3f}, "
          f"2(P+1)/n = {2 * (_p + 1) / _n:.3f}")
    _table.sort_values("cooks_d", ascending=False).head(8).round(3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Your team's code

    Please write a function that takes the rows your baseline is built from and returns the share
    lost over October 8 to 11, with the four predicted baselines and their 95% prediction
    intervals.  If your answer is A or B, compute that baseline directly instead and report the
    share lost.  The function returns `None` until you write it.

    **Check it first.**  Run your function on all 84 rows before anything else.  Its prediction
    for October 11 should be 0.710 with a 95% prediction interval of [0.436, 0.984], and if it is
    not, it is not fitting the model the worked example fits.
    """)
    return


@app.cell
def _():
    def share_lost(fit_rows, all_rows):
        """Fit bot_index ~ t + C(day_of_week) to fit_rows, predict Oct 8-11 in all_rows.

        Return the share lost and the predictions with their 95% prediction intervals.
        """
        return None

    return (share_lost,)


@app.cell
def _(share_lost, yandex):
    share_lost(yandex, yandex)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Not required.**  If your team has time, list the days whose Cook's distance in the worked
    example exceeds 4/(n − P − 1), and say which of them you would remove and why.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Submitting

    **Submit on Canvas first**, to *AE 11: How much did the strikes take offline?*  One person
    submits for the team, ideally a different person from last time, and includes, in this order,
    the team name, your letter, your code and its output pasted as code (Format → Code in the
    Canvas editor), your justification, and who is here today.

    The code and the justification are graded together.  Please write three sentences:

    1. **Say which days define normal in your baseline, and why the strikes could not have
       affected them.**
    2. **Say how uncertain your figure is, using the prediction intervals or the spread of the
       comparison days.**
    3. **Say which result would have changed your answer.**

    **Then in Sli.do**, click your letter.  Sli.do draws the histogram and is not graded.
    """)
    return


if __name__ == "__main__":
    app.run()
