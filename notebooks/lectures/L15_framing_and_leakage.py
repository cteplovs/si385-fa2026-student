# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "scikit-learn>=1.5",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 15: Framing a machine learning problem

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, October 26, 2026

    **Reading due today:** Géron, *Hands-On Machine Learning*, ch. 1, *The Machine Learning
    Landscape*

    ---

    ### Today you will be able to

    - Say when each column in a dataset becomes known, and what that means for a model that has
      to predict before then
    - Recognize leakage: a column that would not exist at the moment the prediction is made
    - Read a cross-validated score as an estimate of how a model would do on students it has not
      seen
    """)
    return


@app.cell
def _():
    import marimo as mo
    from io import BytesIO

    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    # Every lens is one of the first four groups paired with one of the last three, as in the
    # pre-read's table. The column names are exactly as they appear in the lens files.
    GROUPS = {
        "Background": ["Marital status", "Gender", "Age at enrollment", "Nacionality",
                       "International", "Displaced"],
        "Family": ["Mother's qualification", "Father's qualification", "Mother's occupation",
                   "Father's occupation", "Educational special needs"],
        "Admission": ["Application mode", "Application order", "Course",
                      "Daytime/evening attendance", "Previous qualification",
                      "Previous qualification (grade)", "Admission grade"],
        "Economy": ["Unemployment rate", "Inflation rate", "GDP"],
        "Money": ["Debtor", "Tuition fees up to date", "Scholarship holder"],
        "Semester 1": [f"Curricular units 1st sem ({_part})" for _part in
                       ("credited", "enrolled", "evaluations", "approved", "grade",
                        "without evaluations")],
        "Semester 2": [f"Curricular units 2nd sem ({_part})" for _part in
                       ("credited", "enrolled", "evaluations", "approved", "grade",
                        "without evaluations")],
    }
    # What each group holds, and when the institution would know it. The Money entry says only
    # what the documentation says, because when those columns exist is what AE 13 turns on.
    ABOUT = {
        "Background": ("age at enrolment, gender, marital status, nationality, and whether the "
                       "student moved to attend", "At enrolment"),
        "Family": ("each parent's qualification and occupation, and special educational needs",
                   "At enrolment"),
        "Admission": ("how and to which course the student applied, their previous qualification, "
                      "and their admission grade", "At enrolment"),
        "Economy": ("Portugal's unemployment rate, inflation rate and GDP, for the year the "
                    "student enrolled", "At enrolment"),
        "Money": ("whether the student is a debtor, is up to date on tuition fees, and holds a "
                  "scholarship", "The documentation does not say"),
        "Semester 1": ("the student's first semester: the units they enrolled in, were evaluated "
                       "in, passed and were credited with, and their grade",
                       "At the end of the first semester"),
        "Semester 2": ("the student's second semester: the units they enrolled in, were evaluated "
                       "in, passed and were credited with, and their grade",
                       "At the end of the second semester"),
    }
    FIRST_FOUR = ["Background", "Family", "Admission", "Economy"]
    LAST_THREE = ["Money", "Semester 1", "Semester 2"]
    OUTCOMES = ["Dropout", "Enrolled", "Graduate"]
    COLOURS = {"Dropout": "#c2410c", "Enrolled": "#9ca3af", "Graduate": "#1f4e79"}
    return (
        ABOUT,
        BytesIO,
        COLOURS,
        FIRST_FOUR,
        GROUPS,
        LAST_THREE,
        OUTCOMES,
        RandomForestClassifier,
        StratifiedKFold,
        cross_val_score,
        mo,
        np,
        pd,
        plt,
    )


@app.cell(hide_code=True)
def _(ABOUT, mo):
    _rows = "\n".join(f"    | {_g} | {_holds[0].upper()}{_holds[1:]} | {_known} |"
                       for _g, (_holds, _known) in ABOUT.items())
    mo.md(f"""
    ---
    # 0:15 · Application exercise 13

    ## When should the tutoring team call?

    The records describe 4,424 students who enrolled in undergraduate degrees at the Instituto
    Politécnico de Portalegre, in Portugal, between 2008/09 and 2018/19. Each student is labelled
    with where they stood at the end of the normal length of their course: graduated, dropped out,
    or still enrolled.

    Portalegre's tutoring team uses a tool built on these records to estimate each student's risk
    of dropping out, and contacts the students at highest risk. For this module, suppose the team
    has asked the class to build that list of students, and that it will make the list only once.
    A list made early reaches students while there is still time to help them, and a list made
    later can draw on more of what the institution knows about each student.

    > **When should the list be made, and what may it use?**

    Your team will choose one of the options on casefile and post a note there that justifies
    the choice.

    ### Groups of columns

    The columns fall into the groups below. Your team holds a lens: one of the first four groups
    and one of the last three, for every student, together with the outcome. Other teams hold the
    other groups.

    | Group of columns | What it holds | When the institution knows it |
    |---|---|---|
{_rows}

    Please download your team's lens from your team's page on casefile, then choose the file
    below. The notebook reads only that file, and works out which two groups of columns it holds.
    """)
    return


@app.cell
def _(mo):
    lens_upload = mo.ui.file(filetypes=[".csv"], label="Choose your lens file")
    lens_upload
    return (lens_upload,)


@app.cell
def _(BytesIO, FIRST_FOUR, GROUPS, LAST_THREE, lens_upload, mo, pd):
    mo.stop(not lens_upload.value,
            mo.md("Choose your team's lens file above to continue.").callout(kind="info"))

    lens = pd.read_csv(BytesIO(lens_upload.contents()))
    _held = [_g for _g, _cols in GROUPS.items() if set(_cols) <= set(lens.columns)]
    _first = [_g for _g in _held if _g in FIRST_FOUR]
    _second = [_g for _g in _held if _g in LAST_THREE]
    mo.stop(len(_first) != 1 or len(_second) != 1 or "outcome" not in lens.columns,
            mo.md("This file does not look like a casefile lens. Please download it again "
                  "from your team's page on casefile.").callout(kind="warn"))

    first_group, second_group = _first[0], _second[0]
    mo.vstack([
        mo.md(f"Your lens holds **{first_group}** and **{second_group}** for "
              f"{len(lens):,} students, with each student's outcome."),
        lens.head(),
    ])
    return first_group, lens, second_group


@app.cell(hide_code=True)
def _(ABOUT, GROUPS, first_group, mo, second_group):
    column_pick = mo.ui.dropdown(options=GROUPS[second_group],
                                 value=GROUPS[second_group][0], label="Column")
    _holds, _known = ABOUT[second_group]
    _when = ("The documentation does not say when these columns are recorded."
             if second_group == "Money" else
             f"The institution knows them {_known[0].lower()}{_known[1:]}.")
    _codes = " The three columns use 1 for yes and 0 for no." if second_group == "Money" else ""
    mo.md(f"""
    ---
    ### Your {second_group} columns, one at a time

    Your {first_group} columns are known at enrolment, so a list made on the first day could use
    them. Your {second_group} columns record {_holds}. {_when} Whether a list could use them
    depends on when it is made, so please start with them.

    The chart shows, for each value of the column you choose, the share of students who dropped
    out, were still enrolled, or graduated.{_codes}

    {column_pick}
    """)
    return (column_pick,)


@app.cell
def _(COLOURS, OUTCOMES, column_pick, lens, np, pd, plt):
    def bands(values):
        """Group a column's values for the chart: as they are if there are few, otherwise
        zero on its own and the other values in quarters."""
        if values.nunique() <= 10:
            return values
        _nonzero = values[values > 0]
        _whole = bool((_nonzero % 1 == 0).all())
        _edges = np.unique(_nonzero.quantile([0, 0.25, 0.5, 0.75, 1]).to_numpy())
        if _whole:
            _edges = np.unique(np.ceil(_edges))
        # Each band holds the values above its lower edge, up to and including its upper edge.
        _labels = ["0"]
        for _i, _hi in enumerate(_edges[1:]):
            _lo = _edges[0] if _i == 0 else _edges[_i] + (1 if _whole else 0)
            if _whole:
                _labels.append(f"{_lo:g}" if _lo == _hi else f"{_lo:g} to {_hi:g}")
            else:
                _labels.append(f"{_lo:.1f} to {_hi:.1f}")
        return pd.cut(values, bins=[-np.inf, 0, *_edges[1:]], labels=_labels)

    _banded = bands(lens[column_pick.value])
    _shares = pd.crosstab(_banded, lens["outcome"], normalize="index")[OUTCOMES]
    _counts = _banded.value_counts().reindex(_shares.index)

    _fig, _ax = plt.subplots(figsize=(8, 0.45 * len(_shares) + 1.2))
    _left = np.zeros(len(_shares))
    for _outcome in OUTCOMES:
        _ax.barh(_shares.index.astype(str), _shares[_outcome], left=_left,
                 color=COLOURS[_outcome], label=_outcome)
        _left += _shares[_outcome].to_numpy()
    for _i, _n in enumerate(_counts):
        _ax.text(1.01, _i, f"n = {_n:,}", va="center", fontsize=9)
    _ax.set_xlim(0, 1)
    _ax.invert_yaxis()
    _ax.set_xlabel("Share of students")
    _ax.set_ylabel(column_pick.value)
    _ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(first_group, mo, second_group):
    mo.md(f"""
    ---
    ### Adding {second_group} to a model

    The list ranks students by their risk of dropping out, so a better model makes a better list.
    The cell below fits a model that predicts whether each student dropped out, once from your
    {first_group} columns alone and once with your {second_group} columns added. You will not
    need to know how the model works today; session 16 will build models like it.

    Each number is an AUC. If you pick one student who dropped out and one who did not, the AUC
    is the chance that the model gives the student who dropped out the higher risk, so 0.5 is no
    better than guessing and 1.0 would rank every dropout first. The score is cross-validated:
    the students are split into five parts, and each part is scored by a model that was trained
    on the other four, so the number estimates how the model would do on students it has not
    seen. Fitting the ten models takes a few seconds.
    """)
    return


@app.cell
def _(
    GROUPS,
    RandomForestClassifier,
    StratifiedKFold,
    cross_val_score,
    first_group,
    lens,
    mo,
    second_group,
):
    def cv_auc(columns):
        """Mean five-fold cross-validated AUC for predicting dropout from these columns."""
        model = RandomForestClassifier(n_estimators=200, min_samples_leaf=5,
                                       random_state=385, n_jobs=-1)
        folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=385)
        return cross_val_score(model, lens[columns], lens["outcome"] == "Dropout",
                               cv=folds, scoring="roc_auc").mean()

    with mo.status.spinner(title="Fitting the models"):
        auc_first = cv_auc(GROUPS[first_group])
        auc_both = cv_auc(GROUPS[first_group] + GROUPS[second_group])

    mo.hstack([
        mo.stat(value=f"{auc_first:.2f}", label=f"{first_group} alone"),
        mo.stat(value=f"{auc_both:.2f}", label=f"{first_group} and {second_group}"),
    ], justify="start", gap=2)
    return


@app.cell(hide_code=True)
def _(mo, second_group):
    mo.md(f"""
    ---
    ### {second_group} among the students who dropped out

    The table compares the three outcomes on a few facts from your {second_group} columns.
    Each cell is the share of that outcome's students for whom the row is true. Please consider,
    for each row, when the institution would know it, and whether the student would still be
    there to call by then.
    """)
    return


@app.cell
def _(OUTCOMES, lens, pd, second_group):
    def checks(group):
        """The facts to compare for each of the last three groups."""
        if group == "Money":
            return {
                "Is a debtor": lens["Debtor"] == 1,
                "Is not up to date on tuition fees": lens["Tuition fees up to date"] == 0,
                "Holds a scholarship": lens["Scholarship holder"] == 1,
            }
        _sem = "1st" if group == "Semester 1" else "2nd"
        _col = lambda _part: lens[f"Curricular units {_sem} sem ({_part})"]
        return {
            "Enrolled in no units": _col("enrolled") == 0,
            "Was evaluated in no units": _col("evaluations") == 0,
            "Passed no units": _col("approved") == 0,
        }

    _rows = {_label: _true.groupby(lens["outcome"]).mean()[OUTCOMES]
             for _label, _true in checks(second_group).items()}
    _table = pd.DataFrame(_rows).T.map(lambda _share: f"{_share:.0%}")
    _table.loc["Students"] = [f"{_n:,}" for _n in lens["outcome"].value_counts()[OUTCOMES]]
    _table
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### For your team's note

    Please take one number from this notebook into your team's note on casefile, and say what it
    means for when the list should be made.
    """)
    return


if __name__ == "__main__":
    app.run()
