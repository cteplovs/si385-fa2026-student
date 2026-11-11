# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 8: Sampling, uncertainty, and why the order you look matters

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, September 28, 2026

    The reading for this session is Shasha and Wilson, *Statistics is Easy*, chapter 1, pages 6 to
    8, and chapter 2, pages 11 to 15.

    ---

    ### Today you will be able to

    - Explain why a statistic computed from a sample would come out differently in another sample,
      and how the sample size changes how much
    - Compute a bootstrap interval, and say what it does and does not describe
    - Resample the right unit when the rows come in groups, and say what goes wrong when you do not
    - Tell an exploratory result from a confirmatory one, and check a pattern on data that played
      no part in finding it

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Data, pooled and one player at a time | 10 |
    | Samples differ | 5 |
    | The bootstrap | 10 |
    | Resampling the right unit | 10 |
    | Exploring and confirming | 10 |
    | Today's question, in teams | 20 |
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

    return course_parquet, mo, np, pd, plt


@app.cell(hide_code=True)
def code_on_its_own_note(mo):
    mo.md(r"""
    ### Sections headed *The code on its own*

    Each technique ends with a section headed *The code on its own*. The sliders, dropdowns and
    plots above it call functions written for this notebook, which you will not have when you work
    on your own data. The code in those sections uses only pandas and NumPy, starts from a data
    frame, and does the computation without any controls, so that you can copy it into your project
    or another notebook. Each code cell starts with a comment listing the imports it uses, and its
    variable names start with `_`, which keeps them local to the cell.
    """)
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## Data

    The file holds every trip to the line for two free throws in the NBA from the 2006-07 season to
    the 2015-16 season, 268,094 trips with one row each, from ESPN's play-by-play records as
    collected by Sebastian Mantey.

    | Column | Description |
    |---|---|
    | `player` | Who took the two shots |
    | `season` | The season, such as `2012-13` |
    | `playoffs` | Whether the trip was in the playoffs |
    | `first_made`, `second_made` | Whether each shot went in |

    Throughout the session, the question is whether making the first shot changes the chance of
    making the second. The *gap* is the share of second shots made after a make minus the share made
    after a miss, in percentage points.
    """)
    return


@app.cell
def load_trips(course_parquet):
    trips = course_parquet("nba_free_throw_pairs.parquet")
    trips.head()
    return (trips,)


@app.cell
def define_gap():
    def second_shot_gap(rows):
        """Second-shot percentage after a make minus after a miss, in percentage points."""
        after_make = rows.loc[rows["first_made"], "second_made"].mean()
        after_miss = rows.loc[~rows["first_made"], "second_made"].mean()
        return 100 * (after_make - after_miss)

    return (second_shot_gap,)


@app.cell
def define_cells(np, pd):
    def player_cells(rows):
        """For each player, the four counts of trips: make-make, make-miss, miss-make, miss-miss."""
        _first, _second = rows["first_made"], rows["second_made"]
        return pd.DataFrame({
            "player": rows["player"],
            "mm": _first & _second, "mx": _first & ~_second,
            "xm": ~_first & _second, "xx": ~_first & ~_second,
        }).groupby("player").sum()


    def cell_gap(counts):
        """The gap from an array of counts whose last axis is (mm, mx, xm, xx)."""
        counts = np.asarray(counts, dtype=float)
        return 100 * (counts[..., 0] / (counts[..., 0] + counts[..., 1])
                      - counts[..., 2] / (counts[..., 2] + counts[..., 3]))

    return cell_gap, player_cells


@app.cell
def regulars(cell_gap, player_cells, trips):
    # The players with at least 500 trips and 50 missed first shots, each with their own gap.
    cells = player_cells(trips)
    regular_cells = cells[(cells.sum(axis=1) >= 500) & (cells["xm"] + cells["xx"] >= 50)].copy()
    regular_cells["gap"] = cell_gap(regular_cells[["mm", "mx", "xm", "xx"]].to_numpy())
    regular_cells["ft_pct"] = (100 * (2 * regular_cells["mm"] + regular_cells["mx"]
                                      + regular_cells["xm"])
                               / (2 * regular_cells[["mm", "mx", "xm", "xx"]].sum(axis=1)))
    return cells, regular_cells


@app.cell(hide_code=True)
def pooled_intro(mo, regular_cells, second_shot_gap, trips):
    mo.md(f"""
    ---
    ## Pooled, and one player at a time

    Pooling every trip in the file, the gap is **{second_shot_gap(trips):.1f}** points. For the
    **{len(regular_cells)}** players with at least 500 trips and 50 missed first shots, the median
    of their own gaps is **{regular_cells['gap'].median():.1f}** points. The two numbers answer
    different questions, for session 6's reason: good shooters make more first shots and more
    second shots, so pooling puts most of the makes with good shooters and most of the misses with
    poor ones, and the pooled gap compares players as well as shots. The plot shows each regular
    player's gap against their free-throw percentage.
    """)
    return


@app.cell
def pooled_plot(plt, regular_cells):
    _fig, _ax = plt.subplots(figsize=(7, 3.8))
    _ax.scatter(regular_cells["ft_pct"], regular_cells["gap"], s=14, alpha=0.7, color="#1f4e79")
    _ax.axhline(0, color="#111827", linewidth=1)
    _ax.set_xlabel("Free-throw percentage, both shots")
    _ax.set_ylabel("Player's own gap, points")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def samples_intro(mo):
    mo.md(r"""
    ---
    ## Samples differ

    A statistic computed from a sample would come out differently in another sample. To see by how
    much, we draw 300 random samples of trips from the whole file, compute the gap in each, and plot
    the 300 gaps. Please move the slider to change the size of each sample and watch the spread of
    the gaps.
    """)
    return


@app.cell
def samples_control(mo):
    # mo.ui.slider is a marimo function that makes a slider; its .value is the chosen setting.
    sample_size = mo.ui.slider(steps=[100, 300, 1000, 3000, 10000, 30000], value=1000,
                               label="Trips in each sample", show_value=True)
    sample_size
    return (sample_size,)


@app.cell
def samples_plot(cell_gap, mo, np, plt, sample_size, trips):
    _first = trips["first_made"].to_numpy()
    _second = trips["second_made"].to_numpy()
    _codes = 2 * (~_first) + (~_second)  # 0 mm, 1 mx, 2 xm, 3 xx
    _rng = np.random.default_rng(385)
    _gaps = np.array([cell_gap(np.bincount(_codes[_rng.integers(0, len(_codes), sample_size.value)],
                                           minlength=4)) for _ in range(300)])
    _fig, _ax = plt.subplots(figsize=(7, 2.8))
    _ax.hist(_gaps, bins=30, range=(-30, 40), color="#9ca3af")
    _ax.set_xlabel("Gap in the sample, points")
    _ax.set_yticks([])
    _ax.spines[["top", "right", "left"]].set_visible(False)
    _fig.tight_layout()
    _low, _high = np.percentile(_gaps, [5, 95])
    # mo.vstack is a marimo function that stacks outputs one above the other.
    mo.vstack([_fig, mo.md(f"The middle 90% of the 300 gaps runs from **{_low:.1f}** to "
                           f"**{_high:.1f}** points.")])
    return


@app.cell(hide_code=True)
def samples_reading(mo):
    mo.md(r"""
    The spread of the gaps shrinks as the samples grow, roughly in proportion to one over the
    square root of the sample size, so a sample a hundred times larger gives gaps about ten times
    closer together. In practice we have one sample and cannot draw another, which is the problem
    the bootstrap addresses.
    """)
    return


@app.cell(hide_code=True)
def bootstrap_intro(mo):
    mo.md(r"""
    ---
    ## The bootstrap

    The reading's bootstrap treats the sample as a stand-in for the population. It draws a new
    sample of the same size *with replacement*, so that some rows appear more than once and others
    not at all, computes the statistic, and repeats this many times. The spread of the resampled
    statistics estimates how much the statistic would vary from sample to sample, and the 5th and
    95th percentiles of them give a 90% interval.

    Please choose a player and a number of resamples.
    """)
    return


@app.cell
def bootstrap_controls(mo, regular_cells):
    # mo.ui.dropdown is a marimo function that makes a drop-down menu; its .value is the choice.
    player_pick = mo.ui.dropdown(options=sorted(regular_cells.index), value="LeBron James",
                                 label="Player")
    resample_count = mo.ui.slider(steps=[100, 500, 1000, 2000, 5000], value=1000,
                                  label="Resamples", show_value=True)
    # mo.hstack is a marimo function that puts outputs side by side.
    mo.hstack([player_pick, resample_count], justify="start", gap=2)
    return player_pick, resample_count


@app.cell
def bootstrap_view(cell_gap, mo, np, player_pick, plt, regular_cells, resample_count):
    _counts = regular_cells.loc[player_pick.value, ["mm", "mx", "xm", "xx"]].to_numpy(dtype=int)
    _rng = np.random.default_rng(385)
    # Resampling a player's trips with replacement is the same as drawing new counts of the four
    # kinds of trip, with the player's own shares as the probabilities.
    _resampled = cell_gap(_rng.multinomial(_counts.sum(), _counts / _counts.sum(),
                                           size=resample_count.value))
    _low, _high = np.percentile(_resampled, [5, 95])
    _fig, _ax = plt.subplots(figsize=(7, 2.8))
    _ax.hist(_resampled, bins=40, color="#9ca3af")
    _ax.axvspan(_low, _high, color="#1f4e79", alpha=0.15)
    _ax.axvline(0, color="#111827", linewidth=1)
    _ax.set_xlabel("Gap in the resample, points")
    _ax.set_yticks([])
    _ax.spines[["top", "right", "left"]].set_visible(False)
    _fig.tight_layout()
    mo.vstack([_fig, mo.md(
        f"{player_pick.value} took **{_counts.sum():,}** trips and missed **{_counts[2:].sum()}** "
        f"first shots, for a gap of **{cell_gap(_counts):.1f}** points, with a 90% bootstrap "
        f"interval of **{_low:.1f}** to **{_high:.1f}**.")])
    return


@app.cell(hide_code=True)
def bootstrap_reading(mo):
    mo.md(r"""
    The interval is wide for most players because a gap depends on the second shots after a miss,
    and even a regular player misses only a few hundred first shots over ten seasons. More resamples
    make the interval's ends more stable, but they do not make it narrower, because the width comes
    from the data and not from the number of resamples.

    A bootstrap interval describes how much the statistic would vary across samples like this one.
    It does not correct a sample that is unlike the population, and the reading's chapter 2 lists
    the conditions it needs, the most important of which is that the resampled units are
    independent of one another.
    """)
    return


@app.cell(hide_code=True)
def bootstrap_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute a statistic for a set of rows, resample the rows with replacement
    2,000 times, and take the 5th and 95th percentiles of the resampled statistics. To use it on
    other data, you would change the rows and the function `_statistic`.
    """)
    return


