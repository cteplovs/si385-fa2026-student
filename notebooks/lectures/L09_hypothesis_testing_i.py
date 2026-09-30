# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
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

    def course_parquet(name):
        """Read one of the course Parquet files.

        The copy in the course folder is the one to prefer, and it is what you get
        if you are running this the documented way.  The fallback to the public
        repository is there so that the notebook also runs on molab, where there is
        no course folder for it to sit next to, provided you have a network.
        """
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_parquet(local)
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as _response:
            return pd.read_parquet(BytesIO(_response.read()))

    return course_parquet, mo, np, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 9: Hypothesis testing I, and what a p-value does and does not tell you

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, September 30, 2026

    **Reading due today:** Shasha and Wilson, *Statistics is Easy!*, ch. 1, pp. 1–6; ch. 3,
    pp. 19–25; ch. 4 §4.2, pp. 28–29

    ---

    ### Today you will be able to

    - Run a shuffle test and say what its p-value is the probability of
    - Say what a test that does not pass does and does not show
    - Test a claim somewhere other than where it was made
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 · RAT 6

    Canvas gave you your score and your own answers when you submitted, but not the key.
    We will re-poll the items that split the room.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:15 · Application exercise 7

    ## The streaky few

    This is Monday's file: NBA free throws from 2006–07 to 2015–16, one row per trip to the
    line with at least two shots.  Today we work with the 180 regular shooters that ended
    Monday's session, the players with at least 500 trips and at least 50 missed first shots.
    """)
    return


@app.cell
def _(course_parquet):
    trips = course_parquet("nba_free_throw_pairs.parquet")
    trips.head()
    return (trips,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### A worked shuffle test: LeBron's trips

    This is Chapter 1's shuffle test, applied to one player.  If the first shot made no
    difference to his second, the first-shot results could be shuffled among his trips
    without changing anything, so the test shuffles them 2,000 times and recomputes the gap
    each time.
    The share of shuffles whose gap is at least as large as the real one is the one-tailed
    p-value.
    """)
    return


@app.cell
def _(np):
    def second_shot_gap(some_trips):
        """Second-shot percentage after a make minus after a miss, in percentage points."""
        after_make = some_trips.loc[some_trips["first_made"], "second_made"].mean()
        after_miss = some_trips.loc[~some_trips["first_made"], "second_made"].mean()
        return 100 * (after_make - after_miss)

    def shuffle_test(some_trips, n_shuffles=2000, seed=385):
        """Chapter 1's shuffle test on one set of trips.  Returns (gap, p_value)."""
        first = some_trips["first_made"].to_numpy()
        second = some_trips["second_made"].to_numpy()
        observed = second_shot_gap(some_trips)

        # Each row of `shuffled` is one shuffle of the first-shot results.
        rng = np.random.default_rng(seed)
        shuffled = rng.permuted(np.tile(first, (n_shuffles, 1)), axis=1)
        after_make = (second & shuffled).sum(axis=1) / shuffled.sum(axis=1)
        after_miss = (second & ~shuffled).sum(axis=1) / (~shuffled).sum(axis=1)
        shuffled_gaps = 100 * (after_make - after_miss)

        return observed, float((shuffled_gaps >= observed).mean())

    return second_shot_gap, shuffle_test


