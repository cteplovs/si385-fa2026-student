# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
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

    ## Session 6: Conditioning, faceting, and finding structure without a model

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, September 21, 2026

    The reading for this session is Bruce et al., *AI-Assisted Statistics for Data Scientists*,
    chapter 1, the section *Exploring Two or More Variables*.

    ---

    ### Today you will be able to

    - Compare a numeric column across the groups of a categorical one, with counts beside every
      summary
    - Condition a comparison on a third column, and say whether the comparison holds within its
      groups
    - Explain how a difference between groups can come from the mix of a third column rather than
      from the groups themselves
    - Draw a faceted plot, with one panel for each group of a third column on shared axes

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Data | 5 |
    | A pooled comparison | 10 |
    | Conditioning on a third column | 15 |
    | Faceting | 10 |
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

    return course_parquet, mo, pd, plt


@app.cell(hide_code=True)
def code_on_its_own_note(mo):
    mo.md(r"""
    ### Sections headed *The code on its own*

    Each technique ends with a section headed *The code on its own*. The dropdowns and plots above
    it call code written for this notebook, which you will not have when you work on your own
    data. The code in those sections uses only pandas and matplotlib, starts from a data frame, and
    does the computation without any controls, so that you can copy it into your project or another
    notebook. Each code cell starts with a comment listing the imports it uses, and its variable
    names start with `_`, which keeps them local to the cell.
    """)
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## Data

    The data are session 3's: 607 data science salaries from 2020 to 2022, one row per job, which
    people reported about their own pay to a public salary survey. The column we compare across is
    `remote_ratio`, which is 0 for a job with no remote work, 50 for one that is partly remote and
    100 for one that is fully remote. After reading the file, we add the salary in thousands of
    dollars and a column that says whether the company is in the United States.
    """)
    return


@app.cell
def load_salaries(course_parquet):
    salaries = course_parquet("ds_salaries.parquet")
    salaries["salary_k"] = salaries["salary_in_usd"] / 1000
    salaries["company_in_us"] = salaries["company_location"].eq("US").map(
        {True: "US", False: "not US"})
    salaries[["work_year", "experience_level", "remote_ratio", "company_location",
              "company_in_us", "company_size", "salary_k"]].head()
    return (salaries,)


@app.cell(hide_code=True)
def pooled_intro(mo):
    mo.md(r"""
    ---
    ## A pooled comparison

    The first comparison pools everything else: every job with each amount of remote work,
    whatever its country, year, experience level or company. The reading's tools for a numeric
    column across the groups of a categorical one are a table of summaries and a boxplot, and the
    table should always give the number of jobs beside each median.
    """)
    return


@app.cell
def pooled_view(mo, plt, salaries):
    _table = salaries.groupby("remote_ratio")["salary_k"].agg(jobs="size", median="median").round(1)
    _groups = list(_table.index)
    _fig, _ax = plt.subplots(figsize=(6, 3.5))
    _ax.boxplot([salaries.loc[salaries["remote_ratio"] == _g, "salary_k"] for _g in _groups],
                tick_labels=[str(_g) for _g in _groups])
    _ax.set_xlabel("remote_ratio")
    _ax.set_ylabel("Salary (thousands of US dollars)")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    # mo.hstack is a marimo function that puts outputs side by side.
    mo.hstack([_table, _fig], justify="start", align="center", gap=2)
    return


@app.cell(hide_code=True)
def pooled_reading(mo, salaries):
    _medians = salaries.groupby("remote_ratio")["salary_k"].median()
    mo.md(f"""
    Pooled, the fully remote jobs have a median of **{_medians[100]:.0f}** thousand dollars and the
    jobs with no remote work **{_medians[0]:.0f}** thousand, a difference of
    **{_medians[100] - _medians[0]:.0f}** thousand. It is tempting to read that as what remote work
    pays, but the pooled comparison also compares everything else that differs between remote and
    office jobs, and the next section asks what that is.
    """)
    return


@app.cell(hide_code=True)
def pooled_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the number of rows and the median of a numeric column for each
    group of a categorical one, and draw a boxplot for each group.
    """)
    return


@app.cell
def pooled_code(plt, salaries):
    # Uses: import matplotlib.pyplot as plt
    print(salaries.groupby("remote_ratio")["salary_k"].agg(jobs="size", median="median"))
    _groups = sorted(salaries["remote_ratio"].unique())
    _fig, _ax = plt.subplots(figsize=(6, 3.5))
    _ax.boxplot([salaries.loc[salaries["remote_ratio"] == _g, "salary_k"] for _g in _groups],
                tick_labels=[str(_g) for _g in _groups])
    _fig
    return