@app.cell
def bootstrap_code(np, trips):
    # Uses: import numpy as np
    def _statistic(rows):
        after_make = rows.loc[rows["first_made"], "second_made"].mean()
        after_miss = rows.loc[~rows["first_made"], "second_made"].mean()
        return 100 * (after_make - after_miss)

    _rows = trips[trips["player"] == "LeBron James"]
    _rng = np.random.default_rng(385)
    _resampled = [_statistic(_rows.sample(n=len(_rows), replace=True, random_state=_rng))
                  for _ in range(2000)]
    _low, _high = np.percentile(_resampled, [5, 95])
    print(f"statistic {_statistic(_rows):.1f}, 90% interval {_low:.1f} to {_high:.1f}")
    return


@app.cell(hide_code=True)
def unit_intro(mo):
    mo.md(r"""
    ---
    ## Resampling the right unit

    The trips are not independent of one another, because a player's trips share the player: a
    good shooter's trips all lean one way. Resampling trips treats every trip as independent, while
    resampling players, drawing whole players with replacement and keeping each one's trips
    together, matches the way the data vary when a different set of players takes the shots.

    The table below gives two statistics for a group of players, with a 90% interval from each kind
    of resampling. The *pooled gap* is computed from all the group's trips together, and the *mean
    of own gaps* is the average of each player's own gap. Please choose a group of players by their
    free-throw percentage and compare the intervals.
    """)
    return


