# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.24.0",
#     "pandas==3.0.5",
#     "numpy==2.4.6",
#     "matplotlib==3.11.1",
# ]
# ///
#
# Dependencies are declared here as well as in pyproject.toml, so this file also
# runs on its own, outside the course folder:
#
#     uvx marimo edit --sandbox <this file>
#
# `uv run marimo edit --no-sandbox <this file>` from inside the course folder
# remains the documented way to work. The --no-sandbox flag matters: marimo sees
# this header and, in an interactive terminal, stops to ask whether to build an
# isolated environment from it, which is not a question to put to 140 students on
# lecture-hall wifi. The flag answers it in advance. The sandbox line above is the
# fallback for a file that has been moved, renamed, or opened months later.
#
# Versions are pinned EXACTLY to uv.lock on purpose: marimo rewrites loose
# specifiers in place on the first sandbox run, and exact pins make that a no-op
# so the file does not mutate under whoever opens it first. If you change
# pyproject.toml, re-pin these to match.

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385 — Data Exploration

    ## Session 1: What we're doing here

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, August 31, 2026
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Overview

    | | |
    |---|---|
    | 0:00 | In a nutshell |
    | 0:10 | A dataset that lies to you |
    | 0:30 | How this course runs, and why it isn't a lecture |
    | 0:50 | Diagnostic — no grade, no stakes |
    | 1:05 | Teams and seats |
    | 1:15 | What to do before Wednesday |

    No reading was due today.  Every session after this one has one, and the schedule
    on Canvas lists them all.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 1. In a nutshell...

    You spent SI 345 learning how to get data into a shape you could work with.  This
    course is about what comes next, which is deciding what any of it actually means.

    That turns out to be where analysis usually goes wrong.  It is rarely the join or
    the parser that does the damage; it is the moment somebody looks at a number and
    decides to believe it.  Most of what we do this term is a version of the same
    question:

    > *Is this pattern real, and what am I entitled to conclude from it?*
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 2. Datasets that lie to you

    Consider the following summary statistics of four datasets:
    """)
    return


@app.cell
def _():
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    anscombe = pd.DataFrame(
        {
            "set": ["I"] * 11 + ["II"] * 11 + ["III"] * 11 + ["IV"] * 11,
            "x": [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5] * 3
            + [8, 8, 8, 8, 8, 8, 8, 19, 8, 8, 8],
            "y": [
                8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68,
                9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74,
                7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73,
                6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89,
            ],
        }
    )
    return anscombe, plt


@app.cell
def _(anscombe):
    summary = anscombe.groupby("set").agg(
        mean_x=("x", "mean"),
        mean_y=("y", "mean"),
        std_x=("x", "std"),
        std_y=("y", "std"),
    ).round(2)

    correlations = anscombe.groupby("set")[["x", "y"]].corr().iloc[0::2, 1].round(2)
    summary["corr"] = correlations.values
    summary
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Identical to two decimal places: the same means, the same standard deviations, the
    same correlation, and a regression fitted to any one of them gives you the same
    line as the other three.

    Before you scroll any further, please write down what you think these four datasets
    look like.  I mean actually write it, on paper.  This matters more than it probably
    seems to, because the gap between what you predicted and what you are about to see
    is the thing that makes it stick, and you lose most of that if you just keep
    reading.
    """)
    return


