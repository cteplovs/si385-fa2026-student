# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "pandas>=3.0.5",
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

    return course_csv, mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385 — Data Exploration

    ## Session 5: Missingness, outliers, and data quality as a judgement

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, September 16, 2026

    **Reading due today:** van Buuren, *Flexible Imputation of Missing Data*, ch. 1,
    §§1.1–1.3, at <https://stefvanbuuren.name/fimd/ch-introduction.html>.
    McKinney ch. 7 as review.

    ---

    ### Today you will be able to

    - Tell a value that is plainly wrong from a blank whose meaning is contested
    - Say what a denominator assumes about the rows it leaves out
    - Decide what a blank means, cite evidence from the rest of the row for that
      reading, and name what would overturn it
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 — RAT 3, and appeals

    Canvas gave you your score and your own answers when you submitted, and it did not
    give you the key.  Same arrangement as the last two weeks and for the same reason.

    We will re-poll the items that split the room rather than my talking through all
    five.  Vote, argue, vote again.

    Appeals work as before: one per team, in writing, before you leave, citing the
    section and what it actually says.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:15 — Application exercise 3

    ## What does a blank mean?

    In 2014 Open Sourcing Mental Illness (OSMI), a non-profit, ran an online survey of
    people working in tech about mental health and the workplace.  1,259 people
    answered.  The responses are published under CC BY-SA 4.0, and this file is
    theirs, unchanged apart from one column dropped: `comments`, which is free text
    about people's mental health and which nothing today needs.

    Each row is one person.
    """)
    return


@app.cell
def _(course_csv):
    survey = course_csv("survey.csv").drop(columns=["comments"])
    survey.head()
    return (survey,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Two warm-ups before the hard one

    **First, a blank that is not a problem.**  The survey asked *If you live in the
    United States, which state or territory do you live in?*  Consider how often `state`
    is blank, split by whether the person lives in the US.
    """)
    return


@app.cell
def _(pd, survey):
    _in_us = survey["Country"].eq("United States").map({True: "US", False: "not US"})
    pd.DataFrame({
        "people": survey.groupby(_in_us).size(),
        "state blank (%)": (survey["state"].isna().groupby(_in_us).mean() * 100).round(1),
    })
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nearly every non-US blank means *this question did not apply to me*, and you know
    that because the question says so.  Filling those in, or dropping those people,
    would be a mistake about the survey rather than about the data.

    **Second, a value that is plainly wrong.**  Here are the ages outside 16 to 80.
    """)
    return


@app.cell
def _(survey):
    survey.loc[~survey["Age"].between(16, 80), ["Age", "Country", "Gender"]]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Nobody taking a workplace survey is −1726 or 99,999,999,999 years old.  You can
    argue about 11, but not for long.  These are outliers of the uncontroversial kind:
    the value is wrong and you know it is wrong, even though you do not know what it
    should have been.

    ### The hard one

    The survey also asked this, with four possible answers:

    > *If you have a mental health condition, do you feel that it interferes with your
    > work?*  Never / Rarely / Sometimes / Often

    Please read it twice.  It opens with *if*.
    """)
    return


