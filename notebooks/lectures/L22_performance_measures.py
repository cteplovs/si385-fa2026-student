# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
#     "scikit-learn>=1.5",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 22: Classification II: evaluation beyond accuracy

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, November 18, 2026

    The reading due today is chapter 3 of Géron, *Hands-On Machine Learning with Scikit-Learn and
    PyTorch*, from the subsection *Training a Binary Classifier* to the end of the section
    *Performance Measures*.

    ---

    ### Today you will be able to

    - Explain why a classifier's accuracy says little when one class is rare, and compare it with
      a classifier that always predicts the common class
    - Compute a confusion matrix, precision and recall at a chosen threshold, and describe how
      precision and recall change as the threshold moves
    - Choose a threshold to fit what the people using a classifier can do, and judge whether the
      classifier is worth using at that threshold

    ### The main idea

    When one class is rare, a classifier can be very accurate and still find almost none of the
    cases that matter. Precision and recall describe the cases it flags and the cases it finds,
    and the threshold sets the balance between them, so choosing a threshold is a decision about
    what each kind of error costs and who bears it.

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Accuracy when one class is rare | 4 |
    | The confusion matrix, precision and recall | 5 |
    | Thresholds, and the PR and ROC curves | 6 |
    | Today's question, in teams | 35 |
    | After the question: the four capacities together | 10 |
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import (confusion_matrix, precision_recall_curve, precision_score,
                                 recall_score, roc_auc_score, roc_curve)
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    return (
        ColumnTransformer,
        LogisticRegression,
        OneHotEncoder,
        RandomForestClassifier,
        StandardScaler,
        confusion_matrix,
        make_pipeline,
        mo,
        np,
        pd,
        plt,
        precision_recall_curve,
        precision_score,
        recall_score,
        roc_auc_score,
        roc_curve,
        train_test_split,
    )


@app.cell(hide_code=True)
def data_helper(pd):
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    REMOTE = ("https://raw.githubusercontent.com/"
              "cteplovs/si385-fa2026-student/main/data/")


    def _course_bytes(name):
        """Return a path to the local copy of a course data file, or its bytes from GitHub.

        The copy in the course folder is the one to prefer, and it is what you get if you are
        running this the documented way. The fallback to the public repository is there so that
        the notebook also runs on molab, provided you have a network.
        """
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return local
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as response:
            return BytesIO(response.read())


    def course_parquet(name):
        """Read one of the course Parquet files."""
        return pd.read_parquet(_course_bytes(name))

    return (course_parquet,)


@app.cell
def palette():
    # Okabe and Ito's colours, which stay distinct for the common forms of colour blindness.
    MODEL_COLOURS = {"logistic regression": "#0072B2", "random forest": "#E69F00",
                     "at random": "#999999"}
    return (MODEL_COLOURS,)


@app.cell(hide_code=True)
def hidden_code_note(mo):
    mo.md(r"""
    ### Hidden and visible code, and the code on its own

    The code you need to follow today's analysis is visible. Code that only draws a chart, loads a
    file or defines a helper function is hidden, and you see only its output. You are welcome to
    reveal any of it. To show or hide one cell's code, click the cell and press Ctrl+H (⌘H on a
    Mac), or hover over the cell, open its menu with the **⋯** button, and choose
    **Show code**. To show all of it at once, open the command palette with
    Ctrl+K (⌘K on a Mac) and choose **Show all code**. The notebook is also a plain Python file, so
    you can read every cell by opening `L22_performance_measures.py` in any text editor.

    The teaching ends with a section headed *The code on its own*, which uses only pandas and
    scikit-learn, starts from a data frame, and does the computation without any controls, so that
    you can copy it into your project or another notebook.
    """)
    return


@app.cell(hide_code=True)
def accuracy_intro(mo):
    mo.md(r"""
    ## Accuracy when one class is rare

    We start with the Michigan survey from session 21, and with a question it did not ask: of the
    people in the labour force, who is unemployed? About 4% of them are. We fit a logistic
    regression to three quarters of the people and compare its accuracy on the rest with that of a
    classifier that predicts *employed* for everyone, which is the dummy classifier from the
    reading.
    """)
    return


