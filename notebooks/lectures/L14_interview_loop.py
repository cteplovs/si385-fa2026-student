# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "pyarrow>=17",
#     "statsmodels>=0.14",
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
    import statsmodels.formula.api as smf

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

    return course_parquet, mo, np, pd, smf


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 14: The interview loop

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, October 21, 2026

    **No reading and no RAT today.** This is the synthesis session for Module 2.

    ---

    ### Today you will be able to

    - Read a statistical function you did not write and say what it returns
    - Write a bootstrap confidence interval without a library call
    - Judge whether a change in a summary reflects a change in the thing measured or a change in
      who was measured
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:00 · The rounds of a data science interview

    A data scientist described their last ten Python interview rounds for product and marketing
    roles, nearly all at large technology companies. Only one was a LeetCode-style puzzle.

    | Round | Came up in |
    |---|---:|
    | Recreate a stats concept as a function | 3 of 10 |
    | AI-assisted, open book: an investigation, "closer to a diagnostic case study than a coding puzzle" | 3 of 10 |
    | Pandas and data manipulation, with some modelling | 2 of 10 |
    | Interpret code handed to you | 1 of 10 |
    | Base Python, LeetCode-style | 1 of 10 |

    They also noticed that syntax counted for little: in the LeetCode round they made several
    syntax mistakes, were clear about the logic, and passed.

    Today runs three of those rounds with Module 2's material. The first two are warm-ups and
    are not graded; the third is application exercise 12.
    """)
    return


@app.cell
def _(course_parquet, np):
    salaries = course_parquet("ds_salaries.parquet")
    salaries["log_salary"] = np.log(salaries["salary_in_usd"])
    salaries.head()
    return (salaries,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:05 · Round 1: interpret code handed to you

    **Four minutes, on your own, without running anything.** A colleague wrote the function below
    to test whether fully remote data scientists are paid differently from those who work in the
    office. Please read it and decide what it returns.

    > **What does `mystery(office, remote)` return?**
    >
    > **A.** A valid two-sided p-value for the difference in mean salary.
    >
    > **B.** The same p-value whatever the data are.
    >
    > **C.** A confidence interval for the difference in mean salary.
    >
    > **D.** The observed difference in mean salary.

    Vote in Sli.do. Then, and only then, press the button.
    """)
    return


@app.cell
def _(np):
    def mystery(a, b, n=5000, seed=0):
        rng = np.random.default_rng(seed)
        observed = np.mean(b) - np.mean(a)
        count = 0
        for _ in range(n):
            a_shuffled = rng.permutation(a)
            diff = np.mean(b) - np.mean(a_shuffled)
            if abs(diff) >= abs(observed):
                count += 1
        return count / n

    return (mystery,)


@app.cell(hide_code=True)
def _(mo):
    run_mystery = mo.ui.run_button(label="Run mystery(office, remote)")
    run_mystery
    return (run_mystery,)


@app.cell
def _(mo, mystery, run_mystery, salaries):
    mo.stop(not run_mystery.value, mo.md("*Press the button after the vote.*"))
    office = salaries.loc[salaries["remote_ratio"] == 0, "salary_in_usd"].to_numpy()
    remote = salaries.loc[salaries["remote_ratio"] == 100, "salary_in_usd"].to_numpy()
    mo.md(f"`mystery(office, remote)` returns **{mystery(office, remote)}**.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## 0:15 · Round 2: recreate a stats concept

    **With your team.** Please write `bootstrap_ci`, which returns a 95% percentile interval for
    any statistic, using numpy and nothing from `scipy.stats`. Talk the logic through before
    you write any code; as in the interview above, a syntax slip matters far less than a
    mistake in the logic.

    > **What interval does your function give for the median salary in 2022?**
    >
    > **A.** About \$113,000 to \$130,000
    >
    > **B.** \$120,000 to \$120,000
    >
    > **C.** About \$100,000 to \$140,000
    >
    > **D.** About \$118,000 to \$131,000

    The function returns `None` until you write it. Your figures will differ slightly from these
    with a different seed.
    """)
    return


@app.cell
def _():
    def bootstrap_ci(x, stat, n=2000, seed=385):
        """Return the 95% percentile bootstrap interval for stat(x) as (low, high)."""
        return None

    return (bootstrap_ci,)


@app.cell
def _(bootstrap_ci, np, salaries):
    salaries_2022 = salaries.loc[salaries["work_year"] == 2022, "salary_in_usd"].to_numpy()
    bootstrap_ci(salaries_2022, np.median)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Round 5, which we are not doing: base Python

    One round in ten was a LeetCode-style puzzle in base Python. That belongs to SI 345, and the
    point the interview made about it holds for every round today: interviewers listened for the
    logic, and forgave the syntax.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:25 · Application exercise 12

    ## The recruiter's slide

    This is the open-book round, so any tool is allowed, including an agent. A friend graduating
    next spring shows you a slide from a recruiter:

    > **"Data science pay is up 59% since 2020. There has never been a better time to join."**

    The cell below reproduces the slide's figure from the file.
    """)
    return