@app.cell
def unit_control(mo):
    # mo.ui.range_slider is a marimo function that makes a slider with two ends; its .value is a
    # pair of numbers.
    pct_range = mo.ui.range_slider(start=40, stop=95, step=5, value=[40, 95],
                                   label="Free-throw percentage of the players", show_value=True)
    pct_range
    return (pct_range,)


@app.cell
def define_group_intervals(cell_gap, np, pd):
    def group_intervals(group, resamples=1000, seed=385):
        """The pooled gap and the mean of own gaps for a group of players, each with 90%
        intervals from resampling trips and from resampling players."""
        _counts = group[["mm", "mx", "xm", "xx"]].to_numpy(dtype=int)
        _total = _counts.sum(axis=0)
        _rng = np.random.default_rng(seed)
        _players = _rng.integers(0, len(_counts), (resamples, len(_counts)))
        _draws = {
            "pooled gap": (
                cell_gap(_rng.multinomial(_total.sum(), _total / _total.sum(), size=resamples)),
                cell_gap(_counts[_players].sum(axis=1))),
            "mean of own gaps": (
                np.mean([cell_gap(_rng.multinomial(_c.sum(), _c / _c.sum(), size=resamples))
                         for _c in _counts], axis=0),
                cell_gap(_counts)[_players].mean(axis=1)),
        }
        _values = {"pooled gap": cell_gap(_total), "mean of own gaps": cell_gap(_counts).mean()}
        return pd.DataFrame({
            _name: {"value": _values[_name],
                    "trips: low": np.percentile(_trips, 5), "trips: high": np.percentile(_trips, 95),
                    "players: low": np.percentile(_by_players, 5),
                    "players: high": np.percentile(_by_players, 95)}
            for _name, (_trips, _by_players) in _draws.items()}).T.round(2)

    return (group_intervals,)