@app.cell
def _(mo, shuffle_test, trips):
    _gap, _p = shuffle_test(trips[trips["player"] == "LeBron James"])
    mo.md(
        f"LeBron's gap is **{_gap:.1f}** percentage points, and **{_p:.1%}** of the "
        f"shuffles produced a gap at least that large.  His p-value is **{_p:.3f}**."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The same test on all 180

    The table runs `shuffle_test` once per regular shooter, which takes a few seconds.

    The analyst's run found 30 players passing at 5%.  This table uses its own shuffles, and
    a player whose p-value sits right at 0.05 can land on either side of the line from one
    run to the next, so your count may differ from the analyst's by one.
    """)
    return


@app.cell
def _(pd, shuffle_test, trips):
    _rows = []
    for _name, _t in trips.groupby("player"):
        _missed = int((~_t["first_made"]).sum())
        if len(_t) < 500 or _missed < 50:
            continue
        _gap, _p = shuffle_test(_t)
        _rows.append((_name, len(_t), _missed, round(_gap, 2), _p))

    league = pd.DataFrame(_rows, columns=["player", "trips", "missed_first", "gap", "p_value"])
    league["passed"] = league["p_value"] < 0.05
    league = league.sort_values("p_value").reset_index(drop=True)
    league
    return (league,)


@app.cell
def _(league, mo):
    mo.md(
        f"**Of {len(league)} players, {int(league['passed'].sum())} pass at 5%.**"
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Part 1: eight minutes, on your own, in silence

    > **The broadcast analyst is back.  "We ran the shuffle test on all 180 regular shooters.
    > Only 30 make their second shot significantly more often after a make.  For the other 150
    > the first shot makes no difference, and the league-wide effect comes from a few streaky
    > shooters."  Is the analyst right?**

    The analyst's sentence makes more than one claim.  Take a position on each, and write
    down what you would want to see before you believed it.  Please do not talk to your team
    yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:23 · With your team

    Argue to a decision.

    > **Is the analyst right?**
    >
    > **A.** Yes.  The 30 whose tests passed carry the effect, and the other 150 tests found
    > nothing.
    >
    > **B.** No, the analyst is wrong about the 150.  Tests that do not pass cannot show that
    > the first shot makes no difference, and as a group the 150 show the effect too.
    >
    > **C.** No, the analyst is wrong about the 30.  Players picked out by a passed test are
    > picked out partly by luck, and their streakiness would not hold up on other trips.
    >
    > **D.** The shuffle tests cannot settle it.  They were run one player at a time, and the
    > claim is about the league.

    ### Your team writes one test

    Choose the test that bears on your answer, and write it in the cells below.

    - **The share of the effect.**  Weight each player's gap by his missed first shots, and
      report the share carried by the players who passed.  It takes about five lines.
    - **The coin test.**  Count how many of the players who did not pass have a gap above
      zero.  If the first shot made no difference to them, each gap is as likely to fall
      below zero as above it, like a fair coin, which is Chapter 1's first example.  Flip that
      many coins 10,000 times and report how often chance reaches your count.  It takes about
      eight to ten lines.
    - **The split-half test.**  Run `shuffle_test` on each player's even-season trips only
      (2006–07, 2008–09, …), keep the players who pass, and compare their gap in the odd
      seasons with everyone else's.  It takes about ten to fifteen lines and is the hardest
      of the three.

    ### The justification

    Please paste your code and its result, then write three sentences:

    1. **Which part of the analyst's claim your test addresses.**
    2. **What your test would have shown if the analyst were right.**
    3. **Which part of the claim your test leaves unanswered.**

    ### Submitting

    **Submit on Canvas first**, to *AE 7: The streaky few*.  One person submits for the team,
    ideally a different person from last time, and includes, in this order, the team name,
    your letter, your code and its result, your justification, and who is here today.

    **Your code must be marked as code in the Canvas text box.**  Select the lines you
    pasted, open the **Format** menu in the editor toolbar, and choose **Code**.

    **Then in Sli.do**, click your letter.  Sli.do draws the histogram and is not graded.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Your team's test

    Each function below returns `None` until you write it, so please write the one your team
    chose.
    `league`, `trips` and `shuffle_test` are all available.  If you add cells, start new
    variable names with an underscore so they cannot collide with the notebook's own.
    """)
    return


@app.cell
def _():
    def share_of_effect(league_table):
        """Share of the league-wide effect carried by the players who passed.

        Weight each player's gap by his missed first shots.  Return a number between 0
        and 1.
        """
        return None

    def coin_test(heads, coins=150, runs=10_000):
        """Share of runs of `coins` fair coins with at least `heads` heads."""
        # np.random.default_rng(385) gives you a generator; its .integers or .binomial
        # methods will flip coins for you.
        return None

    def split_half():
        """Shuffle-test every regular shooter on even-season trips only.

        Return (number who pass, their mean odd-season gap, everyone else's mean
        odd-season gap).  trips["season"] looks like "2012-13".
        """
        return None

    return coin_test, share_of_effect, split_half


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The checks
    """)
    return


@app.cell
def _(coin_test, league, mo, share_of_effect, split_half):
    def _run(label, call, judge):
        try:
            _result = call()
        except Exception as _error:
            return mo.callout(mo.md(f"**{label}** raised an error: `{_error!r}`"),
                              kind="danger")
        if _result is None:
            return mo.callout(mo.md(f"**{label}** has not been written yet."), kind="info")
        _ok, _message = judge(_result)
        return mo.callout(mo.md(f"**{label}:** {_message}"),
                          kind="success" if _ok else "warn")

    def _judge_coin(_pair):
        _even, _far = _pair
        _ok = 0.4 <= _even <= 0.6 and _far < 0.001
        return _ok, (f"75 heads gives {_even:.3f} and 102 gives {_far:.4f}. "
                     + ("The check passes." if _ok else
                        "The check expected about 0.5 and something below 0.001."))

    def _judge_split(_result):
        _n, _theirs, _others = _result
        _ok = 12 <= _n <= 22
        return _ok, (f"{_n} players pass in the even seasons; in the odd seasons their "
                     f"gap is {_theirs:.1f} against {_others:.1f} for everyone else. "
                     + ("The check passes." if _ok else
                        "The check expected between 12 and 22 players to pass."))

    mo.vstack([
        _run("share_of_effect", lambda: share_of_effect(league),
             lambda _s: (0 < _s < 1, f"the players who passed carry {_s:.0%} of the effect.")),
        _run("coin_test", lambda: None if coin_test(75) is None else (coin_test(75), coin_test(102)),
             _judge_coin),
        _run("split_half", split_half, _judge_split),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:50 · Report

    All thirty-five teams reveal at once, and then four or five defend.

    When you defend, please lead with which part of the analyst's claim your test addresses,
    and what it leaves unanswered.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 1:15 · Consolidation

    The button below shows three fair tests of one claim side by side.
    """)
    return