@app.cell
def _(survey):
    survey["work_interfere"].value_counts(dropna=False)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **264 people left it blank**, 21% of the file.  The survey does not record why.
    Some of them may have no condition and skipped a question that did not apply.
    Some may have a condition and preferred not to say.  Unlike `state`, the question
    does not settle it.

    ### One question, two numbers

    609 people answered *Often* or *Sometimes*.  What share of people is that?  It
    depends on what you divide by, and what you divide by depends on what you have
    decided the blanks are.  Please switch between the two and watch the planning figure
    move.
    """)
    return


@app.cell
def _(mo):
    blank_as = mo.ui.dropdown(
        options=[
            "Dropped: not in the denominator",
            "Counted: as 'does not interfere'",
        ],
        value="Dropped: not in the denominator",
        label="Treat the 264 blanks as:",
    )
    return (blank_as,)


@app.cell
def _(blank_as, mo, survey):
    _interferes = survey["work_interfere"].isin(["Often", "Sometimes"]).sum()
    _answered = survey["work_interfere"].notna().sum()

    if blank_as.value.startswith("Dropped"):
        _denominator = _answered
        _who = "the people who answered"
    else:
        _denominator = len(survey)
        _who = "everyone in the file"

    _share = _interferes / _denominator
    mo.vstack([
        blank_as,
        mo.md(
            f"**{_interferes:,} of {_denominator:,}**, {_who}: "
            f"**{_share:.1%}**, or about **{round(_share * 200)} people** "
            f"in a company of 200."
        ),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    61.2% if the blanks are dropped, 48.4% if they are counted as a no.  Neither number
    is a calculation error.  Each is the right answer to a different claim about who
    the 264 people are.

    ---

    ## Part 1 — eight minutes, on your own, in silence

    A 200-person software company is choosing a mental health benefit.  The HR lead has
    no data on the company's own staff, so the plan has to come from this survey.

    > **How many of the 200 people will say a mental health condition interferes with
    > their work at least sometimes?  What should the HR lead plan for?**

    Take a position and write down one sentence saying what you think a blank means.
    Do not talk to your team yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:23 — With your team

    Argue to a decision.  One choice, and one justification, both submitted before the
    reveal.

    > **What should the HR lead plan for?**
    >
    > **A.** 61%, about 122 people.  The question was only for people with a condition,
    > and the blanks are people it did not apply to.  They do not belong in the
    > denominator.
    >
    > **B.** 48%, about 97 people.  The blanks are almost all people who never sought
    > treatment, and they answer the rest of the survey like people with no condition.
    > They are still staff, so they count, as "does not interfere".
    >
    > **C.** A range, 97 to 122 people.  Which end is right depends on why people
    > skipped the question, and the file cannot say.
    >
    > **D.** Do not plan from this survey.  1,259 people who chose to answer a mental
    > health non-profit's survey are not this company's staff, and the missing
    > responses that matter are from everyone who never opened it.

    ### The justification, which is the only graded part

    Three or four sentences, plus one line of code.

    1. **Say what you think a blank means.**
    2. **Cite one number from the file that this notebook does not show you**, and paste
       the line of code that produced it.  It has to bear on what the blanks mean.  One
       line of pandas is enough.  It does not matter who on the team writes it, or
       whether you have help, as long as it runs against `survey` and produces the
       number you cite.
    3. **Name the one fact about the 264 people** that, if you could learn it, would move
       you off your answer.

    "The data is not missing at random" names a category and stops there.  The version
    that does the work says which rows you looked at, what you found in them, and why it
    tells you what a blank person is likely to be.

    ### Submitting

    **On Canvas first**, *AE 3: What does a blank mean?*  This is the submission that
    counts.  One person submits for the team, and it should be a different person each
    time.  In this order:

    1. Your **team name**
    2. Your **choice**, just the letter
    3. Your **justification**, with the line of code and the number it produced
    4. **Who is here today**, first names are fine

    **Then in Sli.do**, click your letter.  Sli.do draws the histogram the room looks
    at, and it is not graded.  If Sli.do is broken for you, submit on Canvas anyway.
    """)
    return


@app.cell
def _(survey):
    # Your team's line of code goes here.
    #
    # It has to produce one number from `survey` that the cells above do not show,
    # and the number has to bear on what the 264 blanks mean.  The rest of each row
    # is still there.
    #
    # If you add more cells, start new variable names with an underscore (_counts,
    # _blank) so they cannot collide with the notebook's own.
    survey
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:50 — Report

    All thirty-five teams reveal at once.  Then four or five defend.

    Please do not read your justification out when you defend.  I already have it.
    What the room needs from you is the number you found, and an answer to one
    question: what would a blank person have to be for the option next to yours to be
    the right call?
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 1:15 — Consolidation

    OSMI ran the survey again in 2016, and changed one thing about this question.  It
    added a fifth answer: **Not applicable to me.**  557 of the 1,433 people who
    answered in 2016 chose it, and the question has no blanks at all.

    That did not settle what the 2014 blanks meant.  It settled what the 2016 ones
    would have meant, by asking.  The best fix for an ambiguous blank is usually made
    before the data is collected, which is small comfort when the data you have is the
    2014 file.

    ### Before September 21

    - **Reading:** Bruce et al. ch. 1, §*Exploring Two or More Variables*
    - **RAT 4** opens Friday September 18 at 09:50 and closes Sunday September 20 at
      20:59
    """)
    return


if __name__ == "__main__":
    app.run()