@app.cell
def unit_view(group_intervals, mo, pct_range, regular_cells):
    _low, _high = pct_range.value
    _group = regular_cells[regular_cells["ft_pct"].between(_low, _high)]
    mo.stop(len(_group) < 5, mo.md("Please widen the range: it holds fewer than five players."))
    mo.vstack([mo.md(f"**{len(_group)}** players have a free-throw percentage from {_low} to "
                     f"{_high}."), group_intervals(_group)])
    return


@app.cell(hide_code=True)
def unit_reading(group_intervals, mo, regular_cells):
    _all = group_intervals(regular_cells)
    _p = _all.loc["pooled gap"]
    mo.md(f"""
    For all the regular players, the pooled gap's interval from resampling trips runs from
    **{_p['trips: low']:.2f}** to **{_p['trips: high']:.2f}**, and from resampling players from
    **{_p['players: low']:.2f}** to **{_p['players: high']:.2f}**. The pooled gap depends on which
    players are in the group, because it mixes good and poor shooters, and only resampling players
    lets that mix vary, so the interval from resampling trips is too narrow for a claim about
    players in general.

    For the mean of own gaps, the two intervals are close in these data, because each player's own
    gap is so noisy that resampling a player's trips already moves it about as much as replacing the
    player would. Resampling players is still the right choice, because it gives an honest interval
    whether or not that happens to be true. The mean of own gaps is also the better statistic for a
    question about what a make does to the same player's next shot, since it compares each player
    with themselves.
    """)
    return


