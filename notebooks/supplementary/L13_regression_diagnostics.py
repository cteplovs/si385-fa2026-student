# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "scipy>=1.13",
#     "statsmodels>=0.14",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 13: Regression diagnostics

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, October 14, 2026

    **Reading due today:** Bruce et al., *AI-Assisted Statistics for Data Scientists*, ch. 4,
    § *Regression Diagnostics*

    ---

    ### Today you will be able to

    - Read a plot of residuals against fitted values, and say what a fan or a curve in it means
    - Tell an outlier from a point with high leverage, and both from an influential point, using
      standardized residuals, hat-values and Cook's distance
    - Say which rows a rule of thumb for influence flags, and why a flag does not settle what to do
      with a row
    - Say how well a model describes most of the data, and where it does not

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Data, and a regression of salary | 10 |
    | Residuals | 15 |
    | Outliers, leverage and influence | 15 |
    | Rules of thumb | 5 |
    | Today's question, in teams | 15 |
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
    import statsmodels.formula.api as smf
    from scipy import stats

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

    return course_csv, mo, np, pd, plt, smf, stats


@app.cell(hide_code=True)
def code_on_its_own_note(mo):
    mo.md(r"""
    ### Sections headed *The code on its own*

    Each technique ends with a section headed *The code on its own*. The controls and plots above it
    call functions written for this notebook, which you will not have when you work on your own
    data. The code in those sections uses only pandas, NumPy, matplotlib, SciPy and statsmodels,
    starts from a data frame, and does the computation without any controls, so that you can copy it
    into your project or another notebook. Each code cell starts with a comment listing the imports
    it uses, and its variable names start with `_`, which keeps them local to the cell.
    """)
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## Data

    The file holds 607 salaries for data science jobs from 2020 to 2022, collected by the job board
    ai-jobs.net from people who reported their own pay. Each row is one person's job. It is the file
    whose salaries you described in session 3.

    | Column | Description |
    |---|---|
    | `work_year` | The year the salary was paid |
    | `experience_level` | EN entry, MI mid-level, SE senior, EX executive |
    | `job_title` | The job's title, as reported |
    | `salary_in_usd` | The salary, converted to US dollars: the value to explain |
    | `employee_residence`, `company_location` | Where the person lives and where the employer is |
    | `remote_ratio` | 0, 50 or 100: the share of the work done remotely |
    | `company_size` | S fewer than 50 employees, M 50 to 250, L more than 250 |

    After reading the file, we add four columns: the salary in thousands of dollars, its logarithm, readable
    names for the experience levels and company sizes, and whether the employer is in the United
    States.
    """)
    return


@app.cell
def load_salaries(course_csv, np):
    salaries = course_csv("ds_salaries.csv").drop(columns="Unnamed: 0", errors="ignore")
    salaries["salary_k"] = salaries["salary_in_usd"] / 1000
    salaries["log_salary"] = np.log(salaries["salary_in_usd"])
    salaries["experience"] = salaries["experience_level"].map(
        {"EN": "1 Entry", "MI": "2 Mid", "SE": "3 Senior", "EX": "4 Executive"})
    salaries["size"] = salaries["company_size"].map({"S": "Small", "M": "Medium", "L": "Large"})
    salaries["us_company"] = (salaries["company_location"] == "US").astype(int)
    salaries[["job_title", "experience", "company_location", "us_company", "size",
              "salary_k"]].head()
    return (salaries,)


@app.cell
def salary_histogram(plt, salaries):
    _fig, _ax = plt.subplots(figsize=(7, 3))
    _ax.hist(salaries["salary_k"], bins=50, color="#1f4e79")
    _ax.set_xlabel("Salary (thousands of US dollars)")
    _ax.set_ylabel("People")
    _ax.set_title("607 data science salaries: most below $200k, a long tail above")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def model_intro(mo):
    mo.md(r"""
    ---
    ## A regression of salary

    Consider a regression of salary on experience, whether the employer is in the United States, and
    the size of the employer. Experience and size are categories, so statsmodels makes one 0/1 column
    for each level except the first, and each coefficient is the difference from that first level:
    from an entry-level job for experience, and from a large employer for size. The formula's `C()`
    marks a column as a category.

    You can fit the model to the salary in thousands of dollars, as session 12 would, or to its
    logarithm. On the log scale, a coefficient of 0.1 means about 10% higher pay, so each coefficient
    is a proportional difference rather than a difference in dollars. Please keep the dollar scale
    for now; you will return to this choice.
    """)
    return


@app.cell
def scale_control(mo):
    # mo.ui.radio is a marimo function that makes a set of buttons, of which one can be chosen.
    # Given a dictionary, it shows the keys and its .value is the value of the chosen key.
    scale_pick = mo.ui.radio(
        options={"Thousands of dollars": "salary_k", "Log of dollars": "log_salary"},
        value="Thousands of dollars", label="Fit the salary in", inline=True)
    scale_pick
    return (scale_pick,)


@app.cell
def define_model(pd, smf):
    PREDICTORS = "C(experience) + us_company + C(size)"


    def fit(outcome, data, predictors=PREDICTORS):
        """Fit the outcome on the predictors by ordinary least squares."""
        return smf.ols(f"{outcome} ~ {predictors}", data=data).fit()


    def diagnostics(fitted, data):
        """Each row's fitted value, residual, standardized residual, hat-value and Cook's
        distance, alongside the columns that describe the job."""
        _influence = fitted.get_influence()
        _columns = ["job_title", "experience", "company_location", "size", "salary_k"]
        return data[_columns].assign(
            row=data.index,
            fitted=fitted.fittedvalues,
            residual=fitted.resid,
            standardized=_influence.resid_studentized_internal,
            hat=_influence.hat_matrix_diag,
            cooks=_influence.cooks_distance[0],
        )


    def thresholds(fitted):
        """The reading's rules of thumb, with P the number of predictor columns."""
        _n, _p = int(fitted.nobs), int(fitted.df_model)
        return {"n": _n, "P": _p, "cooks": 4 / (_n - _p - 1), "hat": 2 * (_p + 1) / _n}


    def coefficient_table(fitted):
        """Coefficients with their 95% intervals."""
        _intervals = fitted.conf_int()
        return pd.DataFrame({"coefficient": fitted.params, "low": _intervals[0],
                             "high": _intervals[1]}).round(3)


    return PREDICTORS, coefficient_table, diagnostics, fit, thresholds


