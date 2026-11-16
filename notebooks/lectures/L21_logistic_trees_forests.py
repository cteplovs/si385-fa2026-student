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

    ## Session 21: Classification I: logistic regression, trees and forests

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, November 16, 2026

    The reading due today is James, Witten, Hastie, Tibshirani and Taylor, *An Introduction to
    Statistical Learning with Applications in Python*: section 4.3, *Logistic Regression*; section
    8.1, *The Basics of Decision Trees*; section 8.2.1, *Bagging*; and section 8.2.2, *Random
    Forests*.

    ---

    ### Today you will be able to

    - Fit a logistic regression, a decision tree and a random forest with scikit-learn, and compare
      their accuracy on rows they were not fitted to
    - Say what a logistic regression's coefficients and a tree's splits show about how each
      predicts, and why a tree grown without a limit predicts new rows worse than the rows it was
      fitted to
    - Judge whether one kind of classifier's advantage on a question is large enough to choose it
      over a model whose predictions are easier to explain

    ### The main idea

    Logistic regression predicts from one weighted sum of the columns, a decision tree from a
    sequence of thresholds, and a random forest from the class that most of many trees predict. Which of them
    predicts best depends on the data and the question, and which to use also depends on how much
    an advantage in accuracy is worth to the people who will rely on the predictions.

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Logistic regression | 5 |
    | Decision trees | 6 |
    | Random forests | 4 |
    | Today's question, in teams | 35 |
    | After the question: the four outcomes together | 10 |
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
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from matplotlib.colors import to_rgb
    from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree

    return (
        ColumnTransformer,
        DecisionTreeClassifier,
        LogisticRegression,
        OneHotEncoder,
        RandomForestClassifier,
        StandardScaler,
        export_text,
        make_pipeline,
        mo,
        np,
        pd,
        plot_tree,
        plt,
        to_rgb,
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


    def course_csv(name, **kwargs):
        """Read one of the course CSV files, passing any keyword arguments to pd.read_csv."""
        return pd.read_csv(_course_bytes(name), **kwargs)


    def course_parquet(name):
        """Read one of the course Parquet files."""
        return pd.read_parquet(_course_bytes(name))

    return course_csv, course_parquet


@app.cell
def palette():
    # Okabe and Ito's colours, which stay distinct for the common forms of colour blindness.
    CLASS_COLOURS = {"female": "#E69F00", "male": "#0072B2"}
    return (CLASS_COLOURS,)


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
    you can read every cell by opening `L21_logistic_trees_forests.py` in any text editor.

    Each technique ends with a section headed *The code on its own*. The sliders and plots above
    it call helper functions written for this notebook, which you will not have when you work on
    your own data. The code in those sections uses only pandas and scikit-learn, starts from a data
    frame, and does the computation without any controls, so that you can copy it into your project
    or another notebook.
    """)
    return


@app.cell(hide_code=True)
def logistic_intro(mo):
    mo.md(r"""
    ---
    ## Logistic regression

    We start with the Adelie penguins from sessions 19 and 20. Field researchers sometimes need to
    know a bird's sex when they cannot test its DNA, and male Adelies are on average larger than
    females, so we predict each penguin's sex from two measurements, its bill depth and its body
    mass. Gorman, Williams and Fraser sexed these penguins from blood samples, which lets us check
    every prediction. Because the sizes of males and females overlap, neither measurement separates
    them on its own.

    The file has four measurements of each penguin, and we use only two of them here so that we can
    draw each model on a flat plot, with one measurement on each axis and shading where the model
    predicts each sex, which is not possible with three or more. A researcher who wanted the best predictions would use all four, and at the end of the
    section on random forests we will.

    We set aside a quarter of the penguins as *test* rows before fitting anything. Every model is
    fitted to the other three quarters, the *training* rows, and its accuracy on the test rows is
    the share of penguins it has not been fitted to whose sex it predicts correctly.
    """)
    return


@app.cell
def load_penguins(course_csv, train_test_split):
    PENGUIN_COLUMNS = ["bill_depth_mm", "body_mass_g"]
    _all = course_csv("penguins.csv").dropna(subset=PENGUIN_COLUMNS + ["sex"])
    penguins = _all[_all["species"] == "Adelie"]
    penguins_train, penguins_test = train_test_split(
        penguins, test_size=0.25, stratify=penguins["sex"], random_state=0)
    penguins["sex"].value_counts()
    return PENGUIN_COLUMNS, penguins, penguins_test, penguins_train


@app.cell(hide_code=True)
def boundary_helper(CLASS_COLOURS, PENGUIN_COLUMNS, np, pd, penguins):
    def boundary_plot(model, title, ax):
        """Shade the region where `model` predicts each sex, and plot the penguins over it."""
        _x = np.linspace(penguins[PENGUIN_COLUMNS[0]].min() - 0.5,
                         penguins[PENGUIN_COLUMNS[0]].max() + 0.5, 300)
        _y = np.linspace(penguins[PENGUIN_COLUMNS[1]].min() - 200,
                         penguins[PENGUIN_COLUMNS[1]].max() + 200, 300)
        _xx, _yy = np.meshgrid(_x, _y)
        _grid = pd.DataFrame({PENGUIN_COLUMNS[0]: _xx.ravel(), PENGUIN_COLUMNS[1]: _yy.ravel()})
        _male = (model.predict(_grid) == "male").reshape(_xx.shape)
        ax.contourf(_xx, _yy, _male, levels=[-0.5, 0.5, 1.5],
                    colors=[CLASS_COLOURS["female"], CLASS_COLOURS["male"]], alpha=0.18)
        for _sex, _colour in CLASS_COLOURS.items():
            _rows = penguins[penguins["sex"] == _sex]
            ax.scatter(_rows[PENGUIN_COLUMNS[0]], _rows[PENGUIN_COLUMNS[1]], s=10,
                       color=_colour, label=_sex)
        ax.set_xlabel("bill depth (mm)")
        ax.set_ylabel("body mass (g)")
        ax.set_title(title, fontsize=10)
        ax.legend(fontsize=8, loc="upper right")

    def accuracy_line(model, train, test):
        """Return the model's accuracy on the training and test rows, as text."""
        return (f"training rows {model.score(train[PENGUIN_COLUMNS], train['sex']):.3f}, "
                f"test rows {model.score(test[PENGUIN_COLUMNS], test['sex']):.3f}")

    return accuracy_line, boundary_plot


@app.cell
def logistic_fit(
    LogisticRegression,
    PENGUIN_COLUMNS,
    StandardScaler,
    make_pipeline,
    penguins_train,
):
    penguins_logistic = make_pipeline(StandardScaler(), LogisticRegression()).fit(
        penguins_train[PENGUIN_COLUMNS], penguins_train["sex"])
    return (penguins_logistic,)


@app.cell(hide_code=True)
def logistic_plot(
    accuracy_line,
    boundary_plot,
    mo,
    penguins_logistic,
    penguins_test,
    penguins_train,
    plt,
):
    _fig, _ax = plt.subplots(figsize=(5.5, 4))
    boundary_plot(penguins_logistic, "Logistic regression", _ax)
    _fig.tight_layout()
    mo.vstack([_fig, mo.md(f"Accuracy: {accuracy_line(penguins_logistic, penguins_train, penguins_test)}")])
    return


@app.cell(hide_code=True)
def logistic_note(PENGUIN_COLUMNS, mo, np, penguins_logistic):
    _coef = penguins_logistic[-1].coef_[0]
    mo.md(rf"""
    Logistic regression computes a weighted sum of the standardized columns and converts it into a
    probability, and it predicts *male* wherever that probability is above one half, so the
    boundary between the two shaded regions is a straight line. The coefficients are
    {_coef[0]:.2f} for bill depth and {_coef[1]:.2f} for body mass. Each is the change in the
    log-odds of *male* for one standard deviation more of that measurement with the other held
    constant, so one more standard deviation of bill depth multiplies the odds by
    {np.exp(_coef[0]):.1f}, whatever the penguin's mass.

    The weighted sum is a single number for each penguin, so we can draw the model in one
    dimension as well. In the plot below, each penguin's weighted sum is on the horizontal axis
    and its sex on the vertical axis, at 1 for male and 0 for female, spread out a little so that
    the dots do not overlap. The curve is the logistic function, which converts the weighted sum
    into the probability of *male*.
    """)
    return


@app.cell(hide_code=True)
def logistic_curve(CLASS_COLOURS, PENGUIN_COLUMNS, mo, np, penguins, penguins_logistic, plt):
    _score = penguins_logistic.decision_function(penguins[PENGUIN_COLUMNS])
    _rng = np.random.default_rng(0)
    _fig, _ax = plt.subplots(figsize=(6.5, 3.8))
    for _sex, _colour in CLASS_COLOURS.items():
        _these = (penguins["sex"] == _sex).to_numpy()
        _y = (1.0 if _sex == "male" else 0.0) + _rng.uniform(-0.04, 0.04, _these.sum())
        _ax.scatter(_score[_these], _y, s=12, color=_colour, label=_sex, alpha=0.8)
    _x = np.linspace(_score.min() - 0.5, _score.max() + 0.5, 300)
    _ax.plot(_x, 1 / (1 + np.exp(-_x)), color="black", linewidth=1.5,
             label="probability of male")
    _ax.axhline(0.5, color="#999999", linestyle="--", linewidth=1)
    _ax.axvline(0, color="#999999", linestyle="--", linewidth=1)
    _ax.set_xlabel("weighted sum of the standardized measurements (log-odds of male)")
    _ax.set_ylabel("probability of male")
    _ax.set_title("Logistic regression, drawn in one dimension", fontsize=10)
    _ax.legend(fontsize=8, loc="center right")
    _fig.tight_layout()
    _wrong = int(((_score > 0) != (penguins["sex"] == "male").to_numpy()).sum())
    mo.vstack([_fig, mo.md(rf"""
    Despite its name, logistic regression is used here as a classifier. The regression part
    estimates the weights, and the model's output is a probability, which becomes a prediction
    only when we choose a threshold. scikit-learn's `predict` uses a threshold of one half, the
    horizontal dashed line, and the curve crosses it where the weighted sum is zero, at the
    vertical dashed line. Every penguin to the right of that line is predicted to be male, and every
    penguin to the left female, so the {_wrong} of the {len(penguins)} penguins that it
    misclassifies are the orange dots on the right and the blue dots on the left. The vertical
    line is the straight boundary in the plot above, drawn in one dimension, and in session 22 we
    will move the threshold.
    """)])
    return


@app.cell(hide_code=True)
def logistic_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we split the rows, fit the model to the training rows, and print its
    accuracy on the test rows and its coefficients. To use it on other data, you would put your own
    columns in place of `PENGUIN_COLUMNS` and your own outcome in place of `"sex"`.
    """)
    return


@app.cell
def logistic_code(
    LogisticRegression,
    PENGUIN_COLUMNS,
    StandardScaler,
    make_pipeline,
    penguins,
    train_test_split,
):
    # Uses: from sklearn.linear_model import LogisticRegression
    #       from sklearn.model_selection import train_test_split
    #       from sklearn.pipeline import make_pipeline
    #       from sklearn.preprocessing import StandardScaler
    _train, _test = train_test_split(penguins, test_size=0.25, stratify=penguins["sex"],
                                     random_state=0)
    _model = make_pipeline(StandardScaler(), LogisticRegression())
    _model.fit(_train[PENGUIN_COLUMNS], _train["sex"])
    print("test accuracy:", round(_model.score(_test[PENGUIN_COLUMNS], _test["sex"]), 3))
    print("coefficients:", dict(zip(PENGUIN_COLUMNS, _model[-1].coef_[0].round(2))))
    return


@app.cell(hide_code=True)
def tree_intro(mo):
    mo.md(r"""
    ---
    ## Decision trees

    A decision tree splits the training rows on one column at a time, at the threshold that leaves
    the two groups most nearly all one class, and then splits each group again, until it reaches
    the maximum depth. It predicts the majority class of the group a new row falls into, so its
    boundaries are made of horizontal and vertical lines. Please move the depth from 1 to 15 and
    watch the two accuracies below the plot.
    """)
    return


@app.cell(hide_code=True)
def tree_control(mo):
    penguins_depth = mo.ui.slider(1, 15, value=2, label="max_depth")
    return (penguins_depth,)


@app.cell
def tree_fit(DecisionTreeClassifier, PENGUIN_COLUMNS, penguins_depth, penguins_train):
    penguins_tree = DecisionTreeClassifier(max_depth=penguins_depth.value, random_state=0).fit(
        penguins_train[PENGUIN_COLUMNS], penguins_train["sex"])
    return (penguins_tree,)


@app.cell(hide_code=True)
def tree_plot(
    accuracy_line,
    boundary_plot,
    mo,
    penguins_depth,
    penguins_test,
    penguins_train,
    penguins_tree,
    plt,
):
    _fig, _ax = plt.subplots(figsize=(5.5, 4))
    boundary_plot(penguins_tree, f"Decision tree, max_depth = {penguins_depth.value}", _ax)
    _fig.tight_layout()
    mo.vstack([penguins_depth, _fig,
               mo.md(f"Accuracy: {accuracy_line(penguins_tree, penguins_train, penguins_test)}")])
    return


@app.cell(hide_code=True)
def tree_diagram(CLASS_COLOURS, mo, penguins_depth, penguins_tree, plot_tree, plt, to_rgb):
    if penguins_depth.value > 4:
        _out = mo.md(
            f"At max_depth = {penguins_depth.value} the tree has "
            f"{penguins_tree.get_n_leaves()} leaves, which are too many to draw legibly; the "
            "splits printed further down are the way to read a tree this deep.")
    else:
        _depth = penguins_depth.value
        _fig, _ax = plt.subplots(figsize=(min(14, 3 + 2 ** _depth), 1.3 * (_depth + 1) + 0.5))
        _boxes = plot_tree(
            penguins_tree, feature_names=["bill depth (mm)", "body mass (g)"],
            class_names=list(penguins_tree.classes_), impurity=False, proportion=True,
            filled=True, rounded=True, precision=2, fontsize=8 if _depth < 4 else 6, ax=_ax)
        # Shade each box in its majority sex's colour, darker where that sex is a larger share.
        # plot_tree also returns the unboxed True/False labels; the boxes are the nodes in order.
        _values = penguins_tree.tree_.value[:, 0, :]
        _boxes = [_b for _b in _boxes if _b.get_bbox_patch() is not None]
        for _node, _box in enumerate(_boxes):
            _share = _values[_node] / _values[_node].sum()
            _colour = to_rgb(CLASS_COLOURS[penguins_tree.classes_[_share.argmax()]])
            _strength = 0.7 * (2 * _share.max() - 1)
            _box.get_bbox_patch().set_facecolor(
                tuple(1 - _strength * (1 - _c) for _c in _colour))
        _ax.set_title(f"The same tree, max_depth = {_depth}", fontsize=10)
        _fig.tight_layout()
        _out = mo.vstack([
            mo.md("Each box gives the split, the share of the training rows that reach it, the "
                  "share of each sex among them, and the class the tree predicts there. Boxes "
                  "are shaded by the majority sex, more darkly where it is a larger share."),
            _fig])
    _out
    return


@app.cell(hide_code=True)
def tree_note(DecisionTreeClassifier, PENGUIN_COLUMNS, mo, pd, penguins_test, penguins_train):
    _rows = []
    for _depth in [1, 2, 3, 4, 6, 10, None]:
        _model = DecisionTreeClassifier(max_depth=_depth, random_state=0).fit(
            penguins_train[PENGUIN_COLUMNS], penguins_train["sex"])
        _rows.append({"max_depth": "no limit" if _depth is None else _depth,
                      "training rows": _model.score(penguins_train[PENGUIN_COLUMNS],
                                                    penguins_train["sex"]),
                      "test rows": _model.score(penguins_test[PENGUIN_COLUMNS],
                                                penguins_test["sex"])})
    _by_depth = pd.DataFrame(_rows).set_index("max_depth").round(3)
    mo.vstack([mo.md(r"""
    As the tree grows deeper, its accuracy on the training rows rises towards 1, because each
    further split can isolate a few more of them, while its accuracy on the test rows is highest
    for the shallowest trees and generally falls. The deep trees draw small boxes around single penguins, which fit the training rows
    but not new ones. ISLP calls this overfitting, and it is the reason trees are limited in depth
    or pruned:
    """), _by_depth])
    return


@app.cell(hide_code=True)
def tree_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we fit a tree of depth 3 and print its splits with `export_text`, which is
    the way to read a tree that is too deep to draw. Each line is a threshold, and each leaf gives
    the class the tree predicts for the rows that reach it.
    """)
    return


