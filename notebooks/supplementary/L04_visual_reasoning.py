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

    ## Session 4: Anscombe's quartet, and the limits of summary statistics

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, September 14, 2026

    The reading for this session is Healy, *Data Visualization*, chapter 1, the sections *Why Look
    at Data?* and *What Makes Bad Figures Bad?*, free at <https://socviz.co/01-look-at-data.html>.

    ---

    ### Today you will be able to

    - Explain why data with the same summary statistics can show different patterns, and why a
      plot is evidence that a summary is not
    - Show how a pooled average can change over time while every group's average changes
      differently, because the mix of groups changes
    - Check how much of each period a plot is based on before reading a trend from it
    - Say how choices such as the range of an axis change what a reader takes from a figure

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Data | 5 |
    | Anscombe's quartet | 10 |
    | A trend, pooled and by group | 15 |
    | What the plot is based on | 10 |
    | Today's question, in teams | 25 |
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

    Each technique ends with a section headed *The code on its own*. The dropdowns, switches and
    plots above it call code written for this notebook, which you will not have when you work on
    your own data. The code in those sections uses only pandas, NumPy and matplotlib, starts from a
    data frame, and does the computation without any controls, so that you can copy it into your
    project or another notebook. Each code cell starts with a comment listing the imports it uses,
    and its variable names start with `_`, which keeps them local to the cell.
    """)
    return


@app.cell(hide_code=True)
def anscombe_intro(mo):
    mo.md(r"""
    ---
    ## Anscombe's quartet

    In 1973 the statistician Francis Anscombe published four small datasets of eleven points each,
    which the reading uses to open its case for looking at data. The four have the same mean and
    variance of *x*, nearly the same mean and variance of *y*, the same correlation and the same
    fitted line, to two decimal places. Please choose a dataset and compare the table with the
    plot.
    """)
    return


@app.cell
def anscombe_data(pd):
    _x = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
    anscombe = pd.concat([
        pd.DataFrame({"dataset": "I", "x": _x,
                      "y": [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]}),
        pd.DataFrame({"dataset": "II", "x": _x,
                      "y": [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]}),
        pd.DataFrame({"dataset": "III", "x": _x,
                      "y": [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73]}),
        pd.DataFrame({"dataset": "IV", "x": [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],
                      "y": [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]}),
    ], ignore_index=True)
    return (anscombe,)


@app.cell
def anscombe_control(mo):
    # mo.ui.dropdown is a marimo function that makes a drop-down menu; its .value is the choice.
    dataset_pick = mo.ui.dropdown(options=["I", "II", "III", "IV"], value="I", label="Dataset")
    dataset_pick
    return (dataset_pick,)


@app.cell
def anscombe_view(anscombe, dataset_pick, mo, np, pd, plt):
    _summary = anscombe.groupby("dataset").apply(
        lambda _d: np.round([_d["x"].mean(), _d["x"].var(), _d["y"].mean(), _d["y"].var(),
                             _d["x"].corr(_d["y"]), *np.polyfit(_d["x"], _d["y"], 1)], 2),
        include_groups=False)
    _table = pd.DataFrame(np.vstack(_summary.to_numpy()), index=_summary.index,
                          columns=["mean x", "var x", "mean y", "var y", "r", "slope",
                                   "intercept"])
    _rows = anscombe[anscombe["dataset"] == dataset_pick.value]
    _slope, _intercept = np.polyfit(_rows["x"], _rows["y"], 1)
    _fig, _ax = plt.subplots(figsize=(5.5, 4))
    _ax.scatter(_rows["x"], _rows["y"], color="#1f4e79", zorder=3)
    _ax.plot([3, 20], [_intercept + 3 * _slope, _intercept + 20 * _slope], color="#c2410c")
    _ax.set_xlim(2, 21)
    _ax.set_ylim(2, 14)
    _ax.set_title(f"Dataset {dataset_pick.value}")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    # mo.hstack is a marimo function that puts outputs side by side.
    mo.hstack([_table, _fig], justify="start", align="center", gap=2)
    return


@app.cell(hide_code=True)
def anscombe_reading(mo):
    mo.md(r"""
    Dataset I is roughly what a reader imagines from the table: a linear trend with some noise.
    Dataset II is a smooth curve, for which a straight line is the wrong description. In dataset
    III, ten points lie almost exactly on a line and one point pulls the fitted line away from
    them. Dataset IV has no relationship at all between *x* and *y* except for one point, which
    produces the whole correlation by itself. The summary statistics are correct for every
    dataset, and they cannot tell these four situations apart, which is why the reading treats a
    plot as evidence rather than decoration.
    """)
    return


@app.cell(hide_code=True)
def anscombe_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the same summary statistics for each group of a data frame and
    then draw one scatter plot per group in a grid with shared axes, which is how you would check
    whether groups with similar summaries look alike.
    """)
    return