@app.cell
def _(salaries):
    by_year = salaries.groupby("work_year")["salary_in_usd"].agg(["count", "median", "mean"])
    print(by_year.round(0))
    print(f"median, 2020 to 2022: {by_year.loc[2022, 'median'] / by_year.loc[2020, 'median'] - 1:+.0%}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Part 1: eight minutes, on your own, in silence

    > **A friend graduating next spring shows you this slide. Is data science pay up 59% since
    > 2020, for someone like them?**

    Take a position, and write down which result would change your mind. Please do not talk to
    your team yet.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Part 2: with your team

    Argue to a decision.

    > **Is data science pay up 59% since 2020, for someone like your friend?**
    >
    > **A.** Yes, about 59%. The median rose from \$75,544 to \$120,000.
    >
    > **B.** Yes, by about 30%. The mean is the fairer summary, and it rose 30%.
    >
    > **C.** Up, but by about 20%. Most of the 59% is the file filling up with senior people;
    > comparing like with like on experience leaves a rise of about a fifth.
    >
    > **D.** Not shown. Once experience and US location are held fixed, the rise is about 7% and
    > the interval includes zero.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### A worked example: the year-only regression

    The cell below regresses log salary on year and turns the 2022 coefficient into a
    percentage. On a log scale, a coefficient `b` means a factor of `exp(b)`, so the rise is
    `exp(b) - 1`. This model compares everyone in 2022 with everyone in 2020 and controls for
    nothing.
    """)
    return


@app.cell
def _(np, salaries, smf):
    year_only = smf.ols("log_salary ~ C(work_year)", data=salaries).fit()
    _b = year_only.params["C(work_year)[T.2022]"]
    _low, _high = year_only.conf_int().loc["C(work_year)[T.2022]"]
    print(f"2022 vs 2020: {np.exp(_b) - 1:+.0%}, 95% CI [{np.exp(_low) - 1:+.0%}, {np.exp(_high) - 1:+.0%}]")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Your team's code

    Please write `pay_rise`, which takes a model formula and returns the 2022 rise over 2020 as a
    percentage, with its 95% interval. Then call it with the formula your answer rests on. If your
    answer is A or B, compute that summary directly instead.

    **Check it first.** `pay_rise("log_salary ~ C(work_year)")` should give +60% with an interval
    of [+32%, +94%], as the worked example does. The function returns `None` until you write it.
    """)
    return


@app.cell
def _():
    def pay_rise(formula):
        """Fit formula to salaries; return the 2022 vs 2020 rise and its 95% interval, as percentages."""
        return None

    return (pay_rise,)


@app.cell
def _(pay_rise):
    pay_rise("log_salary ~ C(work_year)")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Submitting

    **Submit on Canvas first**, to *AE 12: The recruiter's slide*. One person submits for the team,
    ideally a different person from last time, and includes, in this order, the team name, your
    letter, your code and its output pasted as code (Format → Code in the Canvas editor), your
    justification, and who is here today.

    The code and the justification are graded together. Please write three sentences:

    1. **Say which comparison answers your friend's question, and why.**
    2. **Say how uncertain your figure is.**
    3. **Say which result would have changed your answer.**

    **Then in Sli.do**, click your letter. Sli.do draws the histogram and is not graded.
    """)
    return


if __name__ == "__main__":
    app.run()
