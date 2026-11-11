# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 5: Missingness, outliers, and data quality as a judgement

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, September 16, 2026

    The reading for this session is van Buuren, *Flexible Imputation of Missing Data*, sections 1.1
    to 1.3, free at <https://stefvanbuuren.name/fimd/ch-introduction.html>, with McKinney,
    *Python for Data Analysis*, chapter 7, as review.

    ---

    ### Today you will be able to

    - Find where the blanks in a dataset are, and check whether they depend on other columns
    - Tell blanks that mean "not asked" or "does not apply" from blanks that hide an answer, and
      relate them to the reading's terms MCAR, MAR and MNAR
    - Show how each way of handling blanks changes an answer, and report a range when the blanks
      could go either way
    - Find implausible values, and decide what to do with them as a judgement you state

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Data, and where the blanks are | 5 |
    | Why a value is blank | 15 |
    | What the blanks do to an answer | 10 |
    | Implausible values | 5 |
    | Today's question, in teams | 25 |
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    import numpy as np
    import pandas as pd

    REMOTE = ("https://raw.githubusercontent.com/"
              "cteplovs/si385-fa2026-student/main/data/")


    def course_csv(name):
        """Read one of the course data files.

        The copy in the course folder is the one to prefer, and it is what you get if you are
        running this the documented way. The fallback to the public repository is there so that
        the notebook also runs on molab, provided you have a network.
        """
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_csv(local)
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as response:
            return pd.read_csv(BytesIO(response.read()))

    return course_csv, mo, np, pd


@app.cell(hide_code=True)
def code_on_its_own_note(mo):
    mo.md(r"""
    ### Sections headed *The code on its own*

    Each technique ends with a section headed *The code on its own*. The dropdowns, sliders and
    plots above it call code written for this notebook, which you will not have when you work on
    your own data. The code in those sections uses only pandas, starts from a data
    frame, and does the computation without any controls, so that you can copy it into your project
    or another notebook. Each code cell starts with a comment listing the imports it uses, and its
    variable names start with `_`, which keeps them local to the cell.
    """)
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## Data

    The file holds the 2014 Open Sourcing Mental Illness survey of people working in technology,
    1,259 responses with one row per respondent, published under CC BY-SA 4.0. We leave out the
    free-text comments. The columns
    used most today are these.

    | Column | Description |
    |---|---|
    | `Timestamp` | When the response was submitted |
    | `Age`, `Gender`, `Country`, `state` | About the respondent; `state` is for the United States |
    | `self_employed` | Whether the respondent is self-employed |
    | `treatment` | Whether they have sought treatment for a mental health condition |
    | `work_interfere` | "If you have a mental health condition, do you feel that it interferes with your work?": Never, Rarely, Sometimes or Often |
    | `family_history`, `no_employees`, `remote_work`, `tech_company` | Further questions about the respondent and their employer |
    """)
    return


@app.cell
def load_survey(course_csv):
    survey = course_csv("survey.csv").drop(columns=["comments"])
    survey.head()
    return (survey,)


@app.cell(hide_code=True)
def where_intro(mo):
    mo.md(r"""
    ---
    ## Where the blanks are

    The first step is to count the blanks in every column. The table lists the columns that have
    any, with their share of the 1,259 rows.
    """)
    return


@app.cell
def where_table(pd, survey):
    _blanks = pd.DataFrame({"blank": survey.isna().sum(),
                            "blank_pct": (100 * survey.isna().mean()).round(1)})
    _blanks[_blanks["blank"] > 0].sort_values("blank", ascending=False)
    return


@app.cell(hide_code=True)
def why_intro(mo):
    mo.md(r"""
    ---
    ## Why a value is blank

    A count of blanks says nothing about why they are there, and what can be done with them depends
    on the reason. The reading distinguishes three cases. Blanks are *missing completely at
    random* (MCAR) when whether a value is blank has nothing to do with the data, as when a page of
    forms is lost. They are *missing at random* (MAR) when whether a value is blank depends on other
    columns that were recorded, and *missing not at random* (MNAR) when it depends on the missing
    value itself, as when people with the highest incomes leave the income question blank. A fourth
    case matters as much in practice: a blank can mean that the question did not apply.

    The only evidence you have about the reason is how the blanks are spread across the rest of the
    data. Please choose a column with blanks and a column to split it by, and compare the share of
    blanks in each group.
    """)
    return


@app.cell
def why_controls(mo):
    # mo.ui.dropdown is a marimo function that makes a drop-down menu; its .value is the choice.
    blank_pick = mo.ui.dropdown(options=["work_interfere", "state", "self_employed"],
                                value="work_interfere", label="Blanks in")
    split_pick = mo.ui.dropdown(
        options=["treatment", "family_history", "In the United States", "Submitted in August 2014",
                 "no_employees", "remote_work", "tech_company"],
        value="treatment", label="Split by")
    # mo.hstack is a marimo function that puts outputs side by side.
    mo.hstack([blank_pick, split_pick], justify="start", gap=2)
    return blank_pick, split_pick


@app.cell
def define_split(survey):
    def split_column(name):
        """A column to split the respondents by, including two made from other columns."""
        if name == "In the United States":
            return survey["Country"].eq("United States").map({True: "US", False: "not US"})
        if name == "Submitted in August 2014":
            return survey["Timestamp"].str.startswith("2014-08").map(
                {True: "August 2014", False: "later"})
        return survey[name]

    return (split_column,)


@app.cell
def why_view(blank_pick, pd, split_column, split_pick, survey):
    _group = split_column(split_pick.value)
    pd.DataFrame({
        "respondents": survey.groupby(_group).size(),
        "blank": survey[blank_pick.value].isna().groupby(_group).sum(),
        "blank_pct": (100 * survey[blank_pick.value].isna().groupby(_group).mean()).round(1),
    })
    return


@app.cell(hide_code=True)
def why_reading(mo, survey):
    _wi = survey["work_interfere"].isna().groupby(survey["treatment"]).mean()
    _first = int(survey["self_employed"].isna().iloc[:18].sum())
    mo.md(f"""
    The three columns have three different kinds of blank. `state` is blank for almost everyone
    outside the United States, because the question did not apply to them, and those blanks are
    not missing information at all. `self_employed` is blank in {_first} rows, and they are the
    first {_first} responses in the file, which may mean that the question was added to the form
    after the survey opened; blanks that depend only on when someone responded are close to MCAR.

    `work_interfere` is the hard case. It is blank for **{_wi['No']:.0%}** of the respondents who
    have not sought treatment and **{_wi['Yes']:.1%}** of those who have, so the blanks depend on a
    recorded column, which is the reading's MAR. The question begins "If you have a mental health
    condition", so the most likely reading is that many people left it blank because they have no
    condition, but the data cannot show that, and some of them may have a condition they did not
    want to report, which would be MNAR. No column in the file can tell those two apart.
    """)
    return


@app.cell(hide_code=True)
def why_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we count the blanks in every column, and then compute the share of blanks in
    one column for each value of another, beside the number of rows in each group. To use it on
    other data, you would change the two columns.
    """)
    return