@app.cell
def fit_main(coefficient_table, diagnostics, fit, mo, salaries, scale_pick):
    main_model = fit(scale_pick.value, salaries)
    main_diagnostics = diagnostics(main_model, salaries)
    # mo.vstack is a marimo function that stacks outputs one above the other.
    mo.vstack([mo.md(f"R² = **{main_model.rsquared:.3f}**"), coefficient_table(main_model)])
    return main_diagnostics, main_model


@app.cell(hide_code=True)
def fit_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we fit salary in thousands of dollars on experience and company size as
    categories, with `C()`, and on a column that is 1 for a US company and 0 otherwise, and print
    the coefficients with their 95% intervals. Then we fit the log of salary on the same predictors
    and turn each coefficient into a percentage difference with `exp(b) - 1`. Each category's
    coefficient is measured from the first category in alphabetical order, here `1 Entry` and
    `Large`.
    """)
    return


@app.cell
def fit_code(np, pd, salaries, smf):
    # Uses: import numpy as np
    #       import pandas as pd
    #       import statsmodels.formula.api as smf
    _predictors = "C(experience) + us_company + C(size)"
    _model = smf.ols(f"salary_k ~ {_predictors}", data=salaries).fit()
    print(pd.DataFrame({"coefficient": _model.params,
                        "low": _model.conf_int()[0], "high": _model.conf_int()[1]}).round(1))
    print("R²:", round(_model.rsquared, 3))
    print()
    _log_model = smf.ols(f"np.log(salary_in_usd) ~ {_predictors}", data=salaries).fit()
    (np.exp(_log_model.params.drop("Intercept")) - 1).mul(100).round(0).rename("% difference")
    return


@app.cell(hide_code=True)
def residuals_intro(mo):
    mo.md(r"""
    ---
    ## Residuals

    A regression's coefficients and R² summarize the data, but they are no evidence that a
    straight-line model with these predictors suits it, and the residuals are. Each residual is a
    person's actual salary minus the model's prediction, and if the model suits the data, the
    residuals look like random noise: centred on zero for every fitted value, with about the same
    spread everywhere, and with no curve.

    The left plot shows each residual against its fitted value. The predictors are all categories,
    so the fitted values fall in columns, one for each combination of experience, location and size.
    The right plot compares the residuals with a normal distribution: if they were normal, the points
    would lie on the line.
    """)
    return


@app.cell
def residual_plots(main_diagnostics, main_model, mo, np, pd, plt, scale_pick, stats):
    _units = "thousands of dollars" if scale_pick.value == "salary_k" else "log of dollars"
    _fig, (_left, _right) = plt.subplots(1, 2, figsize=(11, 4))
    _jitter = np.random.default_rng(385).normal(0, main_diagnostics["fitted"].std() * 0.01,
                                                len(main_diagnostics))
    _left.scatter(main_diagnostics["fitted"] + _jitter, main_diagnostics["residual"], s=10,
                  alpha=0.5, color="#1f4e79")
    _left.axhline(0, color="#111827", linewidth=1)
    _left.set_xlabel(f"Fitted value ({_units})")
    _left.set_ylabel("Residual")
    _left.set_title("Residuals against fitted values")
    stats.probplot(main_diagnostics["standardized"], dist="norm", plot=_right)
    _right.get_lines()[0].set_markersize(3)
    _right.set_title("Standardized residuals against a normal distribution")
    for _ax in (_left, _right):
        _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()

    _thirds = pd.qcut(main_diagnostics["fitted"].rank(method="first"), 3,
                      labels=["lowest third", "middle third", "highest third"])
    _spread = main_diagnostics.groupby(_thirds, observed=True)["residual"].std()
    mo.vstack([_fig, mo.md(
        f"Standard deviation of the residuals, by fitted value ({_units}, R² "
        f"{main_model.rsquared:.3f}): "
        + ", ".join(f"{_name} **{_value:.2f}**" for _name, _value in _spread.items()) + ".")])
    return


@app.cell(hide_code=True)
def residuals_reading(mo):
    mo.md(r"""
    On the dollar scale, the residuals fan out: the jobs the model predicts to pay most are also the
    ones it predicts least precisely, and the standard deviations under the plot show how much more
    spread out the residuals are above the lowest third. The reading calls this *heteroskedasticity*, unequal spread. The coefficients are
    still the best straight-line summary, but the confidence intervals and p-values in the table
    assume equal spread, so they are too narrow for some comparisons and too wide for others. A
    single interval for "what a senior data scientist earns" would be too wide for some people and
    too narrow for others. The long upper tail also shows in the right plot, where the points bend
    away from the line at the top.

    Please switch the scale to the log of dollars and look again. The fan at the top end closes,
    and the coefficients become percentages, which is how pay differences are usually described.
    The spread at the low end grows instead, because a few very low salaries (a few thousand dollars
    a year) are far below the rest in proportional terms. Neither scale makes the residuals perfectly
    even, so the choice is a judgement about which comparisons matter more, and it is one you should
    state rather than make silently.
    """)
    return


@app.cell(hide_code=True)
def residuals_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we fit the model and draw the two plots from this section: the residuals
    against the fitted values, where a fan shape shows unequal spread, and the standardized
    residuals against a normal distribution with `stats.probplot`, where points that bend away from
    the line show a long tail.
    """)
    return


