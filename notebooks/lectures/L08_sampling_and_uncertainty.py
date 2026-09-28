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
    # SI 385 — Data Exploration

    ## Session 8: Sampling, uncertainty, and why the order you look matters

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, September 28, 2026

    **Reading due today:** Shasha and Wilson, *Statistics is Easy!*, ch. 1, pp. 6–8, and
    ch. 2, pp. 11–15

    ---

    ### Today you will be able to

    - Write a bootstrap and say what its interval is an interval of
    - Choose what to resample, and say why that is the independent unit
    - Say what choosing a comparison after seeing the data does to its interval
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 — RAT 5

    Canvas gave you your score and your own answers when you submitted, but not the key.
    We will re-poll the items that split the room.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:15 — Application exercise 6

    ## The second free throw

    This is the file from the pre-read: NBA free throws from 2006–07 to 2015–16, one row
    per trip to the line with at least two shots.  `first_made` and `second_made` say
    whether each shot went in.

    The table is derived from the *NBA Free Throws* dataset published on Kaggle by
    Sebastian Mantey, which was collected from ESPN's play-by-play records.
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
    ### Across the whole file

    The second shot, split by what happened on the first:
    """)
    return


@app.cell
def _(trips):
    _pooled = trips.groupby("first_made")["second_made"].agg(
        trips="size", second_made_pct="mean"
    )
    _pooled["second_made_pct"] = (100 * _pooled["second_made_pct"]).round(1)
    _pooled
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### One player at a time

    Players differ a great deal at the line.  The table below gives every player's number
    of trips, the number of first shots they missed, and their free-throw percentage over
    both shots.  It deliberately leaves out the gap.
    """)
    return


@app.cell
def _(trips):
    _made = trips.groupby("player")[["first_made", "second_made"]].sum()
    players = trips.groupby("player").size().rename("trips").to_frame()
    players["missed_first"] = players["trips"] - _made["first_made"]
    players["ft_pct"] = (
        100 * (_made["first_made"] + _made["second_made"]) / (2 * players["trips"])
    ).round(1)
    players = players.sort_values("trips", ascending=False)
    players
    return (players,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Please choose a player to see their second shot split by the first.  The gap is the
    second-shot percentage after a make minus the second-shot percentage after a miss, in
    percentage points.
    """)
    return


@app.cell
def _(mo, players):
    player_choice = mo.ui.dropdown(
        options=sorted(players.index[players["trips"] >= 100]),
        value="LeBron James",
        label="Player:",
    )
    return (player_choice,)


@app.cell
def _(mo, player_choice, trips):
    _one = trips[trips["player"] == player_choice.value]
    _split = _one.groupby("first_made")["second_made"].agg(
        trips="size", second_made_pct="mean"
    )
    _split["second_made_pct"] = 100 * _split["second_made_pct"]
    _gap = _split.loc[True, "second_made_pct"] - _split.loc[False, "second_made_pct"]
    _split["second_made_pct"] = _split["second_made_pct"].round(1)
    mo.vstack([
        player_choice,
        _split,
        mo.md(f"**Gap: {_gap:.1f} percentage points**, from {len(_one):,} trips."),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Part 1 — eight minutes, on your own, in silence

    > **LeBron James has just missed the first of two free throws.  The broadcast analyst
    > says, "The numbers say that makes no difference to the second."  Is the analyst
    > right?**

    Take a position, and write down whose free throws you would want as evidence before
    you answered.  Please do not talk to your team yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:23 — With your team

    Argue to a decision.

    > **Is the analyst right?**
    >
    > **A.** Yes.  LeBron's own 3,376 trips give a gap of 1.5 percentage points, with a
    > 90% interval of −1.0 to 4.3.  Zero is inside it, so his data show no effect.
    >
    > **B.** No.  Across the league, a player's second shot goes in 2.3 points more often
    > after a make, with an interval of 1.9 to 2.7.  LeBron's own estimate is consistent
    > with that, and his own data are too few to overrule it.
    >
    > **C.** No, but not because of the first shot.  A miss tells you he is having a bad
    > night or a bad season, which lowers the second shot too.  The data show that the two
    > shots are related, not that one affects the other.
    >
    > **D.** The data cannot say for LeBron.  The league-wide effect is 3.2 points for
    > 65–75% shooters and 1.7 for 75–85% shooters, he sits at 74.8%, and his own interval
    > is too wide to choose between them.

    ### Your team writes a bootstrap

    The justification includes **a bootstrap you write yourselves** for the evidence your
    answer rests on, and the 90% interval it produces.  The cells below give you a
    working bootstrap for LeBron's own trips to start from, and a check your version has
    to pass.

    ### The justification

    Paste your code and its interval, then three or four sentences:

    1. **Which evidence your answer rests on**, and why that evidence is about LeBron
       rather than about someone else.
    2. **What your code resamples**, and why that is the right unit.
    3. **When you chose your players**: before or after seeing any group's gap.
    4. **Which result would have changed your answer.**

    ### Submitting

    **On Canvas first**, *AE 6: The second free throw*.  One person for the team, ideally
    a different person from last time.  In this order: team name, your letter, your code
    and its interval, your justification, and who is here today.

    **Your code must be marked as code in the Canvas text box.**  Select the lines you
    pasted, open the **Format** menu in the editor toolbar, and choose **Code**.

    **Then in Sli.do**, click your letter.  Sli.do draws the histogram and is not graded.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## A worked bootstrap: LeBron's own trips

    This follows the pseudocode in Shasha and Wilson ch. 1.  The first cell measures the
    gap for any set of trips.  The second draws LeBron's trips with replacement, as many
    as he took, measures the gap in the resample, repeats that 2,000 times, and reads the
    90% interval off the 5th and 95th percentiles.
    """)
    return


