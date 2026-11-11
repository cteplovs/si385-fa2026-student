# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
#     "scipy>=1.13",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 9: Hypothesis testing I, and what a p-value does and does not tell you

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, September 30, 2026

    The reading for this session is Shasha and Wilson, *Statistics is Easy*, chapter 1, pages 1 to
    6, chapter 3, pages 19 to 25, and chapter 4, section 4.2, pages 28 and 29.

    ---

    ### Today you will be able to

    - Run a shuffle test, and say what its p-value is the share of
    - Run a t-test, read its statistic and p-value, and compare it with the shuffle test
    - Say what a p-value does not tell you: the size of an effect, or the chance that the
      hypothesis is true
    - Explain why testing many players finds some that pass by chance, and check a result on data
      that played no part in finding it

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Data | 5 |
    | A shuffle test | 10 |
    | The t-test | 10 |
    | What a p-value does not tell you | 10 |
    | Many tests at once | 10 |
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
    from scipy import stats

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

    return course_parquet, mo, np, pd, plt, stats


@app.cell(hide_code=True)
def code_on_its_own_note(mo):
    mo.md(r"""
    ### Sections headed *The code on its own*

    Each technique ends with a section headed *The code on its own*. The sliders, dropdowns and
    plots above it call functions written for this notebook, which you will not have when you work
    on your own data. The code in those sections uses only pandas, NumPy and SciPy, starts from a
    data frame, and does the computation without any controls, so that you can copy it into your
    project or another notebook. Each code cell starts with a comment listing the imports it uses,
    and its variable names start with `_`, which keeps them local to the cell.
    """)
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## Data

    The data are session 8's: every trip to the line for two free throws in the NBA from 2006-07 to
    2015-16, one row per trip, with the player, the season and whether each shot went in. The *gap*
    is the share of second shots made after a make minus the share made after a miss, in percentage
    points. Session 8 found that a player's own gap is usually a few points and very uncertain.
    This session asks whether any players have a real gap, which some coaches would call being
    streaky.
    """)
    return


@app.cell
def load_trips(course_parquet):
    trips = course_parquet("nba_free_throw_pairs.parquet")
    trips.head()
    return (trips,)


@app.cell
def define_tests(np, stats):
    def gap(first, second):
        """The gap for arrays of first-shot and second-shot results, in percentage points."""
        return 100 * (second[first].mean() - second[~first].mean())


    def shuffle_test(rows, shuffles=2000, seed=385):
        """The reading's shuffle test of the gap: the observed gap, the shuffled gaps, and the
        one-tailed and two-tailed p-values."""
        _first = rows["first_made"].to_numpy()
        _second = rows["second_made"].to_numpy()
        _observed = gap(_first, _second)
        _rng = np.random.default_rng(seed)
        _shuffled_first = _rng.permuted(np.tile(_first, (shuffles, 1)), axis=1)
        _made = _second[None, :]
        _shuffled = 100 * ((_made & _shuffled_first).sum(axis=1) / _shuffled_first.sum(axis=1)
                           - (_made & ~_shuffled_first).sum(axis=1) / (~_shuffled_first).sum(axis=1))
        return {"gap": _observed, "shuffled": _shuffled,
                "p one-tailed": (_shuffled >= _observed).mean(),
                "p two-tailed": (np.abs(_shuffled) >= abs(_observed)).mean()}


    def t_test(rows):
        """Welch's t-test of the second shot after a make against after a miss."""
        _second = rows["second_made"].to_numpy(dtype=float)
        _first = rows["first_made"].to_numpy()
        return stats.ttest_ind(_second[_first], _second[~_first], equal_var=False)

    return gap, shuffle_test, t_test