@app.cell
def residuals_code(plt, salaries, smf, stats):
    # Uses: import matplotlib.pyplot as plt
    #       import statsmodels.formula.api as smf
    #       from scipy import stats
    _model = smf.ols("salary_k ~ C(experience) + us_company + C(size)", data=salaries).fit()
    _fig, (_left, _right) = plt.subplots(1, 2, figsize=(10, 4))
    _left.scatter(_model.fittedvalues, _model.resid, s=10, alpha=0.5)
    _left.axhline(0, color="black", linewidth=1)
    _left.set_xlabel("fitted value")
    _left.set_ylabel("residual")
    stats.probplot(_model.get_influence().resid_studentized_internal, dist="norm", plot=_right)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def influence_intro(mo):
    mo.md(r"""
    ---
    ## Outliers, leverage and influence

    The reading distinguishes three properties of a single row:

    - An *outlier* is far from the model's prediction. Its **standardized residual**, the residual
      divided by its estimated standard deviation, is large; beyond about ±2.5 is a common flag.
    - A point with high *leverage* has unusual predictor values, so the fitted model passes close to
      it. Its **hat-value** is large. With predictors that are categories, leverage is high for the
      members of small groups: the model has little else to fit those groups' averages to.
    - An *influential* point is one whose removal would change the model substantially. **Cook's
      distance** measures how much all the fitted values would move if that row were left out, and it
      is large only when a row is both an outlier and has some leverage.

    The figure plots every row's hat-value against its standardized residual, with the size of each
    point proportional to its Cook's distance. The dashed lines are the reading's rules of thumb: a
    hat-value above 2(P + 1)/n, where P is the number of predictor columns, and a standardized
    residual beyond ±2.5.
    """)
    return