@app.cell(hide_code=True)
def unit_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute one statistic for each group, here each player's own gap, and
    then resample the groups with replacement 2,000 times and take the percentiles of their mean.
    To use it on other data, you would change the grouping column and the statistic.
    """)
    return


@app.cell
def unit_code(np, trips):
    # Uses: import numpy as np
    def _statistic(rows):
        after_make = rows.loc[rows["first_made"], "second_made"].mean()
        after_miss = rows.loc[~rows["first_made"], "second_made"].mean()
        return 100 * (after_make - after_miss)

    _counts = trips.groupby("player").agg(trips=("first_made", "size"),
                                         missed=("first_made", lambda _f: (~_f).sum()))
    _kept = _counts.index[(_counts["trips"] >= 500) & (_counts["missed"] >= 50)]
    _per_group = (trips[trips["player"].isin(_kept)].groupby("player")[["first_made", "second_made"]]
                  .apply(_statistic).to_numpy())
    _rng = np.random.default_rng(385)
    _means = [_rng.choice(_per_group, size=len(_per_group), replace=True).mean()
              for _ in range(2000)]
    _low, _high = np.percentile(_means, [5, 95])
    print(f"{len(_per_group)} groups, mean {_per_group.mean():.2f}, "
          f"90% interval {_low:.2f} to {_high:.2f}")
    return


@app.cell(hide_code=True)
def explore_intro(mo):
    mo.md(r"""
    ---
    ## Exploring and confirming

    A pattern found by searching the data is an *exploratory* result. Checking it on the same data
    that suggested it cannot confirm it, because the search picks out whatever the noise in those
    data happened to favour. The remedy is to divide the data before looking: explore one part and
    confirm on the other.

    Here we divide each player's trips by season, those from seasons starting in an even year and
    those from seasons starting in an odd year. We pick the players with the largest gaps in the
    even seasons and then measure the same players in the odd seasons. Please move the slider to
    change how many players are picked.
    """)
    return


@app.cell
def explore_control(mo):
    pick_count = mo.ui.slider(start=5, stop=60, step=5, value=10,
                              label="Players picked from the even seasons", show_value=True)
    pick_count
    return (pick_count,)


@app.cell
def halves(cell_gap, player_cells, trips):
    # Each player's gap in the even seasons and in the odd seasons, for players with at least 250
    # trips and 25 missed first shots in each half.
    _even = trips["season"].str[:4].astype(int) % 2 == 0
    _parts = {}
    for _name, _mask in (("even", _even), ("odd", ~_even)):
        _c = player_cells(trips[_mask])
        _c = _c[(_c.sum(axis=1) >= 250) & (_c["xm"] + _c["xx"] >= 25)]
        _parts[_name] = _c.assign(gap=cell_gap(_c[["mm", "mx", "xm", "xx"]].to_numpy()))["gap"]
    half_gaps = (_parts["even"].rename("even").to_frame()
                 .join(_parts["odd"].rename("odd"), how="inner"))
    return (half_gaps,)


@app.cell
def explore_view(half_gaps, mo, pick_count):
    _picked = half_gaps.sort_values("even", ascending=False).head(pick_count.value)
    _rest = half_gaps.drop(index=_picked.index)
    mo.md(f"""
    Of **{len(half_gaps)}** players with enough trips in both halves, the **{len(_picked)}**
    with the largest gaps in the even seasons averaged **{_picked['even'].mean():.1f}** points
    there. In the odd seasons, the same players averaged **{_picked['odd'].mean():.1f}** points,
    and everyone else **{_rest['odd'].mean():.1f}**.
    """)
    return


@app.cell(hide_code=True)
def explore_reading(mo):
    mo.md(r"""
    The picked players' gaps fall a long way in the half that played no part in picking them,
    because a large gap in one half is partly skill and partly luck, and the luck does not repeat.
    What remains in the odd seasons is the better estimate of how different those players are. The
    same reasoning applies to any pattern you find by looking through many possibilities, which is
    why the reading insists on deciding what to test before looking at the data that will test it.
    """)
    return


@app.cell(hide_code=True)
def explore_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we divide the rows into two halves before looking, compute the statistic
    for each group in each half, pick the groups with the largest values in the first half, and
    compare them with everyone else in the second half.
    """)
    return