@app.cell(hide_code=True)
def shuffle_intro(mo):
    mo.md(r"""
    ---
    ## A shuffle test

    The reading's shuffle test starts from the claim to be tested against, the *null hypothesis*:
    here, that the first shot makes no difference to the second. If that were true, the first-shot
    results could be shuffled among a player's trips without changing anything that matters, so the
    test shuffles them many times, computes the gap after each shuffle, and asks how often a
    shuffled gap is at least as large as the real one. That share is the *p-value*: one-tailed if
    only larger gaps count, and two-tailed if gaps as far from zero in either direction count.

    Please choose a player and a number of shuffles.
    """)
    return


@app.cell
def shuffle_controls(mo, trips):
    _counts = trips.groupby("player")["first_made"].agg(trips="size",
                                                         missed=lambda _f: (~_f).sum())
    _regulars = sorted(_counts.index[(_counts["trips"] >= 500) & (_counts["missed"] >= 50)])
    # mo.ui.dropdown is a marimo function that makes a drop-down menu; its .value is the choice.
    player_pick = mo.ui.dropdown(options=_regulars, value="LeBron James", label="Player")
    # mo.ui.slider is a marimo function that makes a slider; its .value is the chosen setting.
    shuffle_count = mo.ui.slider(steps=[100, 500, 1000, 2000, 5000], value=2000,
                                 label="Shuffles", show_value=True)
    # mo.hstack is a marimo function that puts outputs side by side.
    mo.hstack([player_pick, shuffle_count], justify="start", gap=2)
    return player_pick, shuffle_count


@app.cell
def shuffle_view(mo, player_pick, plt, shuffle_count, shuffle_test, trips):
    player_rows = trips[trips["player"] == player_pick.value]
    _result = shuffle_test(player_rows, shuffles=shuffle_count.value)
    _fig, _ax = plt.subplots(figsize=(7, 2.8))
    _ax.hist(_result["shuffled"], bins=40, color="#9ca3af", label="shuffled gaps")
    _ax.axvline(_result["gap"], color="#c2410c", linewidth=2, label="the real gap")
    _ax.set_xlabel("Gap, points")
    _ax.set_yticks([])
    _ax.legend(frameon=False)
    _ax.spines[["top", "right", "left"]].set_visible(False)
    _fig.tight_layout()
    # mo.vstack is a marimo function that stacks outputs one above the other.
    mo.vstack([_fig, mo.md(
        f"The real gap is **{_result['gap']:.1f}** points. **{_result['p one-tailed']:.1%}** of "
        f"the shuffled gaps are at least that large, the one-tailed p-value, and "
        f"**{_result['p two-tailed']:.1%}** are at least that far from zero, the two-tailed one.")])
    return (player_rows,)


@app.cell(hide_code=True)
def shuffle_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the observed difference between two groups, shuffle the column
    that defines the groups 2,000 times, and report the one-tailed and two-tailed p-values. To use
    it on other data, you would change the rows and the two columns.
    """)
    return


@app.cell
def shuffle_code(np, trips):
    # Uses: import numpy as np
    _rows = trips[trips["player"] == "LeBron James"]
    _group = _rows["first_made"].to_numpy()
    _outcome = _rows["second_made"].to_numpy()

    def _difference(group):
        return 100 * (_outcome[group].mean() - _outcome[~group].mean())

    _observed = _difference(_group)
    _rng = np.random.default_rng(385)
    _shuffled = np.array([_difference(_rng.permutation(_group)) for _ in range(2000)])
    print(f"observed difference {_observed:.1f}")
    print(f"one-tailed p-value {(_shuffled >= _observed).mean():.3f}")
    print(f"two-tailed p-value {(np.abs(_shuffled) >= abs(_observed)).mean():.3f}")
    return


@app.cell(hide_code=True)
def t_intro(mo):
    mo.md(r"""
    ---
    ## The t-test

    The t-test asks the same question with a formula instead of shuffles. Its statistic is the
    difference between the two group means divided by its *standard error*, an estimate of how much
    that difference would vary from sample to sample, so *t* counts how many standard errors the
    difference is from zero. When the null hypothesis is true and the samples are not too small,
    *t* follows a known distribution, from which the p-value comes. Welch's version, used here,
    does not assume that the two groups have the same spread.

    The table gives both tests for the player you chose above.
    """)
    return


@app.cell
def t_view(pd, player_rows, shuffle_test, t_test):
    _shuffle = shuffle_test(player_rows)
    _t = t_test(player_rows)
    pd.DataFrame({"t-test": {"statistic": round(_t.statistic, 3),
                             "p two-tailed": round(_t.pvalue, 4)},
                  "shuffle test": {"statistic": round(_shuffle["gap"], 3),
                                   "p two-tailed": round(_shuffle["p two-tailed"], 4)}})
    return


@app.cell(hide_code=True)
def t_reading(mo):
    mo.md(r"""
    With several hundred trips after a miss, the two p-values are close, because the formula's
    assumptions hold well with samples this size. The shuffle test needs fewer assumptions and works
    for any statistic you can compute, and the t-test is faster and is what most software reports,
    so it is worth knowing that they answer the same question.
    """)
    return


@app.cell(hide_code=True)
def t_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we run Welch's t-test on one column for two groups with `stats.ttest_ind`
    and `equal_var=False`, and print the difference between the means, the statistic and the
    two-tailed p-value.
    """)
    return