@app.cell
def _(mo):
    show_tests = mo.ui.run_button(label="Show all three tests")
    show_tests
    return (show_tests,)


@app.cell
def _(league, mo, np, pd, second_shot_gap, show_tests, shuffle_test, trips):
    mo.stop(not show_tests.value)

    # The share of the effect.
    _w = league["missed_first"]
    _share = (league["gap"] * _w)[league["passed"]].sum() / (league["gap"] * _w).sum()

    # The coin test on the players who did not pass.
    _rest = league[~league["passed"]]
    _above = int((_rest["gap"] > 0).sum())
    _heads = np.random.default_rng(385).binomial(len(_rest), 0.5, size=10_000)
    _coin_p = float((_heads >= _above).mean())

    # The split-half test, in both directions.
    _regular = trips[trips["player"].isin(league["player"])]
    _even = _regular["season"].str[:4].astype(int) % 2 == 0
    _split_rows = []
    for _chosen_even in (True, False):
        _chosen = _regular[_even == _chosen_even]
        _other = _regular[_even != _chosen_even]
        _passers = {_name for _name, _t in _chosen.groupby("player")
                    if shuffle_test(_t)[1] < 0.05}
        _other_gaps = _other.groupby("player").apply(second_shot_gap)
        _split_rows.append((
            "even seasons" if _chosen_even else "odd seasons",
            len(_passers),
            round(_other_gaps[_other_gaps.index.isin(_passers)].mean(), 1),
            round(_other_gaps[~_other_gaps.index.isin(_passers)].mean(), 1),
        ))
    _split = pd.DataFrame(_split_rows, columns=[
        "selected on", "players passing", "their gap in the other half",
        "everyone else, other half"])

    mo.vstack([
        mo.md(f"""
    **The share of the effect.**  The {int(league['passed'].sum())} players who passed hold
    {_w[league['passed']].sum() / _w.sum():.0%} of the missed first shots and carry
    **{_share:.0%}** of the league-wide effect.

    **The coin test.**  {_above} of the {len(_rest)} players who did not pass have a gap above
    zero, where no effect would put about {len(_rest) // 2}.  In 10,000 runs of {len(_rest)}
    fair coins, the share reaching {_above} was **{_coin_p:.4f}**.

    **The split-half test.**  The table shows the players chosen by a passed test in one half
    of the seasons, and their gap in the other half.
    """),
        _split,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Each test is fair, and they disagree because they answer different parts of the claim.
    In this sample a few players do carry most of the effect, but the players whose tests did
    not pass still lean the same way as a group, far beyond what chance would produce, and
    the few would mostly not remain the few on other trips, because choosing players by a
    passed test chooses luck as well as streakiness.

    The analyst made RAT 6 Q2's error 150 times, reading "could easily have happened by
    chance" as "did not happen", and then the reverse error 30 times, reading a passed test
    as a streaky player.

    ### Before October 5

    - **Reading:** Bruce et al., *AI-Assisted Statistics for Data Scientists*, ch. 3, §§ *Multiple
      Testing*, *Degrees of Freedom* and *ANOVA*.
    - **RAT 7** opens Friday at 09:50 and closes Sunday at 20:59.
    - **DoU 1** is due Monday, October 5, at 23:59.
    """)
    return


if __name__ == "__main__":
    app.run()