@app.cell
def anscombe_code(anscombe, np, plt):
    # Uses: import matplotlib.pyplot as plt
    #       import numpy as np
    print(anscombe.groupby("dataset").agg(mean_x=("x", "mean"), mean_y=("y", "mean"),
                                          var_y=("y", "var")).round(2))
    print(anscombe.groupby("dataset").apply(lambda _d: round(_d["x"].corr(_d["y"]), 2),
                                            include_groups=False).rename("r"))
    _fig, _axes = plt.subplots(2, 2, figsize=(7, 5.5), sharex=True, sharey=True)
    for _ax, (_name, _rows) in zip(_axes.flat, anscombe.groupby("dataset")):
        _ax.scatter(_rows["x"], _rows["y"])
        _slope, _intercept = np.polyfit(_rows["x"], _rows["y"], 1)
        _ax.plot([4, 19], [_intercept + 4 * _slope, _intercept + 19 * _slope])
        _ax.set_title(_name)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## Data

    The rest of the session uses every entry in the Summer Olympic Games from 1896 to 2016, 222,552
    rows with one per athlete per event, so an athlete who entered three events appears three
    times.

    | Column | Description |
    |---|---|
    | `year` | The year of the Games |
    | `sex` | M or F, as the records give it |
    | `sport`, `event` | The sport, and the event within it |
    | `height_cm`, `weight_kg`, `age` | The athlete's height, weight and age, where recorded |
    | `noc` | The athlete's national Olympic committee, as a three-letter code |

    After reading the file, we add the decade of each Games.
    """)
    return


@app.cell
def load_olympics(course_parquet):
    olympics = course_parquet("olympic_heights.parquet")
    olympics["decade"] = (olympics["year"] // 10) * 10
    olympics.head()
    return (olympics,)


@app.cell(hide_code=True)
def trend_intro(mo):
    mo.md(r"""
    ---
    ## A trend, pooled and by group

    Consider the mean height of the athletes in each decade. Please choose a view: everyone
    pooled, men and women separately, or the share of the measured athletes who are women.
    """)
    return


@app.cell
def trend_controls(mo):
    view_pick = mo.ui.dropdown(options=["Everyone pooled", "Men and women separately",
                                        "Women's share of the measured athletes"],
                               value="Everyone pooled", label="View")
    # mo.ui.switch is a marimo function that makes an on-off switch.
    axis_from_zero = mo.ui.switch(value=False, label="Start the height axis at zero")
    mo.hstack([view_pick, axis_from_zero], justify="start", gap=3)
    return axis_from_zero, view_pick


@app.cell
def trend_plot(axis_from_zero, olympics, plt, view_pick):
    _measured = olympics.dropna(subset=["height_cm"])
    _fig, _ax = plt.subplots(figsize=(8, 3.8))
    if view_pick.value == "Everyone pooled":
        _line = _measured.groupby("decade")["height_cm"].mean()
        _ax.plot(_line.index, _line.to_numpy(), marker="o", color="#111827", label="everyone")
    elif view_pick.value == "Men and women separately":
        for _sex, _colour, _label in (("M", "#1f4e79", "men"), ("F", "#c2410c", "women")):
            _line = _measured[_measured["sex"] == _sex].groupby("decade")["height_cm"].mean()
            _ax.plot(_line.index, _line.to_numpy(), marker="o", color=_colour, label=_label)
    else:
        _share = 100 * _measured.assign(_f=_measured["sex"] == "F").groupby("decade")["_f"].mean()
        _ax.plot(_share.index, _share.to_numpy(), marker="o", color="#c2410c",
                 label="women, % of measured athletes")
    if view_pick.value != "Women's share of the measured athletes":
        _ax.set_ylabel("Mean height, cm")
        _ax.set_ylim((0, 190) if axis_from_zero.value else (160, 185))
    else:
        _ax.set_ylabel("% of measured athletes")
        _ax.set_ylim(0, 60)
    _ax.set_xlabel("Decade")
    _ax.legend(frameon=False)
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def trend_reading(mo, olympics):
    _m = olympics.dropna(subset=["height_cm"])
    _mean = lambda _rows, _d: _rows.loc[_rows["decade"] == _d, "height_cm"].mean()
    _men, _women = _m[_m["sex"] == "M"], _m[_m["sex"] == "F"]
    mo.md(f"""
    From the 1960s to the 2010s, the pooled mean rose by **{_mean(_m, 2010) - _mean(_m, 1960):.1f}**
    cm, while the men's mean rose by **{_mean(_men, 2010) - _mean(_men, 1960):.1f}** cm and the
    women's by **{_mean(_women, 2010) - _mean(_women, 1960):.1f}** cm. The pooled line rose less
    than either group's because the share of women among the measured athletes more than doubled
    over the same years, and women are shorter on average, so the changing mix pulled the pooled
    mean down while each group grew taller. A pooled average answers a question about everyone
    measured in each decade, and the group lines answer a question about athletes like each other,
    which is usually the question a reader has in mind.

    The switch shows a second choice that changes what a reader takes from the figure. An axis from
    160 to 185 cm makes a change of a few centimetres look large, and an axis from zero makes it
    look negligible. The reading's point is that neither is wrong in itself: the range should be
    chosen for the comparison the figure is meant to show, and a reader should be able to see what
    it is.
    """)
    return


@app.cell(hide_code=True)
def trend_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we plot the mean of one column for each decade, first for everyone together
    and then for each value of a grouping column, on the same axes. To use it on other data, you
    would change the time column, the value and the grouping column.
    """)
    return


