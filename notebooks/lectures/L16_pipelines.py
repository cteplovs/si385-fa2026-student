# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
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

    ## Session 16: Pipelines, and what a score is measuring

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, October 28, 2026

    **Reading due today:** Géron, *Hands-On Machine Learning*, ch. 2, *End-to-End Machine Learning
    Project*; or the scikit-learn User Guide pages *Common pitfalls and recommended practices* and
    *Pipelines and composite estimators*

    ---

    ### Today you will be able to

    - Build a pipeline that selects columns and fits a model in one step, so that cross-validation
      fits every step on the training data only
    - Choose how to split the data for cross-validation so that the test resembles the prediction
      the model will actually be asked to make
    - Say whether a column describes a person or a group that the person belongs to, and what that
      means for ranking people within the group
    """)
    return


@app.cell
def _():
    import marimo as mo
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    import pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import LeaveOneGroupOut, StratifiedKFold, cross_val_score
    from sklearn.pipeline import make_pipeline

    # The four day-one groups, as in session 15. The column names are exactly as they appear in
    # the lens files and the Economy file.
    DAY_ONE = {
        "Background": ["Marital status", "Gender", "Age at enrollment", "Nacionality",
                       "International", "Displaced"],
        "Family": ["Mother's qualification", "Father's qualification", "Mother's occupation",
                   "Father's occupation", "Educational special needs"],
        "Admission": ["Application mode", "Application order", "Course",
                      "Daytime/evening attendance", "Previous qualification",
                      "Previous qualification (grade)", "Admission grade"],
        "Economy": ["Unemployment rate", "Inflation rate", "GDP"],
    }
    ECONOMY = DAY_ONE["Economy"]
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
        with urllib.request.urlopen(REMOTE + name) as _response:
            return pd.read_csv(BytesIO(_response.read()))

    return (
        BytesIO,
        ColumnTransformer,
        DAY_ONE,
        ECONOMY,
        LeaveOneGroupOut,
        RandomForestClassifier,
        StratifiedKFold,
        course_csv,
        cross_val_score,
        make_pipeline,
        mo,
        pd,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    # 0:15 · Application exercise 14

    ## What do the Economy columns tell a model?

    The tutoring team's list is still made once, on day one, so today every team works with its
    day-one columns only: the group from Background, Family, Admission or Economy that the
    institution knows at enrolment. Your team's Money or Semester columns were ruled on in session
    15 and are set aside.

    The Economy columns are Portugal's national unemployment rate, inflation rate and GDP, for the
    year each student enrolled. About a quarter of the teams hold them in their lens, and today
    they open to every team, so that every team works the same question. On their own, they score
    an AUC of 0.53 for dropout.

    > **What are the Economy columns telling the model, and should the tutoring team's list use
    > them?**

    Your team will choose one of the options on casefile and post a note there that justifies the
    choice.

    ### What your team compares

    Every team receives the same question, the same three Economy columns, and the same table of
    them at the end of this notebook. What your team compares depends on its day-one group.

    | Your team's day-one group | What your team compares |
    |---|---|
    | Background, Family or Admission | Your group alone, against your group with the Economy columns added |
    | Economy | The Economy columns alone, since they are your group |

    Teams whose day-one group is Economy have one comparison fewer than the others, but they hold
    the evidence the question is about, and the table at the end is the same for everyone.

    Please download your team's lens from your team's page on casefile, then choose the file
    below. The notebook adds the Economy columns to it from `data/si385_economy.csv`, matching
    each student by the `student` number.
    """)
    return


@app.cell
def _(mo):
    lens_upload = mo.ui.file(filetypes=[".csv"], label="Choose your lens file")
    lens_upload
    return (lens_upload,)


