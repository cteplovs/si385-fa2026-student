# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
#     "scipy>=1.13",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 3: Describing a distribution

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, September 9, 2026

    The reading for this session is Bruce et al., *AI-Assisted Statistics for Data Scientists*,
    chapter 1, through *Exploring the Data Distribution*.

    ---

    ### Today you will be able to

    - Say how the mean, the median and the trimmed mean respond to extreme values, and choose
      between them for a skewed distribution
    - Measure spread with the standard deviation, the interquartile range and the median absolute
      deviation, and say which of them a long tail inflates
    - Read the shape of a distribution from a histogram and a boxplot, and say how the choice of
      bins and scale changes what you see
    - Say what a summary licenses you to claim, and what it does not

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Data | 5 |
    | Centre | 10 |
    | Spread | 10 |
    | Shape | 10 |
    | What a summary licenses you to say | 5 |
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
    from scipy import stats

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

    return course_parquet, mo, np, pd, plt, stats


@app.cell(hide_code=True)
def code_on_its_own_note(mo):
    mo.md(r"""
    ### Sections headed *The code on its own*

    Each technique ends with a section headed *The code on its own*. The sliders, switches and
    plots above it call code written for this notebook, which you will not have when you work on
    your own data. The code in those sections uses only pandas, NumPy, matplotlib and SciPy, starts
    from a data frame, and does the computation without any controls, so that you can copy it into
    your project or another notebook. Each code cell starts with a comment listing the imports it
    uses, and its variable names start with `_`, which keeps them local to the cell.
    """)
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## Data

    The file holds 607 data science salaries from 2020 to 2022, one row per job, which people
    reported about their own pay to a public salary survey. Each salary was reported in its own
    currency and converted to US dollars.

    | Column | Description |
    |---|---|
    | `work_year` | The year the salary was paid |
    | `experience_level` | EN entry, MI mid, SE senior, EX executive |
    | `employment_type` | FT full time, PT part time, CT contract, FL freelance |
    | `job_title` | The title of the job |
    | `salary`, `salary_currency` | The salary in the currency it was paid in |
    | `salary_in_usd` | The salary converted to US dollars |
    | `employee_residence`, `company_location` | Countries, as two-letter codes |
    | `remote_ratio` | 0 for no remote work, 50 for partly remote, 100 for fully remote |
    | `company_size` | S, M or L |

    After reading the file, we add the salary in thousands of dollars, which is easier to read in
    tables and on axes.
    """)
    return


@app.cell
def load_salaries(course_parquet):
    salaries = course_parquet("ds_salaries.parquet")
    salaries["salary_k"] = salaries["salary_in_usd"] / 1000
    salaries.head()
    return (salaries,)


@app.cell(hide_code=True)
def centre_intro(mo):
    mo.md(r"""
    ---
    ## Centre

    The reading gives three common measures of where a distribution's centre lies. The *mean* adds
    every value and divides by the number of values, so every value pulls on it in proportion to its
    size. The *median* is the middle value once the values are sorted, so it depends only on which
    values are above and below the middle, not on how far above or below they are. The *trimmed
    mean* drops a share of the values at each end and averages the rest, which sits between the two.

    Please move the first slider to add one more salary to the 607 and watch how each measure
    responds, then move the second to change how much the trimmed mean drops at each end.
    """)
    return


@app.cell
def centre_controls(mo):
    # mo.ui.slider is a marimo function that makes a slider; its .value is the chosen setting.
    added_salary = mo.ui.slider(start=0, stop=5000, step=50, value=0,
                                label="Add one salary of (thousands of dollars)",
                                show_value=True)
    trim_share = mo.ui.slider(start=0.0, stop=0.25, step=0.05, value=0.1,
                              label="Trimmed mean: share dropped at each end", show_value=True)
    # mo.vstack is a marimo function that stacks outputs one above the other.
    mo.vstack([added_salary, trim_share])
    return added_salary, trim_share


@app.cell
def centre_view(added_salary, mo, pd, salaries, stats, trim_share):
    _values = salaries["salary_k"]
    if added_salary.value > 0:
        _values = pd.concat([_values, pd.Series([float(added_salary.value)])],
                            ignore_index=True)
    _mean, _median = _values.mean(), _values.median()
    _trimmed = stats.trim_mean(_values, trim_share.value)
    # mo.hstack is a marimo function that puts outputs side by side, and mo.stat shows one number
    # with a label.
    mo.hstack([
        mo.stat(value=f"{len(_values)}", label="Salaries"),
        mo.stat(value=f"{_mean:.1f}", label="Mean, $k"),
        mo.stat(value=f"{_median:.1f}", label="Median, $k"),
        mo.stat(value=f"{_trimmed:.1f}", label=f"Trimmed mean ({trim_share.value:.0%}), $k"),
    ], justify="start", gap=2)
    return


@app.cell(hide_code=True)
def centre_reading(mo, salaries):
    _above = (salaries["salary_k"] > salaries["salary_k"].mean()).mean()
    mo.md(f"""
    Even without an added salary, the mean is above the median, because the salaries have a long
    tail to the right: a few very high salaries pull the mean up and leave the median where it is.
    Only **{_above:.0%}** of the 607 salaries are above the mean, so "the average salary" describes
    a salary that most of these jobs do not reach. Adding a single salary of five million dollars
    moves the mean by several thousand dollars and the median hardly at all, which is what the
    reading means by calling the median a *robust* estimate.
    """)
    return


@app.cell(hide_code=True)
def practice_centre_intro(mo):
    mo.md(r"""
    ### Practice: the share below the median

    Please replace `None` in the cell below with the share of salaries below the median, computed
    from `salaries["salary_k"]`, and compare it with the share below the mean. One of the two
    shares is close to one half for every distribution, and the other depends on the shape.
    """)
    return


@app.cell
def practice_centre():
    my_share_below_median = None
    my_share_below_median
    return


@app.cell(hide_code=True)
def centre_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the mean, the median and a 10% trimmed mean of one column with
    pandas and `stats.trim_mean`. To use it on other data, you would change the column.
    """)
    return