@app.cell
def load_unemployment(course_parquet, train_test_split):
    # The labour force is everyone who is working, or looking for work and able to start.
    _acs = course_parquet("acs_michigan_2023.parquet")
    _labour = _acs[_acs["employment_status"].notna()
                   & (_acs["employment_status"] != "not in the labour force")]
    JOB_NUMERIC = ["age", "schooling"]
    JOB_CATEGORICAL = ["sex", "race", "marital_status", "disability", "born_in_us",
                       "military_service"]
    _X = _labour[JOB_NUMERIC + JOB_CATEGORICAL].copy()
    _X[JOB_CATEGORICAL] = _X[JOB_CATEGORICAL].astype("string").fillna("not applicable")
    _y = _labour["employment_status"] == "unemployed"
    job_X_train, job_X_test, job_y_train, job_y_test = train_test_split(
        _X, _y, test_size=0.25, stratify=_y, random_state=0)
    print(f"{len(_labour):,} people in the labour force, {_y.mean():.1%} unemployed")
    return (
        JOB_CATEGORICAL,
        JOB_NUMERIC,
        job_X_test,
        job_X_train,
        job_y_test,
        job_y_train,
    )


@app.cell
def job_fit(
    ColumnTransformer,
    JOB_CATEGORICAL,
    JOB_NUMERIC,
    LogisticRegression,
    OneHotEncoder,
    StandardScaler,
    job_X_test,
    job_X_train,
    job_y_test,
    job_y_train,
    make_pipeline,
    pd,
):
    job_model = make_pipeline(
        ColumnTransformer([("numeric", StandardScaler(), JOB_NUMERIC),
                           ("categorical", OneHotEncoder(handle_unknown="ignore"),
                            JOB_CATEGORICAL)]),
        LogisticRegression(max_iter=2000)).fit(job_X_train, job_y_train)
    job_scores = job_model.predict_proba(job_X_test)[:, 1]
    pd.Series({"always predict employed": (~job_y_test).mean(),
               "logistic regression": job_model.score(job_X_test, job_y_test)},
              name="accuracy on the test rows").round(3)
    return (job_scores,)


@app.cell(hide_code=True)
def accuracy_note(job_scores, job_y_test, mo):
    mo.md(rf"""
    The two accuracies are almost the same, because a logistic regression that predicts
    *unemployed* only when the estimated probability is above 0.5 predicts it for
    {(job_scores > 0.5).sum()} of the {len(job_y_test):,} test rows. The highest estimated
    probability of any person is {job_scores.max():.2f}. Both classifiers are right about nearly
    everyone who is employed and find almost nobody who is unemployed, and accuracy cannot
    distinguish them because the unemployed are 4% of the rows.
    """)
    return


@app.cell(hide_code=True)
def confusion_intro(mo):
    mo.md(r"""
    ## The confusion matrix, precision and recall

    The confusion matrix counts the four outcomes separately. Each row is the actual class and
    each column is the predicted class, as in the reading. From it, *precision* is the share of
    the people predicted unemployed who are unemployed, and *recall* is the share of the
    unemployed whom the classifier predicted unemployed.

    The slider sets the threshold: the classifier predicts *unemployed* for everyone whose
    estimated probability is above it. Move it down from 0.5 and watch the four counts.
    """)
    return


@app.cell(hide_code=True)
def threshold_control(mo):
    job_threshold = mo.ui.slider(0.02, 0.5, step=0.01, value=0.5, label="threshold")
    return (job_threshold,)


@app.cell
def job_confusion(
    confusion_matrix,
    job_scores,
    job_threshold,
    job_y_test,
    pd,
    precision_score,
    recall_score,
):
    job_predicted = job_scores > job_threshold.value
    job_matrix = pd.DataFrame(
        confusion_matrix(job_y_test, job_predicted, labels=[False, True]),
        index=["actually employed", "actually unemployed"],
        columns=["predicted employed", "predicted unemployed"])
    job_precision = precision_score(job_y_test, job_predicted, zero_division=0)
    job_recall = recall_score(job_y_test, job_predicted)
    return job_matrix, job_precision, job_recall


