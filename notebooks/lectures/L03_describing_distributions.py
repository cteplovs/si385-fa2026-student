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

    return course_parquet, mo, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385 — Data Exploration

    ## Session 3: describing a distribution, and what that licenses you to say

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, September 9, 2026

    **Reading due today:** Bruce et al. ch. 1, through *Exploring the Data Distribution*
    (§§1–6)

    ---

    ### Today you will be able to

    - Say what the mean, the median and a trimmed mean each license you to claim about
      this distribution, and what none of the three will support
    - Separate a question this dataset can settle from one it cannot, and name the column
      it would need to carry before the second kind became the first
    - Defend a reading of the upper tail to a team that read it differently
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Where this session goes

    | Time | Block |
    |---|---|
    | 0:00–0:15 | RAT 1: the items that split the room, and appeals |
    | 0:15–0:23 | The upper tail, on your own and in silence |
    | 0:23–0:50 | Your team converges on one answer and writes it down |
    | 0:50–1:15 | Every team reveals at once, and several are asked to defend |
    | 1:15–1:20 | What survives, and before September 14 |

    This is the first application exercise that counts, and it is the same shape as the
    dry run in session 2.  The pre-read has been up since September 4; if you have not
    opened it, you can still take part.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 — RAT 1, and appeals

    Canvas gave you your score and your own answers on Tuesday night, and it did not give
    you the key.  That is deliberate.  Knowing you missed Q2 without yet knowing what was
    right is the condition under which the next fifteen minutes are worth sitting through.

    We will re-poll the items that split the room rather than my talking through all five.
    Vote, argue, vote again.

    ### Appeals

    An appeal is a team action, not an individual one.  One per team, in writing, before
    you leave the room, and it has to cite the reading — the section, and what it actually
    says.  Two grounds work:

    - **The keyed answer is wrong**, and §*n* says so.
    - **A second option is also correct as written**, and §*n* says so.

    "We thought it was ambiguous" is not a ground, because it names nothing anyone can
    check.  A successful appeal restores the credit to every member of the team that
    filed it.
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
    ---
    # 0:15 — Application exercise 1

    ## Reading a skewed distribution

    Six hundred and seven people reported their own pay to a public salary survey between
    2020 and 2022.  Nobody audited them, nobody sampled them, and everyone in the file
    chose to be in it.

    Somebody is going to quote a number off this dataset.  A recruiter will say what data
    scientists earn, a student will decide what to ask for, a journalist will write that
    the field pays six figures.  Every one of those claims is a claim about this
    distribution, and the interesting part of the distribution is its upper end.

    > ### The question
    >
    > **The upper tail of this distribution: what is it?**

    ### The first eight minutes are silent

    Please read the question, look at whatever you want to look at, and write down which
    answer you would defend and why, before anyone on your team says anything.  Your team
    cannot converge on something you have not yet decided, and eight minutes of quiet is
    what stops the first person to speak from deciding it for everyone.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The four answers

    > **A. Real structure.**  US data science pay genuinely reaches these numbers, and the
    > distribution is telling you so.
    >
    > **B. An artifact of currency conversion.**  Two hundred and nine salaries were
    > reported in some other currency and converted at a rate, on a date, that the dataset
    > does not record.  That compresses them.
    >
    > **C. An artifact of who answers.**  A voluntary salary survey is answered by people
    > with a reason to answer, and that reason is not evenly distributed.
    >
    > **D. Real, but not a tail.**  Condition on residence and this is two distributions
    > that should never have been pooled into a single summary.

    All four are defensible, which is why there are four of them.  The work is not
    deciding which one is true; it is deciding which one you would defend, and being able
    to say what the next most plausible answer would need in order to beat it.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### What you have already been told

    From the pre-read, so that nobody spends the silent phase rediscovering it:

    - Eighteen records sit at or above $250,000, running to $600,000.
    - **Every one of the eighteen was reported in US dollars.**  The highest salary
      anywhere in the file reported in any other currency is $196,979.

    The cells below are the ones the pre-read suggested you run.  They are here so that
    the hour is spent on the question rather than on typing.
    """)
    return


@app.cell
def _(plt, salaries):
    usd = salaries["salary_in_usd"]

    _fig, _ax = plt.subplots(figsize=(9, 4))
    _ax.hist(usd, bins=40, color="#4c72b0", edgecolor="white")
    _ax.axvline(usd.median(), color="#c44e52", linewidth=2, label="median")
    _ax.axvline(usd.mean(), color="#dd8452", linewidth=2, label="mean")
    _ax.set_xlabel("Reported salary, converted to US dollars")
    _ax.set_ylabel("People")
    _ax.legend()
    _fig
    return (usd,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Where you put the line changes what you can say

    Drag the cutoff and watch the two summaries move at different speeds.  §§4 and 5 of
    the reading call that difference *robustness*, and this is what it looks like on real
    money.
    """)
    return