@app.cell
def trend_code(olympics, plt):
    # Uses: import matplotlib.pyplot as plt
    _measured = olympics.dropna(subset=["height_cm"])
    _fig, _ax = plt.subplots(figsize=(8, 3.5))
    _pooled = _measured.groupby("decade")["height_cm"].mean()
    _ax.plot(_pooled.index, _pooled.to_numpy(), marker="o", color="black", label="everyone")
    for _group, _rows in _measured.groupby("sex"):
        _line = _rows.groupby("decade")["height_cm"].mean()
        _ax.plot(_line.index, _line.to_numpy(), marker="o", label=_group)
    _ax.set_ylabel("mean height_cm")
    _ax.legend()
    _fig
    return


@app.cell(hide_code=True)
def coverage_intro(mo):
    mo.md(r"""
    ---
    ## What the plot is based on

    A mean for a decade is only as good as the heights behind it. The table below gives, for each
    decade, the number of entries, the number with a recorded height, and the share recorded.
    Please read it before you read anything into the early decades of the plot above.
    """)
    return


@app.cell
def coverage_table(olympics):
    coverage = olympics.groupby("decade").agg(entries=("height_cm", "size"),
                                              with_height=("height_cm", "count"))
    coverage["recorded_pct"] = (100 * coverage["with_height"] / coverage["entries"]).round(1)
    coverage
    return (coverage,)


@app.cell(hide_code=True)
def coverage_reading(coverage, mo):
    _early = coverage.loc[coverage.index < 1960, "recorded_pct"].max()
    mo.md(f"""
    Before the 1960s, at most **{_early:.0f}%** of the entries in any decade have a recorded height,
    and the athletes whose heights were recorded need not be typical of the rest; they may be, for
    example, the better-known athletes or those from countries that kept records. The
    early part of every line above therefore describes the measured athletes rather than the Games,
    and a trend that starts in 1896 is based on a different kind of evidence from one that starts in
    1960. The plot does not show this unless you add it.
    """)
    return