@app.cell(hide_code=True)
def condition_intro(mo):
    mo.md(r"""
    ---
    ## Conditioning on a third column

    To *condition* on a column is to make the comparison separately within each of its groups, so
    that the groups being compared are alike in that column. If remote jobs pay more because they
    are remote, the difference should appear within each group of the third column too. If it
    appears only when the groups are pooled, it comes from the mix of the third column.

    Please choose a column to condition on. The first table gives the median salary for each
    combination, the second the number of jobs, and the third the share of each remote group that
    falls in each group of the third column.
    """)
    return


@app.cell
def condition_control(mo):
    # mo.ui.dropdown is a marimo function that makes a drop-down menu. Given a dictionary, it shows
    # the keys and its .value is the value of the chosen key.
    condition_pick = mo.ui.dropdown(
        options={"Company in the US": "company_in_us", "Year": "work_year",
                 "Experience level": "experience_level", "Company size": "company_size"},
        value="Company in the US", label="Condition on")
    condition_pick
    return (condition_pick,)


@app.cell
def condition_view(condition_pick, mo, pd, salaries):
    _by = condition_pick.value
    _median = salaries.pivot_table(index="remote_ratio", columns=_by, values="salary_k",
                                   aggfunc="median").round(1)
    _count = salaries.pivot_table(index="remote_ratio", columns=_by, values="salary_k",
                                  aggfunc="size")
    _mix = pd.crosstab(salaries["remote_ratio"], salaries[_by], normalize="index").round(2)
    # mo.vstack is a marimo function that stacks outputs one above the other.
    mo.vstack([mo.md("**Median salary, $k**"), _median, mo.md("**Jobs**"), _count,
               mo.md("**Share of each remote group in each group of the third column**"), _mix])
    return


@app.cell(hide_code=True)
def condition_reading(mo, pd, salaries):
    _m = salaries.pivot_table(index="remote_ratio", columns="company_in_us", values="salary_k",
                              aggfunc="median")
    _mix = pd.crosstab(salaries["remote_ratio"], salaries["company_in_us"], normalize="index")
    mo.md(f"""
    Conditioned on the company's country, the gap shrinks or reverses. Among US companies, fully
    remote jobs have a median **{_m.loc[100, 'US'] - _m.loc[0, 'US']:+.0f}** thousand dollars from
    jobs with no remote work, and among companies elsewhere the gap is
    **{_m.loc[100, 'not US'] - _m.loc[0, 'not US']:+.0f}** thousand. The pooled gap is larger than
    either because **{_mix.loc[100, 'US']:.0%}** of the fully remote jobs are at US companies,
    against **{_mix.loc[0, 'US']:.0%}** of the jobs with no remote work, and US companies pay far
    more. Much of the pooled difference therefore comes from where the jobs are rather than from
    whether they are remote, which is the pattern often called *Simpson's paradox* when the
    direction of a comparison reverses.

    The counts matter as much as the medians. Several cells have fewer than 20 jobs, and a median of
    a handful of salaries can move a long way if one job is added or removed, so a pattern that
    depends on those cells is weak evidence.
    """)
    return


@app.cell(hide_code=True)
def condition_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the median and the number of rows for each combination of the
    column we compare and the column we condition on, with `pivot_table`, and the share of each
    compared group in each group of the third column, with `pd.crosstab` and `normalize="index"`.
    To condition on something else, you would change `_condition`.
    """)
    return


@app.cell
def condition_code(pd, salaries):
    # Uses: import pandas as pd
    _condition = "company_in_us"
    print(salaries.pivot_table(index="remote_ratio", columns=_condition, values="salary_k",
                               aggfunc=["median", "size"]).round(1))
    print()
    print(pd.crosstab(salaries["remote_ratio"], salaries[_condition], normalize="index").round(2))
    return


@app.cell(hide_code=True)
def facet_intro(mo):
    mo.md(r"""
    ---
    ## Faceting

    A *faceted* plot, sometimes called small multiples, draws the same plot once for each group of a
    third column, side by side and on the same axes, so that the eye can compare the panels
    directly. Please choose a column to facet by. Sharing the axes is what makes the comparison
    fair, because a panel with its own scale can make a small difference look large.
    """)
    return


@app.cell
def facet_control(mo):
    facet_pick = mo.ui.dropdown(
        options={"Company in the US": "company_in_us", "Year": "work_year",
                 "Experience level": "experience_level", "Company size": "company_size"},
        value="Company in the US", label="Facet by")
    facet_pick
    return (facet_pick,)


@app.cell
def facet_plot(facet_pick, plt, salaries):
    _panels = sorted(salaries[facet_pick.value].unique())
    _fig, _axes = plt.subplots(1, len(_panels), figsize=(3 * len(_panels), 3.5), sharey=True,
                               squeeze=False)
    for _ax, _panel in zip(_axes[0], _panels):
        _rows = salaries[salaries[facet_pick.value] == _panel]
        _groups = sorted(_rows["remote_ratio"].unique())
        _ax.boxplot([_rows.loc[_rows["remote_ratio"] == _g, "salary_k"] for _g in _groups],
                    tick_labels=[str(_g) for _g in _groups])
        _ax.set_title(f"{_panel} ({len(_rows)} jobs)", fontsize=10)
        _ax.set_xlabel("remote_ratio")
        _ax.spines[["top", "right"]].set_visible(False)
    _axes[0][0].set_ylabel("Salary (thousands of US dollars)")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def facet_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we draw one boxplot panel for each group of a third column, with
    `sharey=True` so that every panel uses the same salary axis.
    """)
    return