@app.cell
def t_code(stats, trips):
    # Uses: from scipy import stats
    _rows = trips[trips["player"] == "LeBron James"]
    _after_make = _rows.loc[_rows["first_made"], "second_made"].astype(float)
    _after_miss = _rows.loc[~_rows["first_made"], "second_made"].astype(float)
    _result = stats.ttest_ind(_after_make, _after_miss, equal_var=False)
    print(f"difference {100 * (_after_make.mean() - _after_miss.mean()):.1f} points, "
          f"t = {_result.statistic:.2f}, p = {_result.pvalue:.3f}")
    return


@app.cell(hide_code=True)
def not_intro(mo):
    mo.md(r"""
    ---
    ## What a p-value does not tell you

    A p-value is the share of shuffled results at least as extreme as the real one, computed as if
    the null hypothesis were true. It is not the chance that the null hypothesis is true, and it is
    not a measure of how large the effect is. To see the second point, suppose a player kept the
    same shares of makes and misses but had taken more trips. Please move the slider to multiply the
    player's trips and watch the gap and the p-value.
    """)
    return


@app.cell
def scale_control(mo):
    trip_multiple = mo.ui.slider(steps=[1, 2, 5, 10, 20, 50], value=1,
                                 label="Trips, times the real number", show_value=True)
    trip_multiple
    return (trip_multiple,)


@app.cell
def scale_view(mo, pd, player_rows, t_test, trip_multiple):
    _scaled = pd.concat([player_rows] * trip_multiple.value, ignore_index=True)
    _t = t_test(_scaled)
    _gap = 100 * (_scaled.loc[_scaled["first_made"], "second_made"].mean()
                  - _scaled.loc[~_scaled["first_made"], "second_made"].mean())
    mo.hstack([
        # mo.stat is a marimo function that displays a single number with a label.
        mo.stat(value=f"{len(_scaled):,}", label="Trips"),
        mo.stat(value=f"{_gap:.2f}", label="Gap, points"),
        mo.stat(value=f"{_t.pvalue:.2g}", label="p-value, t-test"),
    ], justify="start", gap=2)
    return


@app.cell(hide_code=True)
def not_reading(mo):
    mo.md(r"""
    The gap does not change, and the p-value falls as the trips increase, so with enough data a gap
    too small to matter to anyone can have a tiny p-value, and with too little data a large gap can
    have a large one. A p-value says how surprising the data would be if there were no effect, which
    depends on the size of the effect and the amount of data together. A report should therefore
    give the effect and its interval, as in session 8, and the p-value beside them, not instead of
    them.
    """)
    return


