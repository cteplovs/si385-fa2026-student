# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
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

    return course_parquet, mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385 — Data Exploration

    ## Session 6: Conditioning, faceting, and finding structure without a model

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, September 21, 2026

    **Reading due today:** Bruce et al. ch. 1, §*Exploring Two or More Variables*

    ---

    ### Today you will be able to

    - Condition a comparison on a third variable, and say what the grouping changed
    - Read the cell counts beside a table of group medians, and say which cells cannot
      carry a claim
    - Rule on whether a difference between groups is about the groups or about who is
      in them
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 — RAT 4

    When you worked through the RAT, Canvas gave you your score and your own answers
    when you submitted, but it did not
    give you the key.

    We will re-poll the items that split the room (although the ones that did still scored more than 90% of you getting it right).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:15 — Application exercise 4

    ## Does remote work pay?

    This is the salary file from session 3: 607 data science roles reported between 2020
    and 2022, one row per role.  In session 3 you described a single column of it.  Today
    the question needs two (and then three).

    `remote_ratio` is 0 for onsite, 50 for hybrid, and 100 for fully remote.
    """)
    return


@app.cell
def _(course_parquet):
    salaries = course_parquet("ds_salaries.parquet")
    salaries.head()
    return (salaries,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The claim to consider

    A company's People team is rewriting its job adverts.  Someone has run the obvious
    summary and brought this to the meeting.
    """)
    return


@app.cell
def _(salaries):
    pooled = salaries.groupby("remote_ratio")["salary_in_usd"].agg(
        roles="size", median_usd="median"
    ).round(0)
    pooled
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Hybrid roles come out about **$45,000 below fully remote ones**, and below onsite
    roles too.  The dip in the middle is the interesting part: whatever story
    you tell about remote work, it has to explain why half-remote is worse than either
    end.

    ### The same table, conditioned

    Please group the comparison by a third variable and watch the medians move.  The
    counts are beside them, and they matter as much as the medians.
    """)
    return


@app.cell
def _(mo):
    condition_on = mo.ui.dropdown(
        options=[
            "Nothing — everyone pooled",
            "Company location: US or not",
            "Company size",
            "Year",
        ],
        value="Nothing — everyone pooled",
        label="Condition on:",
    )
    return (condition_on,)


@app.cell
def _(condition_on, mo, pd, salaries):
    _s = salaries.copy()
    _s["us"] = _s["company_location"].eq("US").map({True: "US", False: "not US"})

    _by = {
        "Nothing — everyone pooled": None,
        "Company location: US or not": "us",
        "Company size": "company_size",
        "Year": "work_year",
    }[condition_on.value]

    if _by is None:
        _table = _s.groupby("remote_ratio")["salary_in_usd"].agg(
            roles="size", median_usd="median"
        ).round(0)
    else:
        _median = _s.pivot_table(index="remote_ratio", columns=_by,
                                 values="salary_in_usd", aggfunc="median").round(0)
        _count = _s.pivot_table(index="remote_ratio", columns=_by,
                                values="salary_in_usd", aggfunc="size")
        _table = pd.concat({"median_usd": _median, "roles": _count}, axis=1)

    mo.vstack([condition_on, _table])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Two things:

    **The file is 58% US companies, and they are not spread evenly.** Seventy per cent of
    the fully remote roles sit at US companies; twenty per cent of the hybrid ones do.

    **Some of these cells are tiny.** A median over four roles is questionable.
    Read the counts next to every median you are tempted to quote.

    ---

    ## Part 1 — eight minutes, on your own, in silence

    > **The People team wants to put a line in the advert: *fully remote roles in this
    > field pay about 64% more than hybrid ones*.  The arithmetic is right.  What should
    > they do with it?**

    Take a position and write down the grouping you would want to see before you signed
    off on that sentence.  Do not talk to your team yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:23 — With your team

    Argue to a decision.

    > **What should the People team do with the sentence?**
    >
    > **A.** Publish it.  The medians are what they are, $115,000 against $69,999, and
    > the sentence describes this file accurately.
    >
    > **B.** Drop it.  The gap is about *who* is in each group: seven in ten fully remote
    > roles are at US companies against two in ten hybrid ones, and within the US the
    > three arrangements land within about 15% of each other.
    >
    > **C.** Drop it and say the opposite where it applies.  Outside the US, fully remote
    > has the *lowest* median of the three, so a sentence about "this field" is wrong in
    > the direction that matters for anyone not hiring in America.
    >
    > **D.** Publish nothing about hybrid at all.  There are 99 hybrid roles in the whole
    > file and four of them are US roles in 2022.  Whatever the medians say, this file
    > cannot rank three working arrangements.

    ### The justification

    Three or four sentences, plus **three to five lines of code**.

    1. **Say what the pooled gap is measuring**, in your own words.
    2. **Condition on a variable this notebook does not use**, in three to five lines.
       Paste the lines and the table they produced.  Show the counts as well as the
       medians — a table of medians with no counts will not do.
    3. **Say what your table did to the claim**: strengthened it, broke it, or left it
       where it was.

    `job_title`, `employee_residence`, `experience_level`, `employment_type`, and
    residence against company location are all in the file and none of them are used
    above.  Pick one and see.

    ### Submitting

    **On Canvas first**, *AE 4: Does remote work pay?*  One person for the team, ideally a
    different person from last time.  In this order: team name, your letter, your
    justification with the code and its table, and who is here today.

    **Your code must be marked as code in the Canvas text box.** Select the lines you
    pasted, open the **Format** menu in the editor toolbar, and choose **Code**.
    You will know it worked because the text turns monospaced and your indentation is
    still there.

    **Then in Sli.do**, click your letter.  Sli.do draws the histogram and is not graded.
    """)
    return


@app.cell
def _(salaries):
    # Your team's three to five lines go here.
    #
    # Condition the comparison on a variable the cells above do not use, and print
    # the counts next to the medians.  `salaries.pivot_table(...)` will do it in one
    # line if you want it to; the other lines are yours to spend on checking what you
    # found.
    #
    # If you add cells, start new variable names with an underscore (_table, _counts)
    # so they cannot collide with the notebook's own.
    salaries.columns
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:50 — Report

    All thirty-five teams reveal at once.  Then four or five defend.

    When you defend, please lead with your table rather than your letter.  The question
    the room needs answered is what your grouping did to the claim, and whether anyone
    else's grouping did the opposite.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 1:15 — Consolidation

    Bruce et al. plotted King County house values against floor area, saw faint bands
    above the main cloud, and faceted by zip code.  The bands resolved into
    neighbourhoods.  The structure was in the pooled plot the whole time and unreadable
    there, and conditioning did not add data — it named the variable that was already
    doing the work.

    Today's file behaves the same way, in a table rather than a plot.  The pooled
    medians are not wrong.  They answer a question about the roles in this file, which
    is not the question anyone in that meeting was asking.

    One thing this session adds to the reading: **a facet with four rows in it is a
    picture of nothing**, and the counts are what tell you so.  You will see a
    conditioned table that looks decisive again, and the first thing to do is ask how
    many records are behind each cell.

    ### Before September 23

    - **No reading.** Session 7 is the synthesis session: a full period with an
      unfamiliar dataset, and **DoU 1 is assigned** that day.
    - There is no RAT for session 7.
    """)
    return


if __name__ == "__main__":
    app.run()