@app.function
def second_shot_gap(some_trips):
    """Second-shot percentage after a make minus after a miss, in percentage points."""
    after_make = some_trips.loc[some_trips["first_made"], "second_made"].mean()
    after_miss = some_trips.loc[~some_trips["first_made"], "second_made"].mean()
    return 100 * (after_make - after_miss)


@app.cell
def _(mo, np, trips):
    lebron = trips[trips["player"] == "LeBron James"]

    _rng = np.random.default_rng(385)
    lebron_gaps = []
    for _ in range(2000):
        _resample = lebron.sample(n=len(lebron), replace=True, random_state=_rng)
        lebron_gaps.append(second_shot_gap(_resample))

    lebron_low, lebron_high = np.percentile(lebron_gaps, [5, 95])
    mo.md(
        f"LeBron's gap is **{second_shot_gap(lebron):.1f}** percentage points, "
        f"with a 90% interval of **{lebron_low:.1f} to {lebron_high:.1f}**."
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Your team's bootstrap

    If your evidence is a group of players, the bootstrap has to **resample players, not
    trips**.  One player's trips are not independent of one another: a player who shoots
    badly shoots badly on both shots.  Ch. 2 of the reading, item 5, is about exactly this.

    Resampling players means drawing player names with replacement, as many names as
    there are in the group, and then gathering every trip of every drawn player, twice
    over for a player drawn twice.  The worked example above does not show that step.

    Please write `group_bootstrap` below.  It takes the trips, a list of player names and
    a number of resamples, and returns the 5th and 95th percentiles of the gap.  Until you
    write it, it returns `None`.
    """)
    return


@app.function
def group_bootstrap(some_trips, player_names, n_resamples=1000):
    """90% bootstrap interval for the second-shot gap, resampling players.

    Returns (low, high) in percentage points.
    """
    # Your team's code goes here.  Every version needs three pieces:
    #   - draw len(player_names) names from player_names, with replacement
    #   - gather the trips of every drawn name, and measure second_shot_gap
    #   - repeat n_resamples times, then take the 5th and 95th percentiles
    #
    # second_shot_gap is defined above, and np.random.default_rng gives you a
    # generator with a .choice method.  If you add cells, start new variable
    # names with an underscore so they cannot collide with the notebook's own.
    return None


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The check: Josh Smith and Kevin Martin

    These two sit at opposite ends.  Josh Smith was a weak free-throw shooter who was much
    better after a make; Kevin Martin was one of the best in the file and slightly worse
    after one.  For a group of just these two, a bootstrap that resamples players has to
    produce an interval that reaches both of their own gaps.
    """)
    return