@app.cell
def explore_code(trips):
    def _statistic(rows):
        after_make = rows.loc[rows["first_made"], "second_made"].mean()
        after_miss = rows.loc[~rows["first_made"], "second_made"].mean()
        return 100 * (after_make - after_miss)

    _first_half = trips["season"].str[:4].astype(int) % 2 == 0
    _by_half = {}
    for _name, _rows in (("explore", trips[_first_half]), ("confirm", trips[~_first_half])):
        _counts = _rows.groupby("player")["first_made"].agg(
            trips="size", missed=lambda _f: (~_f).sum())
        _kept = _counts.index[(_counts["trips"] >= 250) & (_counts["missed"] >= 25)]
        _by_half[_name] = (_rows[_rows["player"].isin(_kept)]
                           .groupby("player")[["first_made", "second_made"]].apply(_statistic))
    _both = _by_half["explore"].rename("explore").to_frame().join(
        _by_half["confirm"].rename("confirm"), how="inner")
    _picked = _both.nlargest(10, "explore")
    print(f"picked: {_picked['explore'].mean():.1f} when exploring, "
          f"{_picked['confirm'].mean():.1f} when confirming; "
          f"everyone else {_both.drop(index=_picked.index)['confirm'].mean():.1f}")
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    A coach says that players shoot their second free throw better when the first one goes in.

    > **Use these data to say whether making the first free throw changes a player's chance of
    > making the second, and how sure you can be.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. The gap for the group of players you chose, measured within players, with a 90% interval
       from resampling players.
    2. The same group checked on data that played no part in choosing it: the players' gaps in the
       odd seasons, if you chose the group from the even seasons.
    3. One limitation: something these data cannot show about the coach's claim.

    Then compare your results with your teammates', who chose different groups of players, and say
    what their results showed that yours did not, and whether that changes your answer.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each
    prompt, in your own words and with the numbers from your own runs. Each of you should then
    upload your own copy of this notebook to *AE 6* on Canvas, by 23:59 on Tuesday.

    | Part of your answer | Points |
    |---|---:|
    | Your answer: the gap and its interval, the check on the other seasons, and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop rather than watching one
    screen, and choose a different group of players from your teammates, for example poor
    shooters, good shooters or everyone, then compare what you find. Your team may agree on an
    answer, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholders in Step 1, run
    the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_choose():
    # Step 1: choose a group of regular players by free-throw percentage, different from your
    # teammates'. Replace the two placeholders with numbers from 40 to 95.
    answer_low_pct = "SOME_NUMBER"
    answer_high_pct = "SOME_NUMBER"
    return answer_high_pct, answer_low_pct


@app.cell
def step2_interval(answer_high_pct, answer_low_pct, group_intervals, mo, regular_cells):
    # Step 2: the group's pooled gap and the mean of its players' own gaps, each with 90%
    # intervals from resampling trips and from resampling players.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder values.
    mo.stop("SOME_NUMBER" in (answer_low_pct, answer_high_pct),
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md("Replace the placeholders in Step 1 with numbers.").callout(kind="info"))
    answer_group = regular_cells[regular_cells["ft_pct"].between(answer_low_pct, answer_high_pct)]
    print(f"{len(answer_group)} players")
    group_intervals(answer_group)
    return (answer_group,)


@app.cell
def step3_halves(answer_group, half_gaps):
    # Step 3: your group's players in the two halves of the seasons. If you chose your group by
    # looking at its gaps, compare the half you looked at with the other.
    _both = half_gaps[half_gaps.index.isin(answer_group.index)]
    print(f"{len(_both)} of your players have enough trips in both halves")
    _both.mean().round(2).rename("mean gap")
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L08_sampling_and_uncertainty.py` to *AE 6* on Canvas by 23:59 on Tuesday. We will
    cross-reference your claims about evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_gap(mo):
    mo.md(r"""
    **The gap for your group of players, with its interval and the unit you resampled**
    """)
    return


@app.cell
def step4_answer_gap(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_check(mo):
    mo.md(r"""
    **What the check on the other half of the seasons showed**
    """)
    return


@app.cell
def step4_answer_check(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_limitation(mo):
    mo.md(r"""
    **One limitation of your answer**
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