@app.cell
def tree_code(DecisionTreeClassifier, PENGUIN_COLUMNS, export_text, penguins_train):
    # Uses: from sklearn.tree import DecisionTreeClassifier, export_text
    _tree = DecisionTreeClassifier(max_depth=3, random_state=0)
    _tree.fit(penguins_train[PENGUIN_COLUMNS], penguins_train["sex"])
    print(export_text(_tree, feature_names=PENGUIN_COLUMNS))
    return


@app.cell(hide_code=True)
def forest_intro(mo):
    mo.md(r"""
    ---
    ## Random forests

    A random forest grows many deep trees, each on a bootstrap sample of the training rows and
    considering a random subset of the columns at each split, and predicts the class that most of
    the trees predict. The trees' errors differ from one another, so they partly cancel in the
    count, and the forest predicts new rows better than any one deep tree, although no single set of
    splits describes it.
    """)
    return


@app.cell
def forest_fit(PENGUIN_COLUMNS, RandomForestClassifier, penguins_train):
    penguins_forest = RandomForestClassifier(n_estimators=300, random_state=0).fit(
        penguins_train[PENGUIN_COLUMNS], penguins_train["sex"])
    return (penguins_forest,)


@app.cell(hide_code=True)
def forest_plot(
    accuracy_line,
    boundary_plot,
    mo,
    penguins_forest,
    penguins_test,
    penguins_train,
    plt,
):
    _fig, _ax = plt.subplots(figsize=(5.5, 4))
    boundary_plot(penguins_forest, "Random forest, 300 trees", _ax)
    _fig.tight_layout()
    mo.vstack([_fig, mo.md(f"Accuracy: {accuracy_line(penguins_forest, penguins_train, penguins_test)}")])
    return