@app.cell
def why_code(pd, survey):
    # Uses: import pandas as pd
    print(survey.isna().sum().loc[lambda _counts: _counts > 0])
    print()
    _group = survey["treatment"]
    pd.DataFrame({"rows": survey.groupby(_group).size(),
                  "blank_pct": (100 * survey["work_interfere"].isna().groupby(_group).mean())
                  .round(1)})
    return


@app.cell(hide_code=True)
def effect_intro(mo):
    mo.md(r"""
    ---
    ## What the blanks do to an answer

    Consider one number: the share of respondents who say a mental health condition interferes with
    their work *often* or *sometimes*. Each common way of handling the blanks gives a different
    share. Leaving them out, which the reading calls *listwise deletion*, answers a question about
    the people who answered. Counting them as "no" assumes that every blank means no interference.
    Counting them as "yes" gives the highest share the blanks allow, and together the last two give
    the range within which the true share must lie, whatever the blanks mean. Please choose a way of
    handling the blanks and a group to split by.
    """)
    return


@app.cell
def effect_controls(mo):
    handling_pick = mo.ui.dropdown(
        options=["Left out", "Counted as no", "Counted as yes"], value="Left out",
        label="Blanks are")
    effect_split = mo.ui.dropdown(options=["Everyone", "treatment", "family_history",
                                           "remote_work", "no_employees"],
                                  value="Everyone", label="Split by")
    mo.hstack([handling_pick, effect_split], justify="start", gap=2)
    return effect_split, handling_pick


