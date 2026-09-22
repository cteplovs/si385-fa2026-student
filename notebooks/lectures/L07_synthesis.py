# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
#     "matplotlib>=3.9",
# ]
# ///

import marimo

__generated_with = "0.24.0"
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

    ## Session 7: Synthesis — exploring an unfamiliar dataset

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, September 23, 2026

    **No reading due today.** The four weeks behind you are the preparation.

    ---

    ### Today you will be able to

    - Work an unfamiliar file through one analytical lens, and report what that lens on
      its own is able to establish
    - Reconcile four accounts of the same data that do not agree with one another
    - Say what an absent value does and does not entitle you to claim about the records
      behind it
    - Decide what to tell somebody when the file that exists to answer their question
      turns out not to answer it
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:00 — The question

    Somebody asks you a direct question — a younger sibling working out where to apply,
    or a student at a college fair, or some earlier version of yourself.

    > **What does a data science degree pay?**

    In front of you is the file that the United States Department of Education publishes
    for the express purpose of answering precisely that.
    """)
    return


@app.cell
def _(course_parquet):
    degrees = course_parquet("college_scorecard_bachelors.parquet")
    degrees.head()
    return (degrees,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    There are 70,557 bachelor's programs here, drawn from 2,537 institutions across 388
    fields of study, with one row for each institution paired with each field.

    Nine of the columns carrying money are shadowed by a `_status` column, which records
    why the figure beside it is or is not there.
    """)
    return


@app.cell
def _(degrees):
    degrees[
        ["field", "institution", "n_awards", "earn_median_1yr", "earn_median_1yr_status"]
    ].head(8)
    return