@app.cell
def influence_plot(main_diagnostics, main_model, mo, plt, thresholds):
    _rules = thresholds(main_model)
    _fig, _ax = plt.subplots(figsize=(8, 4.5))
    _ax.scatter(main_diagnostics["hat"], main_diagnostics["standardized"],
                s=10 + 4000 * main_diagnostics["cooks"], alpha=0.4, color="#1f4e79",
                edgecolor="white")
    _ax.axvline(_rules["hat"], color="#c2410c", linestyle="--", linewidth=1)
    for _level in (-2.5, 2.5):
        _ax.axhline(_level, color="#c2410c", linestyle="--", linewidth=1)
    _ax.set_xlabel("Hat-value (leverage)")
    _ax.set_ylabel("Standardized residual")
    _ax.set_title("Each person's job; larger points have larger Cook's distance")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    mo.vstack([_fig, mo.md(
        f"n = {_rules['n']}, P = {_rules['P']}: the leverage rule is 2(P + 1)/n = "
        f"**{_rules['hat']:.3f}**, and the influence rule is 4/(n − P − 1) = "
        f"**{_rules['cooks']:.4f}**.")])
    return


@app.cell(hide_code=True)
def drop_intro(mo):
    mo.md(r"""
    ### Leaving rows out

    The table lists the twenty rows with the largest Cook's distance. Please select a few rows by
    ticking them, and compare the coefficients fitted without them with the coefficients fitted to
    every row. A row is influential if leaving it out moves the coefficients you care about by more
    than you would accept.
    """)
    return


@app.cell
def drop_table(main_diagnostics, mo):
    # mo.ui.table is a marimo function that shows a table whose rows can be selected; its .value
    # holds the selected rows.
    drop_pick = mo.ui.table(
        main_diagnostics.sort_values("cooks", ascending=False).head(20).round(3),
        selection="multi", label="Rows to leave out")
    drop_pick
    return (drop_pick,)


@app.cell
def drop_view(coefficient_table, drop_pick, fit, main_model, mo, salaries, scale_pick):
    _dropped = list(drop_pick.value["row"]) if len(drop_pick.value) else []
    _without = fit(scale_pick.value, salaries.drop(index=_dropped))
    _both = coefficient_table(main_model)[["coefficient"]].rename(
        columns={"coefficient": "every row"})
    _both[f"without {len(_dropped)} row(s)"] = coefficient_table(_without)["coefficient"]
    _both["change"] = (_both.iloc[:, 1] - _both.iloc[:, 0]).round(3)
    _both
    return