@app.cell
def define_share(np):
    def interferes_share(rows, handling):
        """Share saying Often or Sometimes, with the blanks handled one of three ways."""
        _yes = rows["work_interfere"].isin(["Often", "Sometimes"])
        _blank = rows["work_interfere"].isna()
        if handling == "Left out":
            return _yes[~_blank].mean()
        if handling == "Counted as no":
            return _yes.mean()
        return np.mean(_yes | _blank)

    return (interferes_share,)


@app.cell
def effect_view(effect_split, handling_pick, interferes_share, pd, survey):
    if effect_split.value == "Everyone":
        _groups = {"everyone": survey}
    else:
        _groups = dict(list(survey.groupby(effect_split.value)))
    pd.DataFrame({
        "respondents": {_g: len(_r) for _g, _r in _groups.items()},
        "blanks": {_g: int(_r["work_interfere"].isna().sum()) for _g, _r in _groups.items()},
        f"share, blanks {handling_pick.value.lower()}": {
            _g: round(interferes_share(_r, handling_pick.value), 3) for _g, _r in _groups.items()},
    })
    return


@app.cell(hide_code=True)
def effect_reading(interferes_share, mo, survey):
    _shares = {_h: interferes_share(survey, _h) for _h in ("Left out", "Counted as no",
                                                          "Counted as yes")}
    mo.md(f"""
    For everyone, the share is **{_shares['Left out']:.1%}** with the blanks left out and
    **{_shares['Counted as no']:.1%}** with them counted as no, and the two answer different
    questions: the first is about people who answered, and the second assumes that everyone who
    did not answer has no interference. With the blanks counted as yes it is
    **{_shares['Counted as yes']:.1%}**, so the data alone allow anything from
    {_shares['Counted as no']:.0%} to {_shares['Counted as yes']:.0%}. The split by `treatment`
    shows why the choice matters so much here: nearly all the blanks are among the people who have
    not sought treatment, so leaving them out changes the mix of people the share describes.

    The reading also warns against *mean imputation*, replacing each blank with the average of the
    answered values. It keeps the mean the same and makes the spread too small, because every filled
    value sits at the centre, and it weakens the relationships with other columns.
    """)
    return


@app.cell(hide_code=True)
def effect_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute one share three ways: with the blanks left out, counted as no and
    counted as yes, and then the same three for each group of another column.
    """)
    return


@app.cell
def effect_code(pd, survey):
    # Uses: import pandas as pd
    def _shares(rows):
        _yes = rows["work_interfere"].isin(["Often", "Sometimes"])
        _blank = rows["work_interfere"].isna()
        return pd.Series({"left out": _yes[~_blank].mean(), "counted as no": _yes.mean(),
                          "counted as yes": (_yes | _blank).mean(), "rows": len(rows)})

    print(_shares(survey).round(3))
    survey.groupby("treatment")[["work_interfere"]].apply(_shares).round(3)
    return


@app.cell(hide_code=True)
def implausible_intro(mo):
    mo.md(r"""
    ---
    ## Implausible values

    A value can be present and still wrong. Please move the slider to set the range of ages you
    would accept, and read the rows outside it before deciding what they are.
    """)
    return


@app.cell
def implausible_control(mo):
    # mo.ui.range_slider is a marimo function that makes a slider with two ends; its .value is a
    # pair of numbers.
    age_range = mo.ui.range_slider(start=0, stop=100, step=1, value=[16, 80],
                                   label="Plausible ages", show_value=True)
    age_range
    return (age_range,)


@app.cell
def implausible_view(age_range, mo, survey):
    _low, _high = age_range.value
    _outside = survey.loc[~survey["Age"].between(_low, _high), ["Age", "Country", "Gender"]]
    _inside = survey.loc[survey["Age"].between(_low, _high), "Age"]
    mo.vstack([
        mo.md(f"**{len(_outside)}** rows fall outside {_low} to {_high}. The mean age of every "
              f"row is **{survey['Age'].mean():,.0f}**, and of the rows inside the range "
              f"**{_inside.mean():.1f}**; the median is **{survey['Age'].median():.0f}** either "
              "way."),
        _outside,
    ])
    return


@app.cell(hide_code=True)
def implausible_reading(mo, survey):
    _genders = survey["Gender"].nunique()
    _cleaned = survey["Gender"].str.strip().str.lower().nunique()
    mo.md(f"""
    One age of 100 billion makes the mean of every row meaningless, while the median does not move,
    which is session 3's point about robust measures again. Ages such as 5 or 8 are probably typing
    errors, and ages such as 329 may be too, but the data cannot say what was meant, so the honest
    choices are to set those values to blank or leave the rows out, and to say which you did.

    The free-text `Gender` column shows a second kind of quality problem: it has **{_genders}**
    distinct values, and still **{_cleaned}** after removing spaces and capitals, because people
    wrote the same answer in different ways and some wrote answers that do not fit any category.
    Grouping those answers is a decision about people, which should be made deliberately and
    reported, not left to a quick replacement.
    """)
    return


@app.cell(hide_code=True)
def implausible_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we list the rows outside a plausible range, then make a copy of the column
    with those values set to blank, with `where`, so that the original values stay in the data, and
    count the distinct values of a free-text column before and after cleaning its spaces and
    capitals.
    """)
    return