@app.cell(hide_code=True)
def confusion_show(job_matrix, job_precision, job_recall, job_threshold, mo):
    _tp = job_matrix.iloc[1, 1]
    _fp = job_matrix.iloc[0, 1]
    _fn = job_matrix.iloc[1, 0]
    mo.vstack([job_threshold, job_matrix, mo.md(rf"""
    At a threshold of {job_threshold.value:.2f}, the classifier predicts *unemployed* for
    {_tp + _fp:,} people, of whom {_tp:,} are unemployed, so its precision is
    {job_precision:.3f}. It finds {_tp:,} of the {_tp + _fn:,} unemployed people, so its recall is
    {job_recall:.3f}.
    """)])
    return


@app.cell(hide_code=True)
def curves_intro(mo):
    mo.md(r"""
    ## Thresholds, and the PR and ROC curves

    Lowering the threshold finds more of the unemployed, so recall rises, and it also flags more
    of the employed, so precision usually falls. The precision/recall (PR) curve on the left shows
    precision and recall at every threshold at once, and the ROC curve on the right shows the true
    positive rate (recall) against the false positive rate, which is the share of the employed
    whom the classifier predicted unemployed. The dot on each curve is the threshold on the
    slider above.

    The grey line on each plot is a classifier that flags people at random. On the PR curve, its
    precision is the share of the rows that are positive, whatever its recall; on the ROC curve, it
    is the diagonal, with an area under the curve (AUC) of 0.5.
    """)
    return


@app.cell(hide_code=True)
def curves_plot(
    MODEL_COLOURS,
    job_precision,
    job_recall,
    job_scores,
    job_threshold,
    job_y_test,
    plt,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
):
    _precision, _recall, _ = precision_recall_curve(job_y_test, job_scores)
    _fpr, _tpr, _ = roc_curve(job_y_test, job_scores)
    _predicted = job_scores > job_threshold.value
    _fpr_here = (_predicted & ~job_y_test.to_numpy()).sum() / (~job_y_test).sum()
    _colour = MODEL_COLOURS["logistic regression"]
    _grey = MODEL_COLOURS["at random"]

    _fig, (_pr, _roc) = plt.subplots(1, 2, figsize=(9, 4))
    _pr.plot(_recall, _precision, color=_colour)
    _pr.axhline(job_y_test.mean(), color=_grey, linestyle=":")
    _pr.plot([job_recall], [job_precision], "o", color="black")
    _pr.set(xlabel="recall", ylabel="precision", xlim=(0, 1), ylim=(0, 1),
            title="Precision against recall")
    _roc.plot(_fpr, _tpr, color=_colour)
    _roc.plot([0, 1], [0, 1], color=_grey, linestyle=":")
    _roc.plot([_fpr_here], [job_recall], "o", color="black")
    _roc.set(xlabel="false positive rate", ylabel="true positive rate (recall)",
             xlim=(0, 1), ylim=(0, 1),
             title=f"ROC curve, AUC {roc_auc_score(job_y_test, job_scores):.3f}")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def curves_note(job_scores, job_y_test, mo, roc_auc_score):
    mo.md(rf"""
    The ROC AUC of {roc_auc_score(job_y_test, job_scores):.2f} is well above the random
    classifier's 0.5, while the PR curve shows that at almost every threshold most of the people
    flagged are employed. The reading's advice is to prefer the PR curve when the positive class
    is rare, as it is here, because the false positive rate is computed over the large number of
    employed people, so a classifier can flag many of them and still have a low false positive
    rate.

    No threshold is correct in general. A programme that offers job-search help by letter can
    afford to flag many employed people to find more of the unemployed, and a programme that
    sends a caseworker to each person flagged cannot.
    """)
    return


@app.cell(hide_code=True)
def code_intro(mo):
    mo.md(r"""
    ### The code on its own

    The code below fits the same logistic regression, then computes the confusion matrix,
    precision and recall at one threshold, the threshold that flags a fixed share of the rows, and
    the ROC AUC. It starts from a data frame `people` with the predictors and a true/false column
    `outcome`.
    """)
    return