@app.cell(hide_code=True)
def forest_note(mo, penguins_forest, penguins_logistic, penguins_test, PENGUIN_COLUMNS):
    _forest = penguins_forest.score(penguins_test[PENGUIN_COLUMNS], penguins_test["sex"])
    _logistic = penguins_logistic.score(penguins_test[PENGUIN_COLUMNS], penguins_test["sex"])
    mo.md(rf"""
    On these two measurements, the forest's accuracy on the test rows is {_forest:.3f} and logistic
    regression's is {_logistic:.3f}. With {len(penguins_test)} test penguins, one penguin is
    {1 / len(penguins_test):.3f} of the accuracy, so a difference of a penguin or two between
    the models is within what a different split of the rows could produce.
    """)
    return


@app.cell(hide_code=True)
def forest_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we fit the forest and print its accuracy on the test rows and its
    *feature importances*, which measure how much each column's splits reduce the impurity of the
    groups, averaged over the trees.
    """)
    return


@app.cell
def forest_code(PENGUIN_COLUMNS, RandomForestClassifier, penguins_test, penguins_train):
    # Uses: from sklearn.ensemble import RandomForestClassifier
    _forest = RandomForestClassifier(n_estimators=300, random_state=0)
    _forest.fit(penguins_train[PENGUIN_COLUMNS], penguins_train["sex"])
    print("test accuracy:", round(_forest.score(penguins_test[PENGUIN_COLUMNS],
                                                penguins_test["sex"]), 3))
    print("importances:", dict(zip(PENGUIN_COLUMNS, _forest.feature_importances_.round(2))))
    return


@app.cell(hide_code=True)
def four_intro(mo):
    mo.md(r"""
    ### All four measurements

    So far we have used two measurements so that every model could be drawn. With only two, the
    importances compare one measurement with the other, which the boundary plot already shows. We
    now fit both models to all four measurements, as a researcher would, for two reasons: to see
    how much the two measurements we left out improve the predictions, and to compare the
    importances of several columns, which is their purpose when the columns cannot all be drawn
    at once. In the cell
    below, we use the same training and test penguins as before, so the accuracies can be compared
    with those above.
    """)
    return


@app.cell
def four_fit(
    LogisticRegression,
    RandomForestClassifier,
    StandardScaler,
    make_pipeline,
    pd,
    penguins_test,
    penguins_train,
):
    # Uses: from sklearn.ensemble import RandomForestClassifier
    #       from sklearn.linear_model import LogisticRegression
    #       from sklearn.pipeline import make_pipeline
    #       from sklearn.preprocessing import StandardScaler
    ALL_MEASUREMENTS = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    _forest = RandomForestClassifier(n_estimators=300, random_state=0)
    _forest.fit(penguins_train[ALL_MEASUREMENTS], penguins_train["sex"])
    _logistic = make_pipeline(StandardScaler(), LogisticRegression())
    _logistic.fit(penguins_train[ALL_MEASUREMENTS], penguins_train["sex"])
    print("forest test accuracy:",
          round(_forest.score(penguins_test[ALL_MEASUREMENTS], penguins_test["sex"]), 3))
    print("logistic regression test accuracy:",
          round(_logistic.score(penguins_test[ALL_MEASUREMENTS], penguins_test["sex"]), 3))
    four_importances = pd.Series(_forest.feature_importances_, index=ALL_MEASUREMENTS,
                                 name="importance").sort_values(ascending=False).round(2)
    four_importances
    return (four_importances,)


@app.cell(hide_code=True)
def four_note(four_importances, mo):
    mo.md(rf"""
    The importances add up to 1, and splits on {four_importances.index[-1].replace("_", " ")}
    account for only {four_importances.iloc[-1]:.2f} of the reduction in impurity, so few of the
    forest's splits are on that measurement. An importance measures how much the forest used a column, not whether
    the column affects the outcome: two columns that measure nearly the same thing share the
    importance between them, and each can look less important than it would on its own.
    """)
    return


@app.cell(hide_code=True)
def question(mo):
    mo.md(r"""
    ---
    ## Today's question

    **Michigan's state government wants to predict all four outcomes for people it has not
    surveyed. Should it use the same kind of model for every outcome, and if so, which? Each of you
    will take one outcome before your team decides.**

    The data are the 2023 American Community Survey answers of 102,581 Michigan residents, from the
    pre-read. Each outcome is defined only for the people it applies to, so the four of you will
    fit models to four different groups of people. Your team's time is for talking through the
    problem, trying out ideas, and helping each other with the code. Each of you should run the
    code on your own laptop. Please take one outcome each, and if your team has three members,
    choose together which outcome to leave out. Your team should decide together what to
    recommend to the state, but the answer you submit is your own.

    In Step 1 you will choose your outcome, in Step 2 fit the three kinds of classifier to it, and
    in Step 3 look at what each model's predictions depend on. In Step 4 you will write your
    answer.
    """)
    return


@app.cell
def load_acs(course_parquet):
    acs = course_parquet("acs_michigan_2023.parquet")
    OUTCOMES = ["earns_over_50k", "employed", "public_coverage", "moved_last_year"]
    acs[OUTCOMES].agg(["count", "mean"]).round(3).rename(index={"count": "people",
                                                                 "mean": "share true"})
    return OUTCOMES, acs


@app.cell
def outcome_columns():
    # The columns used to predict each outcome, following the folktables task definitions.
    # The first list in each pair is numeric, and the second is categorical.
    _DIFFICULTIES = ["disability", "hearing_difficulty", "vision_difficulty",
                     "cognitive_difficulty"]
    _ORIGIN = ["citizenship", "born_in_us", "military_service", "sex", "race"]
    OUTCOME_COLUMNS = {
        "earns_over_50k": (["age", "schooling", "hours_per_week"],
                           ["worker_class", "marital_status", "occupation_group",
                            "relationship", "sex", "race"]),
        "employed": (["age", "schooling"],
                     ["marital_status", "relationship"] + _DIFFICULTIES + _ORIGIN),
        "public_coverage": (["age", "schooling", "personal_income"],
                            ["marital_status", "employment_status", "gave_birth_last_year"]
                            + _DIFFICULTIES + _ORIGIN),
        "moved_last_year": (["age", "schooling", "personal_income", "hours_per_week"],
                            ["marital_status", "employment_status", "relationship",
                             "worker_class"] + _DIFFICULTIES + _ORIGIN),
    }
    return (OUTCOME_COLUMNS,)


@app.cell
def step1_choose(OUTCOMES, mo):
    # Step 1: choose your outcome. Your team should take one each.
    answer_outcome = mo.ui.dropdown(OUTCOMES, value="earns_over_50k", label="Outcome")
    answer_outcome
    return (answer_outcome,)


@app.cell
def step2_data(OUTCOME_COLUMNS, acs, answer_outcome, train_test_split):
    # Step 2: we keep the people your outcome applies to and split them into training and test
    # rows. A missing category, such as the worker class of someone who has never worked, becomes
    # a category of its own.
    my_numeric, my_categorical = OUTCOME_COLUMNS[answer_outcome.value]
    _people = acs[acs[answer_outcome.value].notna()]
    my_X = _people[my_numeric + my_categorical].copy()
    my_X[my_categorical] = my_X[my_categorical].astype("string").fillna("not applicable")
    my_y = _people[answer_outcome.value].astype(bool)
    my_X_train, my_X_test, my_y_train, my_y_test = train_test_split(
        my_X, my_y, test_size=0.25, stratify=my_y, random_state=0)
    print(f"{len(_people):,} people: {len(my_X_train):,} training rows, "
          f"{len(my_X_test):,} test rows; {my_y.mean():.1%} true")
    return (
        my_X_test,
        my_X_train,
        my_categorical,
        my_numeric,
        my_y_test,
        my_y_train,
    )


@app.cell(hide_code=True)
def step2_controls(mo):
    answer_depth = mo.ui.slider(1, 30, value=6, label="max_depth, for the decision tree")
    return (answer_depth,)


@app.cell
def step2_fit(
    ColumnTransformer,
    DecisionTreeClassifier,
    LogisticRegression,
    OneHotEncoder,
    RandomForestClassifier,
    StandardScaler,
    answer_depth,
    make_pipeline,
    my_X_test,
    my_X_train,
    my_categorical,
    my_numeric,
    my_y_test,
    my_y_train,
    pd,
):
    # We give each category its own 0/1 column, and then fit the three kinds of classifier to the
    # training rows. Only logistic regression needs the numeric columns standardized, so the
    # trees' splits stay in years, hours and dollars.
    def _prepare(numeric):
        return ColumnTransformer([("numeric", numeric, my_numeric),
                                  ("categorical", OneHotEncoder(handle_unknown="ignore"),
                                   my_categorical)], verbose_feature_names_out=False)

    my_models = {
        "logistic regression": make_pipeline(_prepare(StandardScaler()),
                                             LogisticRegression(max_iter=2000)),
        f"decision tree, depth {answer_depth.value}": make_pipeline(
            _prepare("passthrough"),
            DecisionTreeClassifier(max_depth=answer_depth.value, random_state=0)),
        "random forest, 100 trees": make_pipeline(
            _prepare("passthrough"),
            RandomForestClassifier(n_estimators=100, min_samples_leaf=5, n_jobs=-1,
                                   random_state=0)),
    }
    for _model in my_models.values():
        _model.fit(my_X_train, my_y_train)

    _majority = my_y_train.mode()[0]
    my_accuracy = pd.DataFrame(
        [{"model": "always predict the majority",
          "training rows": (my_y_train == _majority).mean(),
          "test rows": (my_y_test == _majority).mean()}]
        + [{"model": _name,
            "training rows": _model.score(my_X_train, my_y_train),
            "test rows": _model.score(my_X_test, my_y_test)}
           for _name, _model in my_models.items()]).set_index("model").round(3)
    return my_accuracy, my_models


@app.cell(hide_code=True)
def step2_show(answer_depth, mo, my_accuracy):
    mo.vstack([answer_depth, my_accuracy, mo.md(r"""
    The table gives each model's accuracy on the training rows and on the test rows. Please try
    depths across the slider's range and note the depth at which the tree's accuracy on the test
    rows is highest, and how it compares with the forest there.
    """)])
    return


@app.cell
def step3_by_age(my_X_test, my_models, my_y_test, pd):
    # Step 3: each model's accuracy on the test rows within age bands, which shows where in the
    # population the models differ.
    _band = pd.cut(my_X_test["age"], [15, 25, 35, 45, 55, 65, 75, 95], right=False)
    pd.DataFrame({_name: (_model.predict(my_X_test) == my_y_test).groupby(_band, observed=True).mean()
                  for _name, _model in my_models.items()}).assign(
        people=_band.value_counts().sort_index()).round(3)
    return


@app.cell
def step3_coefficients(my_models, pd):
    # The logistic regression's ten largest coefficients in each direction. A numeric column's
    # coefficient is per standard deviation. Every category has its own column, so a category's
    # coefficient is best compared with those of the other categories of the same column.
    _logistic = my_models["logistic regression"]
    _coefs = pd.Series(_logistic[-1].coef_[0],
                       index=_logistic[0].get_feature_names_out()).sort_values()
    pd.concat([_coefs.head(10), _coefs.tail(10)]).round(2).rename("coefficient")
    return


@app.cell
def step3_tree(export_text, my_models):
    # The first three levels of your decision tree's splits.
    _name = next(_n for _n in my_models if _n.startswith("decision tree"))
    _tree = my_models[_name]
    print(export_text(_tree[-1], feature_names=list(_tree[0].get_feature_names_out()),
                      max_depth=3))
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy
    of `L21_logistic_trees_forests.py` to *AE 19* on Canvas before the end of class.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_accuracy(mo):
    mo.md(r"""
    **Your outcome, and how accurately each kind of classifier predicted it on the test rows, with the depths you tried for the tree**
    """)
    return


@app.cell
def step4_answer_accuracy(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_why(mo):
    mo.md(r"""
    **What the age bands, coefficients and splits show about why the models differ on your outcome, or why they do not**
    """)
    return


@app.cell
def step4_answer_why(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_team(mo):
    mo.md(r"""
    **With your teammates' outcomes alongside yours, whether the state should use the same kind of model for every outcome, and which, and why**
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
    ## After the question: the four outcomes together

    Below, we fit the three kinds of classifier to all four outcomes, with the tree at depth 6, and
    put their accuracy on the test rows side by side.
    """)
    return


@app.cell
def after_table(
    ColumnTransformer,
    DecisionTreeClassifier,
    LogisticRegression,
    OUTCOMES,
    OUTCOME_COLUMNS,
    OneHotEncoder,
    RandomForestClassifier,
    StandardScaler,
    acs,
    make_pipeline,
    pd,
    train_test_split,
):
    _rows = []
    for _outcome in OUTCOMES:
        _numeric, _categorical = OUTCOME_COLUMNS[_outcome]
        _people = acs[acs[_outcome].notna()]
        _X = _people[_numeric + _categorical].copy()
        _X[_categorical] = _X[_categorical].astype("string").fillna("not applicable")
        _y = _people[_outcome].astype(bool)
        _Xtr, _Xte, _ytr, _yte = train_test_split(_X, _y, test_size=0.25, stratify=_y,
                                                  random_state=0)
        _row = {"outcome": _outcome, "majority": (_yte == _ytr.mode()[0]).mean()}
        for _name, _clf in [("logistic", LogisticRegression(max_iter=2000)),
                            ("tree, depth 6", DecisionTreeClassifier(max_depth=6,
                                                                      random_state=0)),
                            ("forest", RandomForestClassifier(n_estimators=100,
                                                              min_samples_leaf=5, n_jobs=-1,
                                                              random_state=0))]:
            _prep = ColumnTransformer([("n", StandardScaler(), _numeric),
                                       ("c", OneHotEncoder(handle_unknown="ignore"),
                                        _categorical)])
            _row[_name] = make_pipeline(_prep, _clf).fit(_Xtr, _ytr).score(_Xte, _yte)
        _rows.append(_row)
    after_accuracy = pd.DataFrame(_rows).set_index("outcome").round(3)
    after_accuracy
    return (after_accuracy,)


@app.cell(hide_code=True)
def after_note(after_accuracy, mo):
    _gap = (after_accuracy["forest"] - after_accuracy["logistic"]) * 100
    _moved = after_accuracy.loc["moved_last_year"]
    _over = (_moved[["logistic", "tree, depth 6", "forest"]].max() - _moved["majority"]) * 100
    mo.md(rf"""
    The forest has the highest accuracy on every outcome, by between {_gap.min():.1f} and
    {_gap.max():.1f} percentage points over logistic regression. The gap is smallest for income,
    where a weighted sum of hours, schooling and occupation predicts nearly as well as the forest.
    It is larger for employment, where the share employed rises from the teens to the late
    twenties, stays level until the mid-fifties and then falls, which a single coefficient on age
    cannot describe and a tree's splits at two or three ages can. For moving, every model improves on always predicting *no* by at most
    {_over:.1f} points, because most young adults did not move, which is the subject of
    session 22.

    Whether the state should use the forest everywhere is a separate question from which model is
    most accurate. A gap of one percentage point is one more correct prediction in a hundred, and
    whether that is worth giving up coefficients that a caseworker or a court could read depends on
    what the predictions will be used for. A model used to decide who is offered a benefit has to
    be explained to the people it affects, and a model used only to plan how many forms to print
    does not.

    ### The main idea, again

    Logistic regression predicts from one weighted sum of the columns, a decision tree from a
    sequence of thresholds, and a random forest from the class that most of many trees predict. Which of them
    predicts best depends on the data and the question, and which to use also depends on how much
    an advantage in accuracy is worth to the people who will rely on the predictions.
    """)
    return


if __name__ == "__main__":
    app.run()