@app.cell
def _(BytesIO, DAY_ONE, ECONOMY, course_csv, lens_upload, mo, pd):
    mo.stop(not lens_upload.value,
            mo.md("Choose your team's lens file above to continue.").callout(kind="info"))

    _lens = pd.read_csv(BytesIO(lens_upload.contents()))
    _held = [_g for _g, _cols in DAY_ONE.items() if set(_cols) <= set(_lens.columns)]
    mo.stop(len(_held) != 1 or not {"student", "outcome"} <= set(_lens.columns),
            mo.md("This file does not look like a casefile lens. Please download it again "
                  "from your team's page on casefile.").callout(kind="warn"))
    day_one = _held[0]

    # Teams holding Economy already have its columns, so only the others take them from the file.
    economy = course_csv("si385_economy.csv")
    students = (_lens if day_one == "Economy"
                else _lens.merge(economy, on="student", validate="one_to_one"))
    dropped_out = students["outcome"] == "Dropout"

    mo.md(f"Your team's day-one group is **{day_one}**. The table holds "
          f"{len(students):,} students, with the Economy columns added where your lens "
          f"did not already have them.")
    return day_one, dropped_out, students


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### A pipeline

    The model is a pipeline of two steps. The first is a `ColumnTransformer` that passes through
    the columns it is given and drops every other column, which is its default for columns it does
    not list; that is how your Money or Semester columns stay out, even though they are still in
    the table. The second is the random forest from session 15.

    Because the column choice is a step in the pipeline, cross-validation fits both steps on the
    training part of each split only, and scores them on the part that was held out. The cell
    below builds the pipeline for your day-one group, and marimo shows its steps.
    """)
    return


@app.cell
def _(ColumnTransformer, DAY_ONE, RandomForestClassifier, day_one, make_pipeline):
    def pipeline(columns):
        """Keep only these columns, then fit a random forest."""
        return make_pipeline(
            ColumnTransformer([("chosen", "passthrough", columns)]),
            RandomForestClassifier(n_estimators=200, min_samples_leaf=5, random_state=385,
                                   n_jobs=-1),
        )

    pipeline(DAY_ONE[day_one])
    return (pipeline,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### Two ways to split the students

    A cross-validated score depends on how the students are split into training and test parts.
    Each split below is scored by AUC, as on Monday: 0.5 is no better than guessing, and 1.0 would
    rank every dropout first.

    - **Random split**, as on Monday. The students are shuffled into five parts, and each part is
      scored by a model trained on the other four.
    - **Split by entering class.** The three Economy columns take only ten combinations of values,
      and they are figures for the year each student enrolled, so students who share a combination
      enrolled under the same national conditions. The notebook calls each combination an
      *entering class*. Here each class in turn is held out, a model is trained on the
      other nine classes, and the held-out class is scored. Each score therefore measures how well
      the model ranks the students within one class that it has never seen, and the number shown is
      the average over the ten classes.

    The tutoring team makes its list for one entering class at a time. Fitting all the models
    takes up to half a minute.
    """)
    return


@app.cell
def _(
    DAY_ONE,
    ECONOMY,
    LeaveOneGroupOut,
    StratifiedKFold,
    cross_val_score,
    day_one,
    dropped_out,
    mo,
    pd,
    pipeline,
    students,
):
    entering_class = students[ECONOMY].astype(str).agg(" / ".join, axis=1)

    def auc(columns, split):
        """Mean cross-validated AUC for predicting dropout from these columns."""
        if split == "random":
            _folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=385)
            return cross_val_score(pipeline(columns), students, dropped_out, cv=_folds,
                                   scoring="roc_auc").mean()
        return cross_val_score(pipeline(columns), students, dropped_out, cv=LeaveOneGroupOut(),
                               groups=entering_class, scoring="roc_auc").mean()

    if day_one == "Economy":
        _rows = {"Economy alone": ECONOMY}
    else:
        _rows = {f"{day_one} alone": DAY_ONE[day_one],
                 f"{day_one} with Economy": DAY_ONE[day_one] + ECONOMY}
    with mo.status.spinner(title="Fitting the models"):
        scores = pd.DataFrame(
            {_label: {"Random split": auc(_cols, "random"),
                      "Split by entering class": auc(_cols, "by class")}
             for _label, _cols in _rows.items()}).T.map("{:.2f}".format)
    scores
    return (entering_class,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### The ten entering classes

    This table is the same for every team. Each row is one entering class, with its Economy values,
    its number of students and the share of them who dropped out. The classes are numbered in order
    of the unemployment rate, because the data do not say which year each one is.
    """)
    return


@app.cell
def _(ECONOMY, dropped_out, entering_class, students):
    _classes = (students.assign(dropped_out=dropped_out, entering_class=entering_class)
                .groupby("entering_class")
                .agg(**{_c: (_c, "first") for _c in ECONOMY},
                     students=("student", "size"), dropout=("dropped_out", "mean"))
                .sort_values("Unemployment rate"))
    _classes.index = [f"Class {_n}" for _n in range(1, len(_classes) + 1)]
    _classes.assign(dropout=_classes["dropout"].map("{:.0%}".format))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ### For your team's note

    Please say, in your team's own words, what the Economy columns vary with, and take one number
    from this notebook into the note, with what it means for the tutoring team's list.
    """)
    return


if __name__ == "__main__":
    app.run()