@app.cell
def code_alone(JOB_CATEGORICAL, JOB_NUMERIC, job_X_test, job_X_train, job_y_test, job_y_train):
    def _code_alone(X_train, y_train, X_test, y_test, numeric, categorical):
        import numpy as np
        from sklearn.compose import ColumnTransformer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import (confusion_matrix, precision_score, recall_score,
                                     roc_auc_score)
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        model = make_pipeline(
            ColumnTransformer([("numeric", StandardScaler(), numeric),
                               ("categorical", OneHotEncoder(handle_unknown="ignore"),
                                categorical)]),
            LogisticRegression(max_iter=2000)).fit(X_train, y_train)
        scores = model.predict_proba(X_test)[:, 1]

        predicted = scores > 0.1                       # any threshold you choose
        print(confusion_matrix(y_test, predicted))     # rows actual, columns predicted
        print("precision", precision_score(y_test, predicted, zero_division=0))
        print("recall   ", recall_score(y_test, predicted))

        # The threshold that flags the 10% of rows with the highest scores.
        top_10 = scores >= np.quantile(scores, 0.9)
        print("flag 10%: precision", precision_score(y_test, top_10),
              "recall", recall_score(y_test, top_10))
        print("ROC AUC", roc_auc_score(y_test, scores))


    _code_alone(job_X_train, job_y_train, job_X_test, job_y_test, JOB_NUMERIC, JOB_CATEGORICAL)
    return


@app.cell(hide_code=True)
def question(mo):
    mo.md(r"""
    ---
    ## Today's question

    **A hospital can enrol only a fixed share of the patients it discharges in a follow-up
    programme that is meant to prevent readmissions. Should it use a classifier to choose who is
    enrolled, and how does the answer depend on how many patients it can enrol? Each of you will
    take one capacity before your team decides.**

    The data describe 69,973 patients with diabetes at 130 US hospitals, from the pre-read, and
    the outcome is whether a patient was admitted again within 30 days. Your team's time is for
    talking through the problem, trying out ideas, and helping each other with the code. Each of
    you should run the code on your own laptop. You should take one capacity each, and if your team has
    three members, choose together which capacity to leave out. Your team should decide together
    what to recommend to the hospital, but the answer you submit is your own.

    In Step 1 you will choose your capacity, in Step 2 fit two classifiers, and in Step 3 see whom
    each would enrol at your capacity. In Step 4 you will write your answer.
    """)
    return


@app.cell
def load_readmission(course_parquet):
    patients = course_parquet("diabetes_readmission.parquet")
    READMIT_NUMERIC = ["days_in_hospital", "lab_tests", "procedures", "medications", "diagnoses",
                       "outpatient_visits_last_year", "emergency_visits_last_year",
                       "inpatient_stays_last_year"]
    READMIT_CATEGORICAL = ["age_group", "sex", "race", "admission_type", "admitted_from",
                           "discharged_to", "primary_diagnosis", "a1c_result", "insulin",
                           "medication_changed", "diabetes_medication"]
    print(f"{len(patients):,} patients, {patients['readmitted_30'].mean():.1%} readmitted "
          "within 30 days")
    return READMIT_CATEGORICAL, READMIT_NUMERIC, patients


@app.cell
def step1_choose(mo):
    # Step 1: choose your capacity, the share of discharged patients the programme can enrol.
    # Your team should take one each.
    answer_capacity = mo.ui.dropdown({"5%": 0.05, "10%": 0.10, "20%": 0.20, "40%": 0.40},
                                     value="10%", label="Capacity")
    answer_capacity
    return (answer_capacity,)


@app.cell
def step2_data(READMIT_CATEGORICAL, READMIT_NUMERIC, patients, train_test_split):
    # Step 2: we split the patients into training and test rows. The test rows stand for the
    # patients the hospital will discharge next, whom the models have not seen.
    _X = patients[READMIT_NUMERIC + READMIT_CATEGORICAL].copy()
    _X[READMIT_CATEGORICAL] = _X[READMIT_CATEGORICAL].astype("string").fillna("unknown")
    _y = patients["readmitted_30"]
    my_X_train, my_X_test, my_y_train, my_y_test = train_test_split(
        _X, _y, test_size=0.25, stratify=_y, random_state=0)
    print(f"{len(my_X_train):,} training rows, {len(my_X_test):,} test rows")
    return my_X_test, my_X_train, my_y_test, my_y_train