@app.cell(hide_code=True)
def many_intro(mo):
    mo.md(r"""
    ---
    ## Many tests at once

    The tests above are for one player chosen in advance. Testing every regular player, 180 of
    them, is a different procedure: if no player had a real gap, each test would still pass at 5%
    one time in twenty, so about nine players would pass by chance alone. Below, we run the t-test
    for every regular player, then run it again after shuffling each player's first-shot results,
    so that no player can have a real gap. Please move the slider to change the cutoff.
    """)
    return


@app.cell
def all_players(np, pd, t_test, trips):
    _rng = np.random.default_rng(385)
    _records = []
    for _player, _rows in trips.groupby("player"):
        _missed = int((~_rows["first_made"]).sum())
        if len(_rows) < 500 or _missed < 50:
            continue
        _shuffled = _rows.assign(first_made=_rng.permutation(_rows["first_made"].to_numpy()))
        _records.append({
            "player": _player, "trips": len(_rows),
            "gap": 100 * (_rows.loc[_rows["first_made"], "second_made"].mean()
                          - _rows.loc[~_rows["first_made"], "second_made"].mean()),
            "p": t_test(_rows).pvalue, "p, shuffled data": t_test(_shuffled).pvalue,
        })
    player_tests = pd.DataFrame(_records).set_index("player")
    return (player_tests,)


@app.cell
def cutoff_control(mo):
    cutoff = mo.ui.slider(steps=[0.001, 0.005, 0.01, 0.05, 0.1], value=0.05,
                          label="Cutoff for passing", show_value=True)
    cutoff
    return (cutoff,)


@app.cell
def many_view(cutoff, mo, np, player_tests, plt):
    _fig, (_left, _right) = plt.subplots(1, 2, figsize=(10, 3), sharey=True)
    for _ax, _column, _title in ((_left, "p", "Real data"),
                                 (_right, "p, shuffled data", "Shuffled: no real gaps")):
        _ax.hist(player_tests[_column], bins=np.linspace(0, 1, 21), color="#9ca3af")
        _ax.axvline(cutoff.value, color="#c2410c", linewidth=2)
        _ax.set_title(_title, fontsize=10)
        _ax.set_xlabel("p-value")
        _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _n = len(player_tests)
    mo.vstack([_fig, mo.md(
        f"At a cutoff of {cutoff.value}, **{int((player_tests['p'] < cutoff.value).sum())}** of "
        f"the {_n} players pass on the real data and "
        f"**{int((player_tests['p, shuffled data'] < cutoff.value).sum())}** on the shuffled data, "
        f"against about **{cutoff.value * _n:.0f}** expected by chance. The Bonferroni cutoff for "
        f"{_n} tests is 0.05/{_n}, or **{0.05 / _n:.5f}**.")])
    return


@app.cell(hide_code=True)
def many_reading(mo):
    mo.md(r"""
    When there are no real gaps, the p-values spread evenly from 0 to 1, and the share below any
    cutoff is about the cutoff itself. The real data have more small p-values than that, which says
    that some players probably do have a gap, but it cannot say which, because the players who pass
    are a mixture of those with real gaps and those who were lucky. Two remedies help: a stricter
    cutoff for each test, such as Bonferroni's, and checking the players who pass on data that
    played no part in choosing them, as session 8 did with the seasons.
    """)
    return