@app.cell
def facet_code(plt, salaries):
    # Uses: import matplotlib.pyplot as plt
    _facet = "company_in_us"
    _panels = sorted(salaries[_facet].unique())
    _fig, _axes = plt.subplots(1, len(_panels), figsize=(3 * len(_panels), 3.5), sharey=True)
    for _ax, _panel in zip(_axes, _panels):
        _rows = salaries[salaries[_facet] == _panel]
        _groups = sorted(_rows["remote_ratio"].unique())
        _ax.boxplot([_rows.loc[_rows["remote_ratio"] == _g, "salary_k"] for _g in _groups],
                    tick_labels=[str(_g) for _g in _groups])
        _ax.set_title(str(_panel))
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    A friend who is choosing between two offers, one remote and one in an office, has read that
    remote data science jobs pay more.

    > **Use these data to say whether remote data science jobs pay more, and explain the difference
    > in the pooled comparison.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. The pooled comparison, with its counts.
    2. The comparison conditioned on the column you chose, with its counts and the mix of that
       column in each remote group, to say whether the difference holds within its groups.
    3. One limitation: something these data cannot tell your friend about their two offers.

    Then compare your results with your teammates', who conditioned on different columns, and say
    what their results showed that yours did not, and whether that changes your answer.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each
    prompt, in your own words and with the numbers from your own runs. Each of you should then
    upload your own copy of this notebook to *AE 4* on Canvas, by 23:59 on Tuesday.

    | Part of your answer | Points |
    |---|---:|
    | Your explanation: the pooled comparison, the conditioned one, and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop rather than watching one
    screen, and condition on a different column from your teammates, then compare what you find.
    Your team may agree on an explanation, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholder in Step 1, run
    the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_choose():
    # Step 1: choose a column to condition on, different from your teammates':
    # company_in_us, work_year, experience_level, company_size or employment_type.
    answer_column = "SOME_COLUMN"
    return (answer_column,)


@app.cell
def step2_condition(answer_column, mo, pd, salaries):
    # Step 2: the medians, the counts and the mix, conditioned on your column.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder value.
    mo.stop(answer_column == "SOME_COLUMN",
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md("Replace the placeholder in Step 1 with a column name.").callout(kind="info"))
    mo.vstack([
        salaries.pivot_table(index="remote_ratio", columns=answer_column, values="salary_k",
                             aggfunc=["median", "size"]).round(1),
        pd.crosstab(salaries["remote_ratio"], salaries[answer_column],
                    normalize="index").round(2),
    ])
    return


@app.cell
def step3_facets(answer_column, mo, plt, salaries):
    # Step 3: one panel for each group of your column, on a shared salary axis.
    mo.stop(answer_column == "SOME_COLUMN")
    _panels = sorted(salaries[answer_column].unique())
    _fig, _axes = plt.subplots(1, len(_panels), figsize=(3 * len(_panels), 3.5), sharey=True,
                               squeeze=False)
    for _ax, _panel in zip(_axes[0], _panels):
        _rows = salaries[salaries[answer_column] == _panel]
        _groups = sorted(_rows["remote_ratio"].unique())
        _ax.boxplot([_rows.loc[_rows["remote_ratio"] == _g, "salary_k"] for _g in _groups],
                    tick_labels=[str(_g) for _g in _groups])
        _ax.set_title(f"{_panel} ({len(_rows)} jobs)", fontsize=10)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L06_multivariate.py` to *AE 4* on Canvas by 23:59 on Tuesday. We will cross-reference your
    claims about evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_pooled(mo):
    mo.md(r"""
    **The pooled comparison, with its counts**
    """)
    return


@app.cell
def step4_answer_pooled(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_conditioned(mo):
    mo.md(r"""
    **The comparison conditioned on your column, and what explains the pooled difference**
    """)
    return


@app.cell
def step4_answer_conditioned(mo):
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