@app.cell
def step2_fit(
    ColumnTransformer,
    LogisticRegression,
    OneHotEncoder,
    READMIT_CATEGORICAL,
    READMIT_NUMERIC,
    RandomForestClassifier,
    StandardScaler,
    make_pipeline,
    my_X_test,
    my_X_train,
    my_y_test,
    my_y_train,
    pd,
    roc_auc_score,
):
    # We fit a logistic regression and a random forest, and give each test patient each model's
    # estimated probability of readmission.
    def _prepare(numeric):
        return ColumnTransformer([("numeric", numeric, READMIT_NUMERIC),
                                  ("categorical", OneHotEncoder(handle_unknown="ignore"),
                                   READMIT_CATEGORICAL)], verbose_feature_names_out=False)

    _models = {
        "logistic regression": make_pipeline(_prepare(StandardScaler()),
                                             LogisticRegression(max_iter=2000)),
        "random forest": make_pipeline(
            _prepare("passthrough"),
            RandomForestClassifier(n_estimators=200, min_samples_leaf=20, n_jobs=-1,
                                   random_state=0)),
    }
    my_scores = {_name: _model.fit(my_X_train, my_y_train).predict_proba(my_X_test)[:, 1]
                 for _name, _model in _models.items()}

    pd.DataFrame(
        [{"model": "always predict not readmitted", "accuracy": (~my_y_test).mean(),
          "ROC AUC": 0.5}]
        + [{"model": _name, "accuracy": ((_s > 0.5) == my_y_test).mean(),
            "ROC AUC": roc_auc_score(my_y_test, _s)}
           for _name, _s in my_scores.items()]).set_index("model").round(3)
    return (my_scores,)


@app.cell
def step3_enrol(answer_capacity, my_scores, my_y_test, np, pd):
    # Step 3: at your capacity, each model enrols the test patients with the highest scores. The
    # first row enrols the same number of patients at random, for comparison.
    _n = round(answer_capacity.value * len(my_y_test))
    _y = my_y_test.to_numpy()
    _rng = np.random.default_rng(0)
    my_enrolled = {"at random": np.isin(np.arange(len(_y)),
                                        _rng.choice(len(_y), _n, replace=False))}
    for _name, _s in my_scores.items():
        my_enrolled[_name] = np.isin(np.arange(len(_y)), np.argsort(-_s)[:_n])

    pd.DataFrame([{"enrolled by": _name,
                   "threshold": (my_scores[_name][_e].min() if _name in my_scores else None),
                   "patients enrolled": _e.sum(),
                   "readmissions among them": (_e & _y).sum(),
                   "precision": (_e & _y).sum() / _e.sum(),
                   "recall": (_e & _y).sum() / _y.sum()}
                  for _name, _e in my_enrolled.items()]).set_index("enrolled by").round(3)
    return (my_enrolled,)


@app.cell
def step3_who(my_X_test, my_enrolled, my_y_test, pd):
    # Who each model enrols: some characteristics of the enrolled patients, with all test
    # patients alongside.
    def _describe(rows):
        return pd.Series({
            "patients": rows.sum(),
            "inpatient stays last year, mean": my_X_test.loc[rows, "inpatient_stays_last_year"].mean(),
            "emergency visits last year, mean": my_X_test.loc[rows, "emergency_visits_last_year"].mean(),
            "days in hospital, mean": my_X_test.loc[rows, "days_in_hospital"].mean(),
            "aged 70 or over": my_X_test.loc[rows, "age_group"].isin(
                ["70 to 79", "80 to 89", "90 to 99"]).mean(),
            "discharged home": my_X_test.loc[rows, "discharged_to"].eq("home").mean(),
            "readmitted within 30 days": my_y_test[rows].mean(),
        })

    _all = pd.Series(True, index=my_X_test.index)
    pd.DataFrame({"all test patients": _describe(_all)}
                 | {_name: _describe(pd.Series(_e, index=my_X_test.index))
                    for _name, _e in my_enrolled.items() if _name != "at random"}).round(2)
    return


@app.cell
def step3_race(my_X_test, my_enrolled, my_y_test, pd):
    # Each model's share of patients enrolled, and its recall, within each race recorded in the
    # data. A group's recall is the share of its readmitted patients whom the model enrolled.
    _race = my_X_test["race"]
    _y = my_y_test.to_numpy()
    _rows = {}
    for _name, _e in my_enrolled.items():
        if _name == "at random":
            continue
        _e = pd.Series(_e, index=my_X_test.index)
        _rows[(_name, "share enrolled")] = _e.groupby(_race).mean()
        _rows[(_name, "recall")] = (_e & _y).groupby(_race).sum() / pd.Series(
            _y, index=my_X_test.index).groupby(_race).sum()
    pd.DataFrame(_rows).assign(patients=_race.value_counts()).round(3)
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy
    of `L22_performance_measures.py` to *AE 20* on Canvas before the end of class.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_capacity(mo):
    mo.md(r"""
    **Your capacity, and the precision and recall of each model at it, compared with enrolling the same number of patients at random**
    """)
    return