@app.cell(hide_code=True)
def many_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we run one test for each group, count how many pass at 5%, compare the
    count with the number expected by chance, and apply the Bonferroni cutoff.
    """)
    return


@app.cell
def many_code(pd, stats, trips):
    # Uses: import pandas as pd
    #       from scipy import stats
    _p = {}
    for _player, _rows in trips.groupby("player"):
        if len(_rows) < 500 or (~_rows["first_made"]).sum() < 50:
            continue
        _second = _rows["second_made"].astype(float)
        _p[_player] = stats.ttest_ind(_second[_rows["first_made"]], _second[~_rows["first_made"]],
                                      equal_var=False).pvalue
    _p = pd.Series(_p)
    print(f"{len(_p)} tests: {(_p < 0.05).sum()} pass at 5%, about {0.05 * len(_p):.0f} "
          f"expected by chance; {(_p < 0.05 / len(_p)).sum()} pass the Bonferroni cutoff")
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    A broadcaster wants to name the streaky free-throw shooters, the players for whom a make on the
    first shot really does raise the chance of making the second.

    > **Use these data to say whether some players are streaky at the line, and whether you can say
    > which ones.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. The tests for every regular player at the cutoff you chose, with the number that pass and
       the number expected by chance.
    2. A check of the players who pass on data that played no part in choosing them: the seasons
       you did not test, in Step 3.
    3. One limitation: something these tests cannot tell the broadcaster.

    Then compare your results with your teammates', who chose different cutoffs and halves, and
    say what their results showed that yours did not, and whether that changes your answer.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each
    prompt, in your own words and with the numbers from your own runs. Each of you should then
    upload your own copy of this notebook to *AE 7* on Canvas, by 23:59 on Thursday.

    | Part of your answer | Points |
    |---|---:|
    | Your answer: the tests, the check on other seasons, and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop rather than watching one
    screen, and choose a different cutoff or half of the seasons from your teammates, then compare
    what you find. Your team may agree on an answer, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholders in Step 1, run
    the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_choose():
    # Step 1: choose a cutoff for passing, such as 0.05 or 0.01, and the half of the seasons to
    # test players on: "even" for seasons starting in an even year, "odd" for the others. The
    # other half will be used to check the players who pass.
    answer_cutoff = "SOME_NUMBER"
    answer_half = "SOME_HALF"
    return answer_cutoff, answer_half


@app.cell
def step2_tests(answer_cutoff, answer_half, mo, pd, t_test, trips):
    # Step 2: the t-test for every player with at least 250 trips and 25 missed first shots in
    # each half, on the half you chose.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder values.
    mo.stop(answer_cutoff == "SOME_NUMBER" or answer_half not in ("even", "odd"),
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md('Replace the placeholders in Step 1 with a number and "even" or "odd".')
            .callout(kind="info"))
    _half = (trips["season"].str[:4].astype(int) % 2).map({0: "even", 1: "odd"})
    _records = {}
    for (_player, _h), _rows in trips.groupby([trips["player"], _half]):
        if len(_rows) < 250 or (~_rows["first_made"]).sum() < 25:
            continue
        _records.setdefault(_player, {})[f"{_h} gap"] = 100 * (
            _rows.loc[_rows["first_made"], "second_made"].mean()
            - _rows.loc[~_rows["first_made"], "second_made"].mean())
        if _h == answer_half:
            _records[_player]["p"] = t_test(_rows).pvalue
    answer_tests = pd.DataFrame.from_dict(_records, orient="index").dropna()
    answer_tests["passes"] = answer_tests["p"] < answer_cutoff
    print(f"{len(answer_tests)} players; {int(answer_tests['passes'].sum())} pass at "
          f"{answer_cutoff} on the {answer_half} seasons, about "
          f"{answer_cutoff * len(answer_tests):.0f} expected by chance")
    answer_tests.sort_values("p").head(15).round(3)
    return (answer_tests,)


@app.cell
def step3_check(answer_half, answer_tests):
    # Step 3: the mean gap of the players who passed and of everyone else, in the half you tested
    # and in the other half.
    _other = "odd" if answer_half == "even" else "even"
    answer_tests.groupby("passes")[[f"{answer_half} gap", f"{_other} gap"]].agg(
        ["count", "mean"]).round(2)
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L09_hypothesis_testing_i.py` to *AE 7* on Canvas by 23:59 on Thursday. We will
    cross-reference your claims about evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_tests(mo):
    mo.md(r"""
    **The players who pass at your cutoff, and how that number compares with chance**
    """)
    return


@app.cell
def step4_answer_tests(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_check(mo):
    mo.md(r"""
    **What the other half of the seasons showed about those players**
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