@app.cell(hide_code=True)
def rules_intro(mo):
    mo.md(r"""
    ---
    ## Rules of thumb

    The reading's rule for high influence, a Cook's distance above 4/(n − P − 1), is a flag for a row
    that is worth a look, and whether to keep the row is a separate judgement. A row may be influential because
    it is a mistake (a salary typed in the wrong currency), because it belongs to a different
    population from the rest (a part-time contract among full-time jobs), or because it is a genuine
    part of the pattern that the model describes poorly, and only the first two are reasons to
    remove it. Removing every flagged row because it is flagged makes the model fit the remaining
    rows better by construction, and a better fit to the rows that are left is no evidence that it
    describes the jobs better.

    Please move the slider to change the cutoff, as a multiple of the rule of thumb, and see how many
    rows are flagged and what removing all of them would do to the coefficients.
    """)
    return


@app.cell
def rule_control(mo):
    # mo.ui.slider is a marimo function that makes a slider; its .value is the chosen setting.
    rule_multiple = mo.ui.slider(steps=[0.5, 1, 2, 5, 10], value=1,
                                 label="Cutoff, times 4/(n − P − 1)", show_value=True)
    rule_multiple
    return (rule_multiple,)


@app.cell
def rule_view(
    coefficient_table,
    fit,
    main_diagnostics,
    main_model,
    mo,
    rule_multiple,
    salaries,
    scale_pick,
    thresholds,
):
    _cutoff = thresholds(main_model)["cooks"] * rule_multiple.value
    _flagged = main_diagnostics.index[main_diagnostics["cooks"] > _cutoff]
    _without = fit(scale_pick.value, salaries.drop(index=_flagged))
    _compare = coefficient_table(main_model)[["coefficient"]].rename(
        columns={"coefficient": "every row"})
    _compare["without the flagged rows"] = coefficient_table(_without)["coefficient"]
    mo.vstack([
        mo.md(f"A cutoff of **{_cutoff:.4f}** flags **{len(_flagged)}** of {len(salaries)} rows. "
              f"R² is **{main_model.rsquared:.3f}** with every row and **{_without.rsquared:.3f}** "
              "without them."),
        _compare,
    ])
    return


@app.cell(hide_code=True)
def practice_outliers_intro(mo):
    mo.md(r"""
    ### Practice: count the outliers

    Please replace `None` in the cell below with the number of rows whose standardized residual is
    beyond ±2.5, computed from `main_diagnostics["standardized"]`, and compare the count on the two
    scales.
    """)
    return


@app.cell
def practice_outliers():
    my_outlier_count = None
    my_outlier_count
    return