@app.cell
def step4_answer_capacity(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_who(mo):
    mo.md(r"""
    **Whom the models enrol at your capacity, and whom they miss, from the tables in Step 3**
    """)
    return


@app.cell
def step4_answer_who(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_team(mo):
    mo.md(r"""
    **With your teammates' capacities alongside yours, whether the hospital should use a classifier to choose who is enrolled, and how the answer depends on its capacity**
    """)
    return


@app.cell
def step4_answer_team(mo):
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
def after_intro(mo):
    mo.md(r"""
    ---
    ## After the question: the four capacities together

    Below, we put the four capacities side by side for both models, and mark them on each model's
    PR curve.
    """)
    return


@app.cell
def after_table(my_scores, my_y_test, np, pd):
    _y = my_y_test.to_numpy()
    _rows = []
    for _capacity in [0.05, 0.10, 0.20, 0.40]:
        _n = round(_capacity * len(_y))
        _row = {"capacity": f"{_capacity:.0%}", "recall at random": _capacity}
        for _name, _s in my_scores.items():
            _e = np.isin(np.arange(len(_y)), np.argsort(-_s)[:_n])
            _row[f"{_name}: precision"] = (_e & _y).sum() / _n
            _row[f"{_name}: recall"] = (_e & _y).sum() / _y.sum()
        _rows.append(_row)
    after_capacity = pd.DataFrame(_rows).set_index("capacity")
    after_capacity.round(3)
    return (after_capacity,)


@app.cell(hide_code=True)
def after_plot(MODEL_COLOURS, after_capacity, my_scores, my_y_test, plt,
               precision_recall_curve):
    _fig, _ax = plt.subplots(figsize=(6, 4))
    for _name, _s in my_scores.items():
        _p, _r, _ = precision_recall_curve(my_y_test, _s)
        _ax.plot(_r, _p, color=MODEL_COLOURS[_name], label=_name)
        _ax.plot(after_capacity[f"{_name}: recall"], after_capacity[f"{_name}: precision"],
                 "o", color=MODEL_COLOURS[_name])
    for _cap, _r, _p in zip(after_capacity.index, after_capacity["random forest: recall"],
                            after_capacity["random forest: precision"]):
        _ax.annotate(_cap, (_r, _p), textcoords="offset points", xytext=(4, 6))
    _ax.axhline(my_y_test.mean(), color=MODEL_COLOURS["at random"], linestyle=":",
                label="at random")
    _ax.set(xlabel="recall", ylabel="precision", xlim=(0, 1), ylim=(0, 0.6),
            title="Precision against recall, with the four capacities")
    _ax.legend()
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def after_note(after_capacity, mo, my_y_test):
    _forest = after_capacity[["random forest: precision", "random forest: recall"]]
    _low, _high = _forest.loc["5%"], _forest.loc["40%"]
    _rate = my_y_test.mean()
    mo.md(rf"""
    At 5%, the forest's enrolled patients are readmitted at {_low.iloc[0]:.0%}, against
    {_rate:.0%} for patients chosen at random, so the model is about
    {_low.iloc[0] / _rate:.1f} times as good as chance at finding them, but the programme reaches
    only {_low.iloc[1]:.0%} of the readmissions. At 40%, it reaches {_high.iloc[1]:.0%} of them,
    against 40% at random, and its advantage over chance has fallen to about
    {_high.iloc[0] / _rate:.1f} times. The two models are close at every capacity, so the choice
    between them matters much less than the choice of capacity.

    Whether the hospital should use either model depends on what an enrolment costs, how many
    readmissions the programme prevents among those enrolled, and who is left out, which the
    tables in Step 3 show for each capacity.

    ### The main idea, again

    When one class is rare, a classifier can be very accurate and still find almost none of the
    cases that matter. Precision and recall describe the cases it flags and the cases it finds,
    and the threshold sets the balance between them, so choosing a threshold is a decision about
    what each kind of error costs and who bears it.
    """)
    return


if __name__ == "__main__":
    app.run()