@app.cell(hide_code=True)
def _(anscombe, mo, plt):
    _fig, _axes = plt.subplots(1, 4, figsize=(14, 3.2), sharex=True, sharey=True)
    for _ax, _name in zip(_axes, ["I", "II", "III", "IV"]):
        _subset = anscombe[anscombe["set"] == _name]
        _ax.scatter(_subset["x"], _subset["y"], s=45, color="#00274C")
        _ax.set_title(f"Set {_name}")
        _ax.set_xlabel("x")
    _axes[0].set_ylabel("y")
    plt.tight_layout()
    mo.mpl.interactive(_fig)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    One of them is a linear relationship, one is a curve, one is a clean line with a
    single contaminating point sitting off it, and one is a vertical stack in which a
    lone outlier is doing all of the work.  Every summary statistic you have is blind to
    the difference between them.

    This is more or less the whole course.  I am not making the point that you should
    always plot your data, because you already know that and knowing it does not seem to
    help anybody very much.  The point is that summary statistics lose information in
    ways you cannot predict from the summary itself, which means you have to go looking,
    and knowing where to look is a skill you build by making mistakes in front of people
    who will argue with you about them.

    Which is a reasonable moment to talk about how the course runs.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 3. This is not a lecture course

    Here is the situation, stated honestly.  There are about 140 of us, the seats are
    bolted to the floor, and it is 8:30 in the morning.  If I stand at the front and
    talk for eighty minutes twice a week, some of you will learn some of it and the rest
    of you will take notes you never look at again.

    So we are going to do something else instead.  It is called **Team-Based Learning**,
    and it was designed for rooms very much like this one.

    ### What happens most days

    Before class, on Canvas, there is a five-question quiz on the reading.  Five
    minutes, closed book, due at 20:59 the night before.  You prepare on your own time,
    and in exchange we spend the eighty minutes on the part that is actually
    interesting.

    | Time | What |
    |---|---|
    | 0:00–0:15 | I teach into whatever the quiz says the room got wrong, and mostly only that |
    | 0:15–0:23 | **Application exercise**, silent, while you work out what *you* think |
    | 0:23–0:50 | Your team argues, and then commits to an answer |
    | 0:50–1:15 | **Every team reveals at once.** A few get called on to defend |
    | 1:15–1:20 | We consolidate, and I live-code whatever broke |

    ### Three things people tend to find surprising

    **You will be in the same team of four all term.**  You pick it on Wednesday and
    then it is fixed.  It takes a few weeks for a group to get good at arguing
    productively, and that argument is where most of the learning in this course
    happens, so we do not reshuffle when it gets uncomfortable in week two.

    **There are no lecture videos.**  Last year's version of this course had them and
    you did not watch them, and I mean that literally: there were points attached and it
    made almost no difference.  So they are gone.  You read before class instead, and in
    exchange class time gets spent on something better than me reading slides at you.

    **The problems will not have one obvious answer.**  They are chosen so that
    reasonable teams end up disagreeing.  Is this outlier real or an artifact?  Does this
    violate the assumption badly enough to matter?  When the room splits we have found
    something worth talking about, and when it doesn't I have probably written a bad
    problem.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The bargain

    I am asking you to do the reading and to show up.  In exchange:

    - **Very little to hand in on your own time.**  Your team submits its answer during
      the application exercise itself, in the room, and once you walk out that one is
      finished.  Outside class there is the reading quiz twice a week, three
      Demonstrations of Understanding, and the team project, and nothing else.
    - **The reading quiz carries 27% of your grade.**  Five questions, five minutes,
      on your own, twice a week.  That is essentially the entire enforcement mechanism,
      which is precisely why there is so little else.
    - **Two free absences from the RAP and three from application exercises**, built
      into the grading as best-of counts.  No email, no doctor's note, no explanation
      required.  If you sleep through one, that is what they are for.

    What I get out of it is a room where people are awake and arguing at 8:40 in the
    morning, which is a better deal for both of us than it may sound right now.

    And if you find yourself missing class repeatedly or falling behind, please talk to
    one of us rather than waiting it out.  We have access to resources that can help,
    and the earlier we know the more of them are still useful.

    ### On the DoUs

    Some of you did these with me in SI 345.  Same instrument, tightened up a bit.

    There are two parts.  The first is a notebook that answers a real question about
    data you have not seen before.  The second is a memo with a hard cap of **400
    words**, and it is emphatically not a walkthrough of your code.  What it should
    contain is one analytical decision you would defend, the alternative you rejected
    and why, and what you are still unsure about in your own analysis.

    Every claim in the memo has to be anchored, which means citing the cell where you
    made the choice and quoting the number your notebook actually produced.

    The cap is the hard part and it is deliberate.  Deciding which decision mattered
    most, and then cutting everything else, is itself the skill being assessed.  It is
    also, incidentally, the reason a language model cannot do this for you: it will
    happily generate an analysis, but it cannot tell me why *you* found one choice
    harder than another.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 4. Diagnostic

    Sli.do, for the next ten minutes.  **Not graded, and not recorded against you.**

    There are two reasons I am asking.  The first is that you took SI 345 from one of
    two instructors and the sections covered somewhat different ground, so I need to
    know what is actually in the room.  The second is that tonight I will post the
    shape of the answers to Canvas — the aggregate, not names and not individual
    scores — so that when you pick your own team on Wednesday you can see where the gap
    runs and choose people who cover yours.

    I am not assigning teams.  You pick them, and this is the map you will be picking
    from, which is why it is worth answering honestly.  Nobody sees your individual
    answers, and an inflated aggregate just turns Wednesday into guesswork for
    everybody.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    _q = mo.md(
        r"""
    **Go to sli.do — the join code is on the screen.**

    Eight questions, all of the form "have you used this?", with four options:

    > Never heard of it · Heard of it · Used it a bit · Comfortable with it

    | # | Thing |
    |---|---|
    | 1 | pandas `groupby` / split-apply-combine |
    | 2 | Merging DataFrames (inner, left, outer) |
    | 3 | seaborn |
    | 4 | Regular expressions |
    | 5 | SQL (any flavour) |
    | 6 | DuckDB specifically |
    | 7 | Parquet files |
    | 8 | polars |

    Plus one free-text question: **which SI 345 section did you take, and with whom?**
    """
    )
    mo.callout(_q, kind="info")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### What I expect to see

    Items 1 through 4 should be close to universal.  Items 6, 7 and 8 are the ones I
    expect to come back split roughly down the middle.

    If that is what happens, Wednesday bridges the gap and we carry on.  Nobody is
    behind.  The two sections covered different things, which is a fact about
    scheduling and not a statement about any of you.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 5. Teams

    Teams are self-selected groups of four and they form on Wednesday.

    One strong suggestion: try to include at least one person from each SI 345 section.
    After today I will post the diagnostic aggregate to Canvas so you can see where the
    tooling gap runs, and a mixed team starts the first application exercise with the
    full toolkit where a single-section team may not.  This is a recommendation rather
    than a requirement.  At the same time, most of you are seniors and some of you have
    built durable working relationships over the past few years, and I am not trying to
    break those up.

    **Teams do not change.**  Not after week two, and not after a bad application
    exercise.  The awkward stretch is weeks one to three and every team goes through it.

    Sit with your team.  In a sloped hall the only way four people can actually talk to
    each other is if they are already sitting together, and you will want to be able to
    talk.

    Twice this term you will evaluate your teammates.  You get the points for doing the
    evaluation thoughtfully rather than for the ratings you receive, though the ratings
    you do receive adjust your share of the team points.  A team that ends up carrying
    someone should not have to carry their grade as well.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 6. Before Wednesday

    1. **Take the practice quiz on Canvas.**  It opens the moment you walk out of here
       and closes **Tuesday at 20:59**.  Five questions, five minutes, ungraded.  Its
       real job is to prove the setup works before it counts for anything, so please
       actually do it.
    2. **Read the syllabus**, all of it.  Start with the at-a-glance summary if that is
       easier; both are on Canvas.
    3. **Set up your environment**, following the setup guide on Canvas.  That guide
       is where the download link for the course materials lives, so start there
       rather than hunting for the repository yourself.  You install one tool called
       `uv` and it brings the right version of Python along with it, so please do not
       go to python.org.  If it fights you, stop after fifteen minutes.  Wednesday
       handles setup, and molab runs this entire course in a browser tab with nothing
       installed at all.
    4. **Skim** the marimo *Getting Started* page.  It is short.
    5. **Read** *R for Data Science* §10.1–10.2, which is about three pages and free at
       <https://r4ds.hadley.nz/eda>.  Yes, it is an R book, and no, you do not need R;
       stop at §10.3 where the code starts.  There is a question on it on Wednesday.
    6. **Check Canvas** for the diagnostic aggregate by SI 345 section, which will be
       useful when you are picking teammates.

    ### One thing about marimo

    We are not using Jupyter this term.  marimo notebooks are reactive, which means that
    when you change a cell everything downstream of it re-runs on its own.  There is no
    stale state left over in a kernel and no output on screen that quietly stopped
    matching the code that produced it.

    A fair amount of the time you lost to debugging in SI 345 was that problem, and it
    is now structurally impossible rather than merely discouraged.

    There is a cost, which is that **a variable can only be defined in one cell**.  You
    cannot redefine `df` eight times going down the notebook the way you probably have
    been.  This is irritating for about a week and then, in my experience, it quietly
    makes you a better programmer.

    ### And about AI

    **You may use an AI agent during application exercises.**  That is deliberate, and I
    would rather explain the reasoning than just state the rule.

    An agent can compute faster than you can, and that is not what you are being graded
    on.  The exercises are built so that the computation is the easy part and the
    judgement is the actual problem: whether this outlier is real, whether this
    assumption is violated badly enough to matter, which of two defensible answers your
    team will commit to in front of the room.  An agent will answer any of those with
    total confidence and no basis whatsoever.  You still have to decide, and then defend
    it to a team that chose differently.

    Nothing in this course requires you to pay for an agent, and everything you are
    graded on works without one.

    If you ever find that the agent is simply *doing* an application exercise for you,
    please tell me.  It means I wrote a bad one and I would like to know.

    ---

    See you Wednesday.  Read the syllabus.
    """)
    return


if __name__ == "__main__":
    app.run()