@app.cell
def _(mo):
    cutoff = mo.ui.slider(
        start=100_000, stop=600_000, step=10_000, value=250_000,
        label="Treat everything above this as the tail:", show_value=True,
    )
    return (cutoff,)


@app.cell
def _(cutoff, mo, usd):
    _kept = usd[usd <= cutoff.value]
    _table = f"""
    | | Everyone | Below the line |
    |---|---|---|
    | Records | {len(usd)} | {len(_kept)} |
    | Mean | ${usd.mean():,.0f} | ${_kept.mean():,.0f} |
    | Median | ${usd.median():,.0f} | ${_kept.median():,.0f} |
    """
    mo.vstack([cutoff, mo.md(_table)])
    return


@app.cell
def _(salaries):
    # The eighteen records at the top, which are the thing under discussion.
    tail = salaries[salaries["salary_in_usd"] >= 250_000].sort_values("salary_in_usd")
    tail[["experience_level", "job_title", "salary_in_usd", "salary_currency",
          "employee_residence", "company_location", "remote_ratio"]]
    return (tail,)


@app.cell
def _(salaries):
    # Three splits.  One of them changes the picture more than the other two.
    by_residence = salaries.groupby(
        salaries["employee_residence"].eq("US").map({True: "US", False: "everywhere else"})
    )["salary_in_usd"].agg(["count", "median", "max"])

    by_currency = salaries.groupby(
        salaries["salary_currency"].eq("USD").map({True: "USD", False: "converted"})
    )["salary_in_usd"].agg(["count", "median", "max"])

    by_year = salaries.groupby("work_year")["salary_in_usd"].agg(["count", "median", "max"])

    by_residence, by_currency, by_year
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Two things in the table of eighteen worth looking at twice

    The experience levels are mixed rather than a clean seniority tier.  Eight are senior
    and five are executive, but four are mid-level, including two at $450,000, and one is
    entry-level.  So "these are just the executives" is an answer the data declines to
    support.

    And seventeen of the eighteen live in the United States.  The one who does not is a
    senior machine learning scientist in Japan, whose pay was reported in US dollars.
    """)
    return


@app.cell
def _():
    # Your workspace.  Anything you want to check before you commit to a letter.
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:23 — With your team

    Four people, one letter.  Nobody abstains, and a team that cannot agree still has to
    pick, which is an ordinary thing to have to do.

    ### Submitting, and please have both in before 0:50

    **First, on Canvas.**  This is the submission that counts.  One person per team, and
    a different person each time.  In this order:

    1. Your **team number**
    2. Your **choice** — the letter on its own
    3. Your **justification**
    4. **Who is here today**, first names are fine

    **Then, in Sli.do**, click your letter.  Sli.do draws the histogram we look at
    together and nothing else; it is not graded.  If it is broken for you, submit on
    Canvas anyway and tell one of us afterwards.

    ### What the justification has to do

    Three or four sentences, and not a summary of what you did.  Two things:

    - **The one check you would run** to separate your answer from the next most
      plausible one.
    - **The column this dataset would need to carry** for that check to be possible.

    A team that writes "the median is robust to outliers" has restated the reading.  A
    team that writes "we would want the conversion date, because a 2020 euro salary and a
    2022 euro salary were almost certainly not converted at the same rate, and this file
    records neither" has done the work.

    ### How this is marked

    Six points for a committed choice with a real justification submitted before the
    reveal, and zero otherwise.  Only the justification is graded, not the choice itself,
    and you are not marked on whether your letter turns out to be the popular one.

    The deadline is hard, because committing before you see anyone else's answer is the
    entire point of doing it this way.  If you miss one, the best-20-of-23 count absorbs
    it and there is nothing to email me about.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:50 — Everyone reveals at once

    The poll closes and the histogram goes up before anybody speaks.  If teams revealed
    one after another, the later ones would drift towards whatever was winning, and the
    disagreement that makes this worth an hour would quietly disappear.

    Then I will ask about four teams to defend, chosen from the distribution rather than
    at random: one from the largest group, one from the largest minority, and one from
    whichever corner is thinly populated that day.  I will say why I picked each.  Being
    asked to defend an unpopular letter is not a verdict on the letter.

    I keep a log of which teams have defended, and across twenty-three exercises it comes
    to two or three turns each.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 1:15 — Consolidation

    The dataset records what people said they earn.  It does not record who was asked,
    who declined, what rate their currency was converted at, or on what date.  Three of
    the four answers on offer turn on exactly those absent columns, which is why no amount
    of further computation on this file will settle the question — and why naming the
    missing column is the part worth marking.

    ### Before September 14

    - **Reading:** Tufte, excerpt (posted on Canvas)
    - **RAT 2** opens Friday September 11 at 09:50 and closes Sunday September 13 at 20:59
    """)
    return


if __name__ == "__main__":
    app.run()
