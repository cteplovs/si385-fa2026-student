import marimo

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    import pandas as pd
    import matplotlib.pyplot as plt

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

    return course_parquet, mo, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385 — Data Exploration

    ## Session 4: Anscombe's quartet, and the limits of summary statistics

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, September 14, 2026

    **Reading due today:** Healy, *Data Visualization*, ch. 1, the two sections
    *Why Look at Data?* and *What Makes Bad Figures Bad?*, at
    <https://socviz.co/01-look-at-data.html>

    ---

    ### Today you will be able to

    - Say what a pooled summary is a summary *of*, and name the question it answers
      instead of the one that was asked
    - Separate the three kinds of failure Healy distinguishes (taste, data, perception)
      and say which one a given figure is guilty of
    - Rule on whether a true sentence is an honest description, and defend the ruling to
      a room that disagrees
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 — RAT 2, and appeals

    Canvas gave you your score and your own answers on Sunday night, and it did not give
    you the key.  Same arrangement as last week and for the same reason.

    We will re-poll the items that split the room rather than my talking through all five.
    Vote, argue, vote again.

    Appeals work as they did in session 3: one per team, in writing, before you leave,
    citing the section and what it actually says.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:15 — Application exercise 2

    ## A sentence that is true

    Every entry in a Summer Olympic Games from 1896 to 2016 is in this file: 222,552 of
    them, one row per athlete per event.  Where somebody recorded a height, it is in
    `height_cm`.  Where nobody did, it is missing, and it has been left missing.

    A wire service has the file and is about to run this sentence:

    > **Olympic athletes are no taller today than they were a century ago.**

    The number behind it is correct.  Here it is.
    """)
    return


@app.cell
def _(course_parquet):
    olympics = course_parquet("olympic_heights.parquet")
    olympics.head()
    return (olympics,)


@app.cell
def _(olympics, plt):
    _measured = olympics.dropna(subset=["height_cm"]).copy()
    _measured["decade"] = (_measured["year"] // 10) * 10
    _pooled = _measured.groupby("decade")["height_cm"].mean()

    _fig, _ax = plt.subplots(figsize=(9, 4))
    _ax.plot(_pooled.index, _pooled.values, marker="o", color="#4c72b0", linewidth=2)
    _ax.set_xlabel("Decade")
    _ax.set_ylabel("Mean height, cm")
    _ax.set_title("Mean height of Summer Olympic athletes")
    _ax.set_ylim(160, 190)
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Flat.  From the 1920s to the 2010s the pooled mean moves from 175.4 cm to 176.1 cm.
    Seven millimetres a century, which is nothing.

    ### The same data, grouped

    Please change the grouping and watch what the line does.
    """)
    return


@app.cell
def _(mo):
    split_by = mo.ui.dropdown(
        options=["Everyone pooled", "By sex", "By sex, share of the field"],
        value="Everyone pooled",
        label="Group the athletes by:",
    )
    return (split_by,)