@app.cell(hide_code=True)
def coverage_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we count the rows and the recorded values for each period and compute the
    share recorded, with `size`, which counts every row, and `count`, which leaves out missing
    values.
    """)
    return


@app.cell
def coverage_code(olympics):
    _table = olympics.groupby("decade").agg(rows=("height_cm", "size"),
                                            recorded=("height_cm", "count"))
    _table.assign(recorded_pct=(100 * _table["recorded"] / _table["rows"]).round(1))
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    A sports writer wants to say how much taller Olympic athletes have become, with a figure to go
    with the claim.

    > **Use these data to say how much taller Summer Olympic athletes have become, and describe the
    > figure that shows it honestly.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. The mean height by decade for the sport you chose, for men and women separately, with the
       change you would report and the decades it covers.
    2. The share of heights recorded in those decades, to say where the trend is well supported.
    3. One limitation: something about these data that the figure cannot show.

    Then compare your results with your teammates', who chose different sports, and say what
    their results showed that yours did not, and whether that changes your answer.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each
    prompt, in your own words and with the numbers from your own runs. Each of you should then
    upload your own copy of this notebook to *AE 2* on Canvas, by 23:59 on Tuesday.

    | Part of your answer | Points |
    |---|---:|
    | Your answer: the change, where it is well supported, the figure, and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop rather than watching one
    screen, and choose a different sport from your teammates, then compare what you find. Your
    team may agree on an answer, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholder in Step 1, run
    the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_choose(olympics):
    # Step 1: choose a sport, different from the one your teammates choose. The list below gives
    # the sports with the most entries; any value of olympics["sport"] will work.
    print(olympics["sport"].value_counts().head(15).index.tolist())
    answer_sport = "SOME_SPORT"
    return (answer_sport,)


@app.cell
def step2_table(answer_sport, mo, olympics, pd):
    # Step 2: the mean height, the number of heights and the share recorded, by decade and sex.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder value.
    mo.stop(answer_sport == "SOME_SPORT",
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md("Replace the placeholder in Step 1 with a sport.").callout(kind="info"))
    answer_rows = olympics[olympics["sport"] == answer_sport]
    _grouped = answer_rows.groupby(["decade", "sex"])["height_cm"]
    pd.DataFrame({"mean_height": _grouped.mean().round(1), "heights": _grouped.count(),
                  "recorded_pct": (100 * _grouped.count() / _grouped.size()).round(1)}).unstack()
    return (answer_rows,)


@app.cell
def step3_plot(answer_rows, answer_sport, plt):
    # Step 3: the mean height by decade for men and women, with the decades in which fewer than
    # half of the heights were recorded shaded. Change the axis range if your sport needs it.
    _fig, _ax = plt.subplots(figsize=(8, 3.8))
    _recorded = answer_rows.groupby("decade")["height_cm"].apply(lambda _v: _v.notna().mean())
    for _decade in _recorded.index[_recorded < 0.5]:
        _ax.axvspan(_decade - 5, _decade + 5, color="#e5e7eb")
    for _sex, _colour in (("M", "#1f4e79"), ("F", "#c2410c")):
        _line = answer_rows[answer_rows["sex"] == _sex].groupby("decade")["height_cm"].mean()
        _ax.plot(_line.index, _line.to_numpy(), marker="o", color=_colour, label=_sex)
    _ax.set_title(f"{answer_sport}: mean height by decade; shaded decades have under half "
                  "of heights recorded", fontsize=10)
    _ax.set_ylabel("Mean height, cm")
    _ax.legend(frameon=False)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L04_visual_reasoning.py` to *AE 2* on Canvas by 23:59 on Tuesday. We will cross-reference your
    claims about evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_change(mo):
    mo.md(r"""
    **How much taller athletes in your sport have become, for men and women, and over which decades**
    """)
    return


@app.cell
def step4_answer_change(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_figure(mo):
    mo.md(r"""
    **The figure you would publish with the claim, and the choices you made in it**
    """)
    return


@app.cell
def step4_answer_figure(mo):
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