@app.cell
def centre_code(salaries, stats):
    # Uses: from scipy import stats
    _values = salaries["salary_k"]
    print(f"mean {_values.mean():.1f}")
    print(f"median {_values.median():.1f}")
    print(f"10% trimmed mean {stats.trim_mean(_values, 0.1):.1f}")
    return


@app.cell(hide_code=True)
def spread_intro(mo):
    mo.md(r"""
    ---
    ## Spread

    The reading's measures of spread follow the same pattern as the measures of centre. The
    *standard deviation* is built from squared deviations from the mean, so a value far from the
    mean counts for a great deal. The *interquartile range* (IQR) is the distance between the 25th
    and 75th percentiles, which depends only on the middle half of the values. The *median absolute
    deviation* (MAD) is the median of each value's distance from the median.

    Please turn the switch on to leave out the highest 1% of the salaries, seven jobs, and see which
    measures change.
    """)
    return


@app.cell
def spread_control(mo):
    # mo.ui.switch is a marimo function that makes an on-off switch.
    drop_top = mo.ui.switch(value=False, label="Leave out the highest 1%")
    drop_top
    return (drop_top,)


@app.cell
def spread_view(drop_top, mo, pd, salaries):
    _values = salaries["salary_k"]
    if drop_top.value:
        _values = _values[_values < _values.quantile(0.99)]
    _q1, _q3 = _values.quantile([0.25, 0.75])
    mo.vstack([
        mo.hstack([
            mo.stat(value=f"{len(_values)}", label="Salaries"),
            mo.stat(value=f"{_values.std():.1f}", label="Standard deviation, $k"),
            mo.stat(value=f"{_q3 - _q1:.1f}", label="IQR, $k"),
            mo.stat(value=f"{(_values - _values.median()).abs().median():.1f}",
                    label="MAD, $k"),
        ], justify="start", gap=2),
        pd.DataFrame({"percentile": [5, 25, 50, 75, 95, 99],
                      "salary, $k": _values.quantile([0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
                      .round(1).to_numpy()}).set_index("percentile").T,
    ])
    return


@app.cell(hide_code=True)
def spread_reading(mo):
    mo.md(r"""
    Seven salaries out of 607 move the standard deviation by much more than they move the IQR or the
    MAD. A standard deviation is still the right measure when the values are roughly symmetric,
    because much of later statistics is built on it, but for a distribution with a long tail the
    percentiles describe the spread that most of the jobs show. The table of percentiles is often
    the most useful summary of all, because it shows the spread at both ends without forcing it into
    one number.
    """)
    return


@app.cell(hide_code=True)
def spread_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the standard deviation, a set of percentiles, the IQR and the
    MAD of one column.
    """)
    return


@app.cell
def spread_code(salaries):
    _values = salaries["salary_k"]
    _q1, _q3 = _values.quantile([0.25, 0.75])
    print(f"standard deviation {_values.std():.1f}")
    print(f"IQR {_q3 - _q1:.1f}")
    print(f"MAD {(_values - _values.median()).abs().median():.1f}")
    print()
    print(_values.quantile([0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).round(1))
    return


@app.cell(hide_code=True)
def shape_intro(mo):
    mo.md(r"""
    ---
    ## Shape

    A histogram counts the values in bins of equal width, and its shape depends on the bins you
    choose: too few hide detail, and too many make every small gap look like a feature. A boxplot
    draws the quartiles as a box and the median as a line inside it, with whiskers out to the
    furthest values within 1.5 IQRs of the box and every value beyond them as a separate point.

    Please move the slider to change the number of bins, and turn the switch on to put the salaries
    on a log scale, where equal distances stand for equal ratios rather than equal differences.
    """)
    return


@app.cell
def shape_controls(mo):
    bin_count = mo.ui.slider(start=5, stop=120, step=5, value=40, label="Bins", show_value=True)
    log_scale = mo.ui.switch(value=False, label="Log scale")
    mo.hstack([bin_count, log_scale], justify="start", gap=3)
    return bin_count, log_scale


@app.cell
def shape_plot(bin_count, log_scale, np, plt, salaries):
    _values = salaries["salary_k"]
    _bins = (np.geomspace(_values.min(), _values.max(), bin_count.value + 1) if log_scale.value
             else bin_count.value)
    _fig, (_hist, _box) = plt.subplots(2, 1, figsize=(8, 4.5), sharex=True,
                                       gridspec_kw={"height_ratios": [3, 1]})
    _hist.hist(_values, bins=_bins, color="#1f4e79", edgecolor="white")
    _hist.axvline(_values.median(), color="#c2410c", linewidth=2, label="median")
    _hist.axvline(_values.mean(), color="#e69f00", linewidth=2, label="mean")
    _hist.set_ylabel("Jobs")
    _hist.legend(frameon=False)
    _box.boxplot(_values, vert=False, widths=0.6)
    _box.set_yticks([])
    _box.set_xlabel("Salary (thousands of US dollars)")
    if log_scale.value:
        _hist.set_xscale("log")
    for _ax in (_hist, _box):
        _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def shape_reading(mo):
    mo.md(r"""
    On the dollar scale, the salaries pile up below 200 thousand with a tail that runs to 600
    thousand, and the boxplot marks the tail's values as separate points. On the log scale, the
    same values look far more symmetric, with a few very low salaries now standing out on the left.
    Both pictures are of the same data. The dollar scale shows the differences in pay that a person
    would notice, and the log scale shows which salaries are unusual in proportion to the rest.
    """)
    return


@app.cell(hide_code=True)
def shape_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we draw a histogram with the mean and the median marked, then a boxplot for
    each value of a grouping column, on a log scale.
    """)
    return


@app.cell
def shape_code(plt, salaries):
    # Uses: import matplotlib.pyplot as plt
    _values = salaries["salary_k"]
    _fig, (_left, _right) = plt.subplots(1, 2, figsize=(10, 3.5))
    _left.hist(_values, bins=40, color="#1f4e79", edgecolor="white")
    _left.axvline(_values.median(), color="#c2410c", label="median")
    _left.axvline(_values.mean(), color="#e69f00", label="mean")
    _left.legend()
    _groups = sorted(salaries["experience_level"].unique())
    _right.boxplot([salaries.loc[salaries["experience_level"] == _g, "salary_k"]
                    for _g in _groups], tick_labels=_groups)
    _right.set_yscale("log")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def licence_intro(mo):
    mo.md(r"""
    ---
    ## What a summary licenses you to say

    A summary is a claim about the data, and each one supports a different sentence. "Half of these
    jobs pay more than the median" is true of any distribution. "A typical job pays about the
    median" is reasonable for a skewed one. "The average job pays the mean" is true as arithmetic,
    but for these data it describes a salary most jobs do not reach. None of the three says anything
    about data science jobs in general: these are 607 salaries that people chose to report to one
    website, many of them converted from other currencies, so any sentence about them should say
    which jobs it describes.

    The table below gives the count, the median and the IQR for each value of one column. Please
    choose a column and read the counts before the medians.
    """)
    return


@app.cell
def licence_control(mo):
    # mo.ui.dropdown is a marimo function that makes a drop-down menu. Given a dictionary, it shows
    # the keys and its .value is the value of the chosen key.
    group_pick = mo.ui.dropdown(
        options={"Experience level": "experience_level", "Year": "work_year",
                 "Company size": "company_size", "Remote work": "remote_ratio",
                 "Employment type": "employment_type"},
        value="Experience level", label="Group by")
    group_pick
    return (group_pick,)


@app.cell
def define_summary():
    def summary(data, column):
        """Count, median, quartiles and IQR of salary_k for each value of a column."""
        _grouped = data.groupby(column)["salary_k"]
        _table = _grouped.agg(jobs="count", median="median",
                              q1=lambda _v: _v.quantile(0.25), q3=lambda _v: _v.quantile(0.75))
        return _table.assign(IQR=_table["q3"] - _table["q1"]).round(1)

    return (summary,)


@app.cell
def licence_view(group_pick, salaries, summary):
    summary(salaries, group_pick.value)
    return


@app.cell(hide_code=True)
def licence_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the count, the median and the IQR of one column for each value of
    another, with `groupby` and `agg`. To use it on other data, you would change the two columns.
    """)
    return


@app.cell
def licence_code(salaries):
    _grouped = salaries.groupby("experience_level")["salary_k"]
    _table = _grouped.agg(jobs="count", median="median",
                          q1=lambda _v: _v.quantile(0.25), q3=lambda _v: _v.quantile(0.75))
    _table.assign(IQR=_table["q3"] - _table["q1"]).round(1)
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    A student who is about to graduate asks what a data science job pays.

    > **Use these data to describe a typical salary and how much salaries vary, and say for which
    > groups of jobs the answer is different.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. A measure of centre and a measure of spread for all 607 salaries, and the reason you chose
       those measures for this distribution.
    2. The same measures for the groups of one column, with their counts, to say which groups
       differ and by how much.
    3. One limitation: something about these data that limits what your answer can tell the
       student.

    Then compare your results with your teammates', who started from different columns, and say
    what their results showed that yours did not, and whether that changes your answer.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each
    prompt, in your own words and with the numbers from your own runs. Each of you should then
    upload your own copy of this notebook to *AE 1* on Canvas, by 23:59 on Thursday.

    | Part of your answer | Points |
    |---|---:|
    | Your description: centre and spread, the groups that differ, and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop rather than watching one
    screen, and start from a different column from your teammates, then compare what you find.
    Your team may agree on an answer, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholder in Step 1, run
    the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_choose():
    # Step 1: choose a column to group by, different from the one your teammates choose:
    # experience_level, work_year, company_size, remote_ratio, employment_type or
    # employee_residence. You may also set a minimum number of jobs for a group to be shown.
    answer_column = "SOME_COLUMN"
    answer_min_jobs = 10
    return answer_column, answer_min_jobs


@app.cell
def step2_summary(answer_column, answer_min_jobs, mo, salaries, summary):
    # Step 2: the count, median and IQR for each group of your column.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder value.
    mo.stop(answer_column == "SOME_COLUMN",
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md("Replace the placeholder in Step 1 with a column name.").callout(kind="info"))
    answer_table = summary(salaries, answer_column)
    answer_table = answer_table[answer_table["jobs"] >= answer_min_jobs]
    answer_table
    return (answer_table,)


@app.cell
def step3_boxplots(answer_column, answer_table, plt, salaries):
    # Step 3: a boxplot for each group in Step 2, on a log scale. Try it without the log scale too.
    _groups = list(answer_table.index)
    _fig, _ax = plt.subplots(figsize=(8, 0.5 * len(_groups) + 1.5))
    _ax.boxplot([salaries.loc[salaries[answer_column] == _g, "salary_k"] for _g in _groups],
                vert=False, tick_labels=[str(_g) for _g in _groups])
    _ax.set_xscale("log")
    _ax.set_xlabel("Salary (thousands of US dollars)")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L03_describing_distributions.py` to *AE 1* on Canvas by 23:59 on Thursday. We will
    cross-reference your claims about evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_overall(mo):
    mo.md(r"""
    **A typical salary and how much salaries vary, and why you chose those measures**
    """)
    return


@app.cell
def step4_answer_overall(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_groups(mo):
    mo.md(r"""
    **The groups of jobs for which the answer is different, and by how much**
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