@app.cell
def _(mo, olympics, plt, split_by):
    _m = olympics.dropna(subset=["height_cm"]).copy()
    _m["decade"] = (_m["year"] // 10) * 10

    _fig2, _ax2 = plt.subplots(figsize=(9, 4))

    if split_by.value == "Everyone pooled":
        _p = _m.groupby("decade")["height_cm"].mean()
        _ax2.plot(_p.index, _p.values, marker="o", color="#4c72b0",
                  linewidth=2, label="everyone")
        _ax2.set_ylabel("Mean height, cm")
        _ax2.set_ylim(160, 190)
    elif split_by.value == "By sex":
        for _s, _colour, _name in (("M", "#4c72b0", "men"), ("F", "#c44e52", "women")):
            _p = _m[_m["sex"] == _s].groupby("decade")["height_cm"].mean()
            _ax2.plot(_p.index, _p.values, marker="o", color=_colour,
                      linewidth=2, label=_name)
        _ax2.set_ylabel("Mean height, cm")
        _ax2.set_ylim(160, 190)
    else:
        _share = _m.assign(is_f=_m["sex"].eq("F")).groupby("decade")["is_f"].mean() * 100
        _ax2.plot(_share.index, _share.values, marker="o", color="#c44e52",
                  linewidth=2, label="women, % of measured field")
        _ax2.set_ylabel("Women as % of the measured field")
        _ax2.set_ylim(0, 60)

    _ax2.set_xlabel("Decade")
    _ax2.legend()
    mo.vstack([split_by, _fig2])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Both lines climb.  Men gain 5.7 cm between the 1920s and the 2010s, women 3.9 cm.
    The pooled average sits still because the field it averages over changed: women were
    one in twenty of the measured athletes in the 1920s and are nearly half of them now.

    Neither line is wrong.  They answer different questions.
    """)
    return


@app.cell
def _(olympics, pd):
    _o = olympics.copy()
    _o["decade"] = (_o["year"] // 10) * 10
    _cov = _o.groupby("decade").agg(
        entries=("height_cm", "size"),
        with_height=("height_cm", "count"),
    )
    _cov["recorded_pct"] = (_cov["with_height"] / _cov["entries"] * 100).round(1)
    coverage = _cov
    coverage
    return (coverage,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### One more column before you decide

    That is how much of each decade actually carries a height.  Seventeen per cent of the
    1920s field, ninety-nine per cent of the 2010s.  Nothing in the file says who the
    measured fifth of 1924 were, or why they and not the rest.

    ---

    ## Part 1 — eight minutes, on your own, in silence

    > **The sentence is true.  Should it run?**

    Take a position and write down the one sentence you would say to the editor.  Do not
    talk to your team yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:23 — With your team

    Argue to a decision.  One choice, and one justification, both submitted before the
    reveal.

    > **A wire service is about to run the sentence "Olympic athletes are no taller today
    > than they were a century ago." The number behind it is correct. Should it run?**
    >
    > **A.** Yes.  The pooled mean is the summary of the population that competed, and it
    > is flat.  The sentence is true and the reader is entitled to it.
    >
    > **B.** No.  Men gained 5.7 cm and women 3.9 cm.  The flat average is a consequence
    > of who was admitted to the Games, and the sentence tells the reader the opposite of
    > what happened to athletes.
    >
    > **C.** No, and conditioning does not rescue it.  Height is missing for over four
    > fifths of the 1920s field, so there is no baseline anyone can defend, whatever you
    > break the data down by.
    >
    > **D.** Yes, if the composition change runs in the same sentence.  That women went
    > from one in twenty to nearly half *is* the century's finding, and a sex-stratified
    > chart that leaves it out is its own kind of distortion.

    ### The choice

    One of A, B, C, D in Sli.do.  Every team commits before anybody sees the histogram.
    Ungraded.

    ### The justification

    Three or four sentences, submitted at the same moment, and the only part that is
    graded.

    Name the reader you have in mind and what they would take away from those nine words.
    Then name the one fact that, if this file carried it, would move you off your answer.

    "Pooling hides subgroup differences" restates Simpson's paradox and stops there.  The
    version that does the work sounds more like: *we would need to know who got measured
    in 1924.  If it was only the medal favourites, the 1920s mean is a ceiling, and every
    comparison to it understates the gain.*

    The data is in front of you and you may go further into it than the cells above.  The
    figures that would settle a disagreement between A and B are two lines of pandas, and
    finding them is a reasonable use of the next twenty minutes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:50 — Report

    All thirty-five teams reveal at once.  Then four or five defend.

    Please do not summarise your justification when you defend.  I already have it.  What
    the room needs from you is an answer to one question: what would have to be true for
    the option next to yours to be the right call?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 1:15 — Consolidation

    Put Healy's three kinds of failure against what just happened.  Taste was not the
    problem; the chart was clean.  Perception was not the problem either; the axis covered
    the full range and the line was drawn straight.  If you called anything here a failure,
    it was in the measure, which is what went wrong with the democracy figure in the
    reading.  That chart was elegant, and it showed the share of people answering ten out
    of ten rather than the average score.

    So a figure can be well made, honestly drawn, correctly computed, and still answer a
    question nobody asked.

    ### Before September 16

    - **Reading:** McKinney ch. 7 (review), and Segel & Heer
    - **RAT 3** opens Monday September 14 at 09:50 and closes Tuesday September 15 at 20:59
    """)
    return


if __name__ == "__main__":
    app.run()