@app.cell
def implausible_code(survey):
    print(survey.loc[~survey["Age"].between(16, 80), ["Age", "Country"]])
    _age_checked = survey["Age"].where(survey["Age"].between(16, 80))
    print(f"\nmean age, implausible values blank: {_age_checked.mean():.1f}, "
          f"blanks: {_age_checked.isna().sum()}")
    print("distinct Gender values:", survey["Gender"].nunique(),
          "after cleaning:", survey["Gender"].str.strip().str.lower().nunique())
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    A company that is planning support for its employees asks how common it is for a mental health
    condition to interfere with work.

    > **Use these data to say what share of the respondents report that a mental health condition
    > interferes with their work, and what the blanks do to that answer.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. The share for everyone, with the way you handled the blanks and the reason, and the range
       the blanks allow.
    2. The same share for the groups of one column, to say whether the answer differs between
       groups and whether the blanks fall evenly across them.
    3. One limitation: something about these data that the blanks keep you from knowing.

    Then compare your results with your teammates', who split the respondents by different
    columns, and say what their results showed that yours did not, and whether that changes your
    answer.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each
    prompt, in your own words and with the numbers from your own runs. Each of you should then
    upload your own copy of this notebook to *AE 3* on Canvas, by 23:59 on Thursday.

    | Part of your answer | Points |
    |---|---:|
    | Your answer: the share and its range, the groups, and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop rather than watching one
    screen, and split the respondents by a different column from your teammates, then compare
    what you find. Your team may agree on an answer, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholder in Step 1, run
    the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_choose():
    # Step 1: choose a column to split the respondents by, different from your teammates':
    # treatment, family_history, remote_work, no_employees, tech_company, benefits or
    # self_employed.
    answer_column = "SOME_COLUMN"
    return (answer_column,)


@app.cell
def step2_shares(answer_column, interferes_share, mo, pd, survey):
    # Step 2: the share three ways for each group of your column, with the number of blanks.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder value.
    mo.stop(answer_column == "SOME_COLUMN",
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md("Replace the placeholder in Step 1 with a column name.").callout(kind="info"))
    _groups = dict(list(survey.groupby(answer_column))) | {"everyone": survey}
    pd.DataFrame({
        "respondents": {_g: len(_r) for _g, _r in _groups.items()},
        "blanks": {_g: int(_r["work_interfere"].isna().sum()) for _g, _r in _groups.items()},
        **{f"blanks {_h.lower()}": {_g: round(interferes_share(_r, _h), 3)
                                    for _g, _r in _groups.items()}
           for _h in ("Left out", "Counted as no", "Counted as yes")},
    })
    return


@app.cell
def step3_answers(answer_column, mo, pd, survey):
    # Step 3: every answer to work_interfere, blanks included, for each group of your column, as
    # shares of the group.
    mo.stop(answer_column == "SOME_COLUMN")
    pd.crosstab(survey[answer_column], survey["work_interfere"].fillna("blank"),
                normalize="index").round(3)
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L05_missingness.py` to *AE 3* on Canvas by 23:59 on Thursday. We will cross-reference your
    claims about evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_share(mo):
    mo.md(r"""
    **The share for everyone, how you handled the blanks and why, and the range the blanks allow**
    """)
    return


@app.cell
def step4_answer_share(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_groups(mo):
    mo.md(r"""
    **How the share and the blanks differ between the groups of your column**
    """)
    return


@app.cell
def step4_answer_groups(mo):
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