@app.cell(hide_code=True)
def influence_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute each row's standardized residual, hat-value and Cook's distance,
    print the reading's two rules of thumb, list the rows with the largest Cook's distance, and then
    refit the model without the rows above the influence rule and compare the coefficients. Whether
    any of those rows should be left out is a judgement about each row, and the comparison only shows
    how much the coefficients depend on them.
    """)
    return


@app.cell
def influence_code(pd, salaries, smf):
    # Uses: import pandas as pd
    #       import statsmodels.formula.api as smf
    _formula = "salary_k ~ C(experience) + us_company + C(size)"
    _model = smf.ols(_formula, data=salaries).fit()
    _influence = _model.get_influence()
    _table = salaries[["job_title", "experience", "company_location", "salary_k"]].assign(
        standardized=_influence.resid_studentized_internal,
        hat=_influence.hat_matrix_diag,
        cooks=_influence.cooks_distance[0],
    )
    _n, _p = int(_model.nobs), int(_model.df_model)
    _cooks_rule, _hat_rule = 4 / (_n - _p - 1), 2 * (_p + 1) / _n
    print(f"n = {_n}, P = {_p}, influence rule {_cooks_rule:.4f}, leverage rule {_hat_rule:.3f}")
    print(_table.sort_values("cooks", ascending=False).head(8).round(3))
    print()

    _flagged = _table.index[_table["cooks"] > _cooks_rule]
    _without = smf.ols(_formula, data=salaries.drop(index=_flagged)).fit()
    pd.DataFrame({"every row": _model.params,
                  f"without {len(_flagged)} rows": _without.params}).round(1)
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    A university career office wants to tell students what data science jobs pay, and how pay
    differs with experience, the employer's location and its size. It plans to quote a regression
    like the one in this notebook.

    > **Fit the regression, then use its diagnostics to say how well it describes most of these
    > jobs, and where it does not.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. The residual plots, on the scale you would choose, to say whether the model's errors are even
       across the jobs and what that means for the intervals the office would quote.
    2. The influence measures, to say which rows have the most influence, why, and whether leaving
       them out changes the coefficients the office cares about.
    3. One limitation of your explanation: something the diagnostics cannot tell the office.

    Then compare your results with your teammates', who started from a different scale or a
    different set of predictors, and say what their results showed that yours did not, and whether
    that changes your explanation.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each
    prompt, in your own words and with the numbers from your own runs. Each of you should then
    upload your own copy of this notebook to *AE 11* on Canvas, by 23:59 on Thursday.

    | Part of your answer | Points |
    |---|---:|
    | Your explanation: the residuals and the scale, the influential rows and their effect, and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop rather than watching one
    screen, and start from a different scale or set of predictors from your teammates, then compare
    what you find. Your team may agree on an explanation, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholders in Step 1, run
    the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_choose():
    # Step 1: choose the scale, "salary_k" or "log_salary", and the predictors. The notebook's
    # predictors are "C(experience) + us_company + C(size)"; you may add remote_ratio or
    # C(work_year), or remove one.
    answer_outcome = "SOME_SCALE"
    answer_predictors = "SOME_PREDICTORS"
    return answer_outcome, answer_predictors


@app.cell
def step2_fit(
    answer_outcome,
    answer_predictors,
    coefficient_table,
    diagnostics,
    fit,
    mo,
    plt,
    salaries,
):
    # Step 2: fit the model, list its coefficients, and plot the residuals against the fitted values.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder values.
    mo.stop("SOME_" in answer_outcome + answer_predictors,
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md("Replace the placeholders in Step 1.").callout(kind="info"))
    answer_model = fit(answer_outcome, salaries, answer_predictors)
    answer_diagnostics = diagnostics(answer_model, salaries)
    _fig, _ax = plt.subplots(figsize=(7, 3.5))
    _ax.scatter(answer_diagnostics["fitted"], answer_diagnostics["residual"], s=10, alpha=0.5)
    _ax.axhline(0, color="#111827", linewidth=1)
    _ax.set_xlabel("Fitted value")
    _ax.set_ylabel("Residual")
    _fig.tight_layout()
    mo.vstack([mo.md(f"R² = **{answer_model.rsquared:.3f}**"), coefficient_table(answer_model),
               _fig])
    return answer_diagnostics, answer_model


@app.cell
def step3_influence(answer_diagnostics, answer_model, mo, thresholds):
    # Step 3: the ten rows with the largest Cook's distance, and how many pass the rule of thumb.
    _rule = thresholds(answer_model)["cooks"]
    mo.vstack([
        mo.md(f"**{int((answer_diagnostics['cooks'] > _rule).sum())}** rows have a Cook's distance "
              f"above 4/(n − P − 1) = {_rule:.4f}."),
        answer_diagnostics.sort_values("cooks", ascending=False).head(10).round(3),
    ])
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L13_regression_diagnostics.py` to *AE 11* on Canvas by 23:59 on Thursday. We will
    cross-reference your claims about evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_residuals(mo):
    mo.md(r"""
    **What the residuals show on the scale you chose, and what that means for the intervals**
    """)
    return


@app.cell
def step4_answer_residuals(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_influence(mo):
    mo.md(r"""
    **The most influential rows, why they are influential, and what leaving them out changes**
    """)
    return


@app.cell
def step4_answer_influence(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_limitation(mo):
    mo.md(r"""
    **One limitation of your explanation**
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