@app.cell(hide_code=True)
def _(degrees, mo, pd):
    _fields = ["Data Science.", "Data Analytics.", "Computer Science."]
    _d = degrees[degrees["field"].isin(_fields)]
    _t = pd.DataFrame({
        "programs": _d.groupby("field").size(),
        "reporting earnings": _d.groupby("field")["earn_median_1yr"].count(),
        "median class size": _d.groupby("field")["n_awards"].median(),
    }).reindex(_fields)

    mo.vstack([
        mo.md(r"""
        ### What the session turns on

        The pre-read handed you this one already.  Here it comes out of the file rather
        than out of a table that somebody typed up.
        """),
        _t,
        mo.md(r"""
        Every bachelor's program in data science that this file covers has been
        suppressed, as has every program in data analytics, and the median one among them
        graduated two people.
        """),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Your team divides four ways

    Each of you takes one lens for the first part of the period, and the four lenses are
    the four sessions you have just worked through.  Please sort out who is taking which
    now, using the dropdown below to move between them.  Nothing prevents a team that is
    short of people from covering more than one, beyond the time it takes.

    | Analyst | Lens | From |
    |---|---|---|
    | **1** | Describe the distribution — centre, spread, shape | Session 3 |
    | **2** | Look at it — what the plot shows that the summary does not | Session 4 |
    | **3** | What is missing, and whether the missingness is itself a finding | Session 5 |
    | **4** | Condition on a third variable, and see whether the story survives | Session 6 |

    These four accounts are unlikely to agree with one another, and reconciling them is
    where the greater part of the period is going to go.
    """)
    return


@app.cell
def _(mo):
    analyst = mo.ui.dropdown(
        options={
            "1 — Describe the distribution": 1,
            "2 — Look at the plot": 2,
            "3 — What is missing": 3,
            "4 — Condition on something": 4,
        },
        value="1 — Describe the distribution",
        label="I am analyst:",
    )
    return (analyst,)


@app.cell(hide_code=True)
def _(analyst, degrees, mo, pd, plt):
    _n = analyst.value

    if _n == 1:
        _e = degrees["earn_median_1yr"].dropna()
        _summary = pd.DataFrame({
            "value": [
                len(_e), _e.mean(), _e.median(), _e.std(), _e.skew(),
                _e.min(), _e.quantile(0.05), _e.quantile(0.95), _e.max(),
            ]
        }, index=["programs", "mean", "median", "sd", "skew",
                  "min", "p5", "p95", "max"]).round(2)
        _view = mo.vstack([
            mo.md(r"""
            ### Analyst 1 — the distribution

            Median earnings one year after graduation, taken across every program that
            reports such a figure.  Please describe it the way session 3 asked you to,
            working through centre, spread and shape, and saying in each case what that
            particular property licenses you to claim.
            """),
            _summary,
            mo.md(
                "If you had to write a single sentence about this column, what would it "
                "say?"
            ),
        ])

    elif _n == 2:
        _d = degrees.dropna(subset=["debt_median", "earn_median_1yr"])
        _fig, _ax = plt.subplots(figsize=(7, 5))
        for _c, _colour in [("Public", "#4477aa"),
                            ("Private, nonprofit", "#ee6677"),
                            ("Private, for-profit", "#228833")]:
            _s = _d[_d["control"] == _c]
            _ax.scatter(_s["debt_median"], _s["earn_median_1yr"],
                        s=4, alpha=0.25, label=_c, color=_colour)
        _ax.set_xlabel("median debt at graduation (USD)")
        _ax.set_ylabel("median earnings, one year out (USD)")
        _ax.legend(markerscale=3, frameon=False)
        _ax.set_title(f"{len(_d):,} programs reporting both")
        _view = mo.vstack([
            mo.md(r"""
            ### Analyst 2 — the plot

            Debt plotted against earnings, coloured according to who runs the
            institution.  Session 4 concerned itself with what a picture is able to show
            that a summary cannot, and with the various ways in which a well-made picture
            can nonetheless answer the wrong question.
            """),
            _fig,
            mo.md(
                "What is present in this plot that analyst 1's table has no way of "
                "holding?"
            ),
        ])

    elif _n == 3:
        _status = degrees["earn_median_1yr_status"].value_counts().rename("programs")
        _size = degrees.groupby("earn_median_1yr_status", observed=True)["n_awards"].median()
        _by_control = degrees.assign(
            reported=degrees["earn_median_1yr"].notna()
        ).groupby("control")["reported"].agg(["size", "mean"]).round(3)
        _view = mo.vstack([
            mo.md(r"""
            ### Analyst 3 — what is missing

            Two different absences sit inside this one column.  A cell marked
            `suppressed` is one where the Department holds the number and declines to
            publish it, on the grounds that the cell is too small to be published without
            exposing the people counted in it, whereas `not reported` means that nothing
            was ever collected.
            """),
            _status,
            mo.md(
                "Median graduating class, by which kind of absence.  The pre-read gave "
                "you four for the absent programs taken together; separating them is "
                "where that four came from."
            ),
            _size,
            mo.md("How often each kind of institution reports anything at all:"),
            _by_control,
            mo.md(
                "Session 5 asked what a blank means.  What is it that a *suppressed* "
                "blank entitles you to say about the people counted inside it?"
            ),
        ])

    else:
        _pooled = degrees.groupby("control")["earn_median_1yr"].agg(
            programs="count", median="median"
        )
        _cs = degrees[degrees["field"] == "Computer Science."].groupby(
            "control"
        )["earn_median_1yr"].agg(programs="count", median="median")
        _view = mo.vstack([
            mo.md(r"""
            ### Analyst 4 — conditioning

            Pooled across all 388 fields, by who runs the institution:
            """),
            _pooled,
            mo.md("The same comparison, inside computer science alone:"),
            _cs,
            mo.md(
                "Session 6 called this conditioning.  Which of these two tables would "
                "you be willing to put in front of somebody, and what does the other one "
                "do to it once they have seen it?"
            ),
        ])

    mo.vstack([analyst, _view])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Part 1 — twelve minutes, on your own, in silence

    For these twelve minutes only, please stay inside the lens you were given, since the
    point of the exercise is that four people arrive at the table having looked at the
    same file in four incompatible ways.  Write down what your lens shows you and what
    you take it to settle.

    Write down as well whatever it is that your lens cannot reach, because you will be
    asked for it shortly, and each of the other three will have run into the same
    difficulty from a different direction.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:20 — With your team

    The division of labour is over.  From here the whole file is open to all four of you,
    and the dropdown above is how you walk the team through each account in turn, so that
    everyone sees what everyone else was looking at rather than taking it on trust.

    What you are arguing about is which of the four accounts the eventual answer ought to
    be addressed to, and what the other three do to it.

    > **A high-school student asks you what a data science degree pays, and you have in
    > front of you the federal file that exists to answer exactly that question.  What do
    > you tell them?**
    >
    > **A.** Give them the computer science figure, roughly **$71,000**.  It is the
    > nearest field that reports anything, there are 355 programs behind it, and a
    > seventeen-year-old asking about money is owed a number.
    >
    > **B.** Give them a broader bucket — *Computer and Information Sciences, General*,
    > roughly **$61,000** across 462 programs.  The methodology of the file itself
    > recommends aggregating upward when cells are small, and this is the bucket into
    > which a data science program would most plausibly fall.
    >
    > **C.** Give them no number at all.  Every available substitute answers a question
    > about a different degree, and the gap between A and B is $9,500 that depends on
    > nothing but which neighbour you happened to choose.
    >
    > **D.** Give them the absence itself as the answer.  All 144 programs are suppressed
    > and the median one graduates two people, so what the file does report is that this
    > degree is too new and too small to have generated an earnings record.

    ### The justification

    This is written by the team rather than by any one of you, and it runs to three or
    four sentences plus **three to five lines of code**.

    1. **Set out what each lens found**, in a line apiece.  Where a lens went unworked,
       please name it and say what you would have wanted from it.  That is part of the
       submission rather than an admission, and the marker reads it as evidence that you
       know the shape of your own argument.
    2. **Name the account that most contradicted the others**, and say what the team
       decided to do about it.  This is the part that is actually being marked.
    3. **Cite a number from the file that this notebook does not display**, together with
       the lines that produced it.  Show the counts alongside the medians, because a
       table of medians with nothing to say how many records sit behind each one will not
       do.

    ### Submitting

    **On Canvas first**, *AE 5: What does this degree pay?*  One person for the team,
    ideally a different person from last time.  In this order: team name, your letter,
    your justification with the code and its table, which lens each of you worked, and
    who is here today.

    **Your code must be marked as code in the Canvas text box.** Select the lines you
    pasted, open the **Format** menu in the editor toolbar, and choose **Code**.
    You will know it worked because the text turns monospaced and your indentation is
    still there.

    **Then in Sli.do**, click your letter.  One click per team rather than per person.
    Sli.do draws the histogram the room looks at before anybody speaks, and is not graded.
    """)
    return


@app.cell
def _(degrees):
    # Your team's three to five lines go here.
    #
    # Find a number this notebook does not show you.  The columns above are not all of
    # them; there are debt figures, earnings four years out, and splits by Pell status
    # and by gender, each with its own _status column.
    #
    # Print the counts next to whatever you compute.  `degrees.groupby(...)` and
    # `degrees.pivot_table(...)` will each do it in one line.
    #
    # If you add cells, start new variable names with an underscore (_table, _counts)
    # so they cannot collide with the notebook's own.
    degrees.columns
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:45 — Report

    All thirty-five teams reveal at once, after which four or five are asked to defend.

    When your turn comes, please lead with the disagreement rather than with the letter
    you chose, since what the room needs to hear is which of your four accounts pulled
    hardest against the others and what you decided to do about it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 1:05 — Consolidation

    The rule that emptied the data science column is not published.  The Department's own
    documentation says so directly:

    > "Debt metrics have been treated via cell suppression methods, and to further reduce
    > disclosure risk, information about the specific suppression rules is not available
    > to the public."

    The rule is withheld on the grounds that a published threshold can be worked
    backwards, so that a reader who knows where the line falls can begin to recover the
    very values the line was drawn to protect.  Session 5 argued that you cannot test
    which missingness mechanism you happen to be working under; here the agency that
    holds the mechanism has concluded that disclosing it would itself amount to a
    disclosure.

    Earnings receive a second treatment as well, in that every published count and every
    published median has had noise added to it by a differentially private algorithm,
    after which the suppression proceeds in two stages, first eliminating the cells that
    are too small and then discarding any surviving median whose relative error exceeds a
    threshold that is likewise undisclosed.  A number in this file is therefore not quite
    the number, and an absent one is absent partly on account of the size of its cell and
    partly on account of where the noise happened to fall.

    Both of the decisions that shaped this file most heavily were taken in order to
    suppress less of it.  Students are pooled into two-year cohorts so as to raise the
    cell sizes, and programs are collapsed into four-digit CIP codes for the same reason,
    with the documentation acknowledging that finer variation "will not be observed using
    the current methodology."

    Data science emerges from all of that blank, on 144 programs with a median of two
    graduates apiece, two award years already pooled together, and a final rule that
    nobody outside the Department is permitted to read.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 1:10 — Demonstration of Understanding 1

    **Assigned today.  Due Monday, October 5 at 23:59.  Individual work, 120 points.**

    ## You have inherited an analysis

    An analyst has left the Office of Data Analytics, and their last piece of work has
    landed on your desk: a briefing note for a city committee that wanted to know whether
    chain restaurants have an advantage in health inspections.  It reports one number.

    > **Independent restaurants score about 44% worse than chain restaurants.**

    The notebook is `notebooks/dou/DoU01_inherited.py`, which arrives in your course
    folder with this one.  It runs, it contains no bugs, and its arithmetic is correct.
    Instead, it contains several decisions its author made but did not record, and those
    decisions were not trivial, nor were the impacts stemming from them.

    Your work is to find them, take the one you judge most consequential, change it, and
    then defend what you did.  That is **three or four cells of your own code** — 40
    points — and **a 400-word memo** worth 80.

    The hour you have just spent was preparation for this, and the three blocks of the
    memo map onto it directly.

    The memo asks for three blocks inside a limit of 400 words.  The first of them is
    **the single analytical decision you would defend**, which is the position you took
    in silence at 0:08 and then had to hold against three people who had been looking at
    the same file in quite different ways.  The second is **the alternative you rejected,
    and why you rejected it**, which is what your team was doing for the twenty-five
    minutes between 0:20 and 0:45.  The third is **what you are still unsure about in
    your own analysis**, which is the thing you wrote down at the end of part one, and
    which any team short of members has already had to commit to writing.

    Every claim in the memo has to be anchored, which means naming the cell in which you
    made the choice and quoting the numbers that your own notebook produced.  A memo that
    could have been written about anybody's analysis is, so far as this course is
    concerned, about nobody's.

    The data is 295,295 New York City restaurant inspections, and you have not seen it
    before.  Nothing in it has been cleaned.

    An agent will list the inherited notebook's buried decisions faster than you can, and
    asking it to do that is a good use of one.  What it cannot tell you is which of them
    matters most here, because that depends on what the committee is going to do with the
    number, and the committee is not in the file.

    The full brief is on Canvas and we will go through it now.

    ### Between now and then

    Session 8 opens the second module on Monday September 28 with sampling and
    uncertainty, and RAT 5 opens on Friday at 09:50.  There are three free late days
    available for Demonstrations of Understanding, taken in whole 24-hour blocks, and
    using one requires no explanation from you.
    """)
    return


if __name__ == "__main__":
    app.run()