@app.cell
def _(mo, trips):
    _pair = trips[trips["player"].isin(["Josh Smith", "Kevin Martin"])]
    _smith = second_shot_gap(_pair[_pair["player"] == "Josh Smith"])
    _martin = second_shot_gap(_pair[_pair["player"] == "Kevin Martin"])
    _pooled = second_shot_gap(_pair)

    _facts = mo.md(
        f"| | Gap |\n|---|---|\n"
        f"| Josh Smith | {_smith:.1f} |\n"
        f"| Kevin Martin | {_martin:.1f} |\n"
        f"| The two pooled | {_pooled:.1f} |"
    )

    try:
        _result = group_bootstrap(trips, ["Josh Smith", "Kevin Martin"])
    except Exception as _error:
        _verdict = mo.callout(
            mo.md(f"`group_bootstrap` raised an error: `{_error!r}`"), kind="danger"
        )
    else:
        if _result is None:
            _verdict = mo.callout(
                mo.md("`group_bootstrap` has not been written yet."), kind="info"
            )
        else:
            _low, _high = _result
            if _low <= _martin + 0.1 and _high >= _smith - 0.1:
                _verdict = mo.callout(
                    mo.md(f"Your interval, **{_low:.1f} to {_high:.1f}**, reaches both "
                          "players' gaps. The check passes."),
                    kind="success",
                )
            else:
                _verdict = mo.callout(
                    mo.md(f"Your interval, **{_low:.1f} to {_high:.1f}**, does not reach "
                          "both players' gaps. An interval that sits above both of them "
                          "usually means the code resamples trips rather than players."),
                    kind="warn",
                )

    mo.vstack([_facts, _verdict])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Look at the pooled gap before you move on.  It is larger than either player's own, and
    working out why is worth a minute of your team's time.

    ### Your evidence

    Please put your team's players in the list below.  If your evidence is LeBron alone,
    the worked example is already your bootstrap, so try `group_bootstrap` on him anyway
    and work out why the interval it gives has no width.
    """)
    return


@app.cell
def _(trips):
    _our_players = []
    group_bootstrap(trips, _our_players) if _our_players else None
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:50 — Report

    All thirty-five teams reveal at once.  Then four or five defend.

    When you defend, please lead with whose free throws your interval came from, and when
    you chose them.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 1:15 — Consolidation

    The table below runs the bootstrap for every player with at least 500 trips and 50
    missed first shots, one player at a time, and sorts them by the low end of the
    interval.
    """)
    return


@app.cell
def _(mo):
    show_league = mo.ui.run_button(label="Show the league table")
    show_league
    return (show_league,)


@app.cell
def _(mo, np, pd, show_league, trips):
    mo.stop(not show_league.value)

    # One interval per regular shooter, resampling that player's own trips.  This is
    # the worked example above, vectorised so that 180 players take seconds.
    _rng = np.random.default_rng(385)
    _rows = []
    for _name, _t in trips.groupby("player"):
        _first = _t["first_made"].to_numpy()
        _second = _t["second_made"].to_numpy()
        if len(_t) < 500 or (~_first).sum() < 50:
            continue
        _idx = _rng.integers(0, len(_t), size=(1000, len(_t)))
        _f, _s = _first[_idx], _second[_idx]
        _gaps = 100 * ((_s & _f).sum(1) / _f.sum(1) - (_s & ~_f).sum(1) / (~_f).sum(1))
        _low, _high = np.percentile(_gaps, [5, 95])
        _gap = 100 * (_second[_first].mean() - _second[~_first].mean())
        _rows.append((_name, len(_t), round(_gap, 1), round(_low, 1), round(_high, 1)))

    _league = (
        pd.DataFrame(_rows, columns=["player", "trips", "gap", "low", "high"])
        .sort_values("low", ascending=False)
        .reset_index(drop=True)
    )
    _above = int((_league["low"] > 0).sum())
    _below = int((_league["high"] < 0).sum())
    mo.vstack([
        mo.md(f"**{len(_league)} players.** {_above} intervals sit above zero and "
              f"{_below} below it.  With no effect at all, about "
              f"{round(0.05 * len(_league))} would sit on each side by chance."),
        _league,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Suppose the question had not named LeBron.  Somebody scans this table, finds the
    player at the top, and reports that player's interval.  With this many players, a
    handful would clear zero by chance alone, and the scan cannot tell which ones.  The
    90% on the reported interval describes a procedure that draws one player's trips and
    stops, which is not what was done.

    The question named its player in advance, which is why LeBron's interval means what it
    says.  The same holds for your team's group: an interval for a group chosen before
    looking carries its 90%, and one chosen after trying several does not.

    ### Before September 30

    - **Reading:** Shasha and Wilson, *Statistics is Easy!*, ch. 1, pp. 1–6; ch. 3,
      pp. 19–25; ch. 4 §4.2, pp. 28–29.
    - **RAT 6** opens Monday at 09:50 and closes Tuesday at 20:59.
    """)
    return


if __name__ == "__main__":
    app.run()
