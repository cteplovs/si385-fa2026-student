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

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 17: Principal components, and what a component means

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, November 2, 2026

    **Reading due today:** Géron, *Hands-On Machine Learning*, *Dimensionality Reduction*: ch. 8 in
    the third edition (*Scikit-Learn, Keras and TensorFlow*), or ch. 7 in the *Scikit-Learn and
    PyTorch* edition

    ---

    ### Today you will be able to

    - Say what PCA does when it projects points onto a line, and what the first component keeps
    - Fit PCA to a set of columns and read how much of the variance each component explains
    - Decide how many components to keep, and say why an elbow and a 95% threshold can disagree
    - Describe what a component means from its weights, and check the description against the
      people who score highest and lowest on it
    - Explain why a component's sign can flip, and why scaling matters even when every column is on
      the same scale

    ### Timing

    | Part | Minutes |
    |---|---:|
    | PCA with two columns, and how it differs from regression | 7 |
    | The data, and fitting PCA | 4 |
    | Reading a component | 4 |
    | Today's question, in teams | 35 |
    | What the question showed: signs and scaling | 10 |
    | RAT 13, round 2 | 10 |
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from sklearn.decomposition import PCA
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    return PCA, StandardScaler, make_pipeline, mo, np, pd, plt


@app.cell(hide_code=True)
def data_helper(pd):
    import urllib.request
    from io import BytesIO
    from pathlib import Path

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

    return (course_csv,)


@app.cell(hide_code=True)
def hidden_code_note(mo):
    mo.md(r"""
    ### Hidden and visible code

    The code you need to follow today's analysis is visible. Code that only draws a chart, loads a
    file or defines a helper function is hidden, and you see only its output. You are welcome to
    reveal any of it. To show one cell's code, hover over the cell, open its menu with the **⋯**
    button, and choose **Show code**. To show all of it at once, open the command palette with
    Ctrl+K (⌘K on a Mac) and choose **Show all code**. The notebook is also a plain Python file, so
    you can read every cell by opening `L17_pca.py` in any text editor.
    """)
    return


@app.cell(hide_code=True)
def two_columns_intro(mo):
    mo.md(r"""
    ---
    ## PCA with two columns

    Consider first a case small enough to draw. The points below are 200 people's heights and
    weights, made up for this illustration and standardized, so that both columns are measured in
    standard deviations. Tall people tend to be heavier, so the points lie along a diagonal.

    PCA looks for the line through the middle of the points that keeps them as spread out as
    possible when each point is projected onto it, that is, moved onto the line at a right angle.
    Please move the slider to turn the line, and watch how much of the variance the projected points
    keep.
    """)
    return


@app.cell(hide_code=True)
def body_data(np, pd):
    _rng = np.random.default_rng(17)
    _height = _rng.normal(170, 10, 200)
    _weight = 70 + 0.8 * (_height - 170) + _rng.normal(0, 6, 200)
    body = pd.DataFrame({"height_cm": _height.round(1), "weight_kg": _weight.round(1)})
    body_z = (body - body.mean()) / body.std()
    return (body_z,)


@app.cell(hide_code=True)
def angle_slider(mo):
    # Shown above the figure it turns, in the cell below.
    line_angle = mo.ui.slider(0, 175, step=5, value=0, label="Angle of the line (degrees)",
                              show_value=True)
    return (line_angle,)


@app.cell(hide_code=True)
def projection_plot(body_z, line_angle, mo, np, plt):
    _direction = np.array([np.cos(np.radians(line_angle.value)),
                           np.sin(np.radians(line_angle.value))])
    _points = body_z.to_numpy()
    _along = _points @ _direction
    _projected = np.outer(_along, _direction)
    _kept = _along.var() / _points.var(axis=0).sum()

    _fig, _ax = plt.subplots(figsize=(4.5, 4.5))
    for _p, _q in zip(_points, _projected):
        _ax.plot([_p[0], _q[0]], [_p[1], _q[1]], color="lightgrey", linewidth=0.6)
    _ax.scatter(_points[:, 0], _points[:, 1], s=10, label="People")
    _ax.scatter(_projected[:, 0], _projected[:, 1], s=10, color="tab:red",
                label="Projected onto the line")
    _ax.axline((0, 0), _direction, color="black", linewidth=1)
    _ax.set_xlim(-3.5, 3.5)
    _ax.set_ylim(-3.5, 3.5)
    _ax.set_aspect("equal")
    _ax.set_xlabel("Height (standardized)")
    _ax.set_ylabel("Weight (standardized)")
    _ax.set_title(f"The projected points keep {_kept:.0%} of the variance")
    _ax.legend(loc="upper left", fontsize="small")
    _fig.tight_layout()
    mo.vstack([line_angle, _fig])
    return


@app.cell
def two_column_pca(PCA, body_z, np):
    pca_2d = PCA(1).fit(body_z)
    pc1_angle = np.degrees(np.arctan2(pca_2d.components_[0, 1], pca_2d.components_[0, 0])) % 180
    body_scores = pca_2d.transform(body_z)[:, 0]
    return body_scores, pc1_angle, pca_2d


@app.cell(hide_code=True)
def two_column_note(mo, pc1_angle, pca_2d):
    _weights = pca_2d.components_[0]
    mo.md(f"""
    PCA's answer is the line at about {pc1_angle:.0f} degrees, which keeps
    {pca_2d.explained_variance_ratio_[0]:.0%} of the variance, and that line is the first principal
    component. Its weights are {_weights[0]:.2f} for height and {_weights[1]:.2f} for weight. They
    have the same sign, so height and weight move together on this component, which could fairly be
    called body size.

    Projecting onto the component turns two columns into one. Each person's position along the line
    is their score on the component, and the strip below shows those scores on their own: a
    one-dimensional version of the data that keeps most of the differences between people. The
    second component is the line at right angles to the first, and it holds what is left, which
    here is whether someone is heavier or lighter than their height would suggest.
    """)
    return


@app.cell(hide_code=True)
def scores_strip(body_scores, plt):
    _fig, _ax = plt.subplots(figsize=(7, 1.6))
    _ax.scatter(body_scores, [0] * len(body_scores), s=10, color="tab:red", alpha=0.6)
    _ax.set_yticks([])
    _ax.set_xlabel("Score on the first principal component")
    _ax.set_title("The same 200 people, in one dimension")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def regression_note(body_z, mo):
    _r = body_z["height_cm"].corr(body_z["weight_kg"])
    mo.md(f"""
    ### How PCA differs from regression

    A regression line through the same points answers a different question. Regressing weight on
    height treats weight as the outcome and height as the predictor, and it chooses the line that
    makes the vertical distances from the points to the line as small as possible. PCA has no
    outcome. It treats height and weight alike and chooses the line that makes the perpendicular
    distances as small as possible, which is the same as keeping as much of the spread along the
    line as possible.

    The figure below draws three lines through the same points. Because both columns are
    standardized, the regression of weight on height has a slope equal to the correlation,
    {_r:.2f}, so it is flatter than the PCA line. Regressing height on weight swaps the roles and
    gives a steeper line, while the PCA line stays the same whichever column you list first.
    Regression is the tool when one column is what you want to predict, and PCA is the tool when
    you want to summarize several columns without singling one out.
    """)
    return


@app.cell(hide_code=True)
def regression_plot(body_z, pca_2d, plt):
    _r = body_z["height_cm"].corr(body_z["weight_kg"])
    _pc1 = pca_2d.components_[0]
    _fig, _ax = plt.subplots(figsize=(4.5, 4.5))
    _ax.scatter(body_z["height_cm"], body_z["weight_kg"], s=10, color="lightgrey")
    _ax.axline((0, 0), _pc1, color="black", linewidth=1.5, label="PCA: first component")
    _ax.axline((0, 0), slope=_r, color="tab:blue", linestyle="--",
               label="Regression of weight on height")
    _ax.axline((0, 0), slope=1 / _r, color="tab:orange", linestyle=":",
               label="Regression of height on weight")
    _ax.set_xlim(-3.5, 3.5)
    _ax.set_ylim(-3.5, 3.5)
    _ax.set_aspect("equal")
    _ax.set_xlabel("Height (standardized)")
    _ax.set_ylabel("Weight (standardized)")
    _ax.set_title("One cloud of points, three lines")
    _ax.legend(loc="upper left", fontsize="small")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## The data

    Each row is one person, and each column is that person's rating of a genre of music, from 1
    (dislike) to 10 (like). There are 240 people and eleven genres. The ratings were generated for
    this session from a survey of an earlier class, so no row describes a real person, but the
    genres and the patterns between them come from that survey.

    Eleven columns are too many to look at together. PCA finds a few new columns, the principal
    components, that keep as much of the variation between people as possible, and today's question
    is what those components mean.
    """)
    return


@app.cell
def load_tastes(course_csv):
    tastes = course_csv("music_tastes.csv")
    ratings = tastes.drop(columns="respondent")
    # The .T transposes the table, so that the genres are the rows of the output.
    ratings.describe().T.round(1)
    return (ratings,)


@app.cell(hide_code=True)
def fit_intro(mo):
    mo.md(r"""
    ---
    ## Fitting PCA

    PCA looks for the direction along which the people differ most, then the direction at right
    angles to it along which they differ most of what is left, and so on, one component for each
    column. We standardize the ratings first, for a reason we will come back to after the question.

    The table shows the share of the variance that each component explains, and the running total.
    """)
    return


@app.cell
def fit_pca(PCA, StandardScaler, make_pipeline, pd, ratings):
    pca_model = make_pipeline(StandardScaler(), PCA()).fit(ratings)
    pca = pca_model.named_steps["pca"]
    # Names for the components, "PC1" to "PC11", to label the rows and columns of the tables below.
    # PCA keeps one component for each column, and n_components_ is how many it kept.
    COMPONENTS = [f"PC{_i}" for _i in range(1, pca.n_components_ + 1)]
    variance = pd.DataFrame({
        "explained": pca.explained_variance_ratio_,
        "cumulative": pca.explained_variance_ratio_.cumsum(),
    }, index=COMPONENTS)
    variance.round(2)
    return COMPONENTS, pca, pca_model, variance


@app.cell(hide_code=True)
def variance_plot(plt, variance):
    _fig, _ax = plt.subplots(figsize=(7, 4))
    _ax.bar(variance.index, variance["explained"], label="Explained by the component")
    _ax.plot(variance.index, variance["cumulative"], marker="o", color="black",
             label="Cumulative")
    _ax.axhline(0.95, linestyle="--", color="grey", label="95% of the variance")
    _ax.set_ylabel("Share of the variance")
    _ax.set_title("Variance explained by each principal component")
    _ax.legend(loc="center right")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def variance_note(mo, variance):
    _for_95 = int((variance["cumulative"] >= 0.95).argmax()) + 1
    mo.md(f"""
    Two of the ways Géron offers to choose how many components to keep can be read from this
    chart. One is to keep enough for a large share of the variance, such as 95%, which here takes
    **{_for_95}** components. The other is to look for the elbow, where the curve stops rising quickly. Where is the elbow in
    the chart above, and why might the two answers differ?
    """)
    return


@app.cell(hide_code=True)
def weights_intro(mo):
    mo.md(r"""
    ---
    ## Reading a component

    Each component is a weighted combination of the genres. The weights are in the fitted model's
    `components_`, one row for each component, and the table below shows the first three.

    Please read the weights of a component together rather than one at a time. Genres with the same
    sign move together on that component, genres with opposite signs are set against each other,
    and genres with weights near zero play little part in it.
    """)
    return


@app.cell
def weights_table(COMPONENTS, pca, pd, ratings):
    weights = pd.DataFrame(pca.components_.T, index=ratings.columns, columns=COMPONENTS)
    weights.iloc[:, :3].round(2)
    return (weights,)


@app.cell(hide_code=True)
def weight_plotter(plt, weights):
    def plot_weights(component):
        """Draw one component's weights as bars, sorted from most negative to most positive."""
        _sorted = weights[component].sort_values()
        _fig, _ax = plt.subplots(figsize=(6, 4))
        _ax.barh(_sorted.index, _sorted,
                 color=["tab:red" if _w < 0 else "tab:blue" for _w in _sorted])
        _ax.axvline(0, color="black", linewidth=0.8)
        _ax.set_xlabel("Weight")
        _ax.set_title(f"Weights of {component}")
        _fig.tight_layout()
        return _fig

    return (plot_weights,)


@app.cell(hide_code=True)
def demo_picker(COMPONENTS, mo):
    # Shown above the chart it controls, in the cell below.
    demo_component = mo.ui.dropdown(COMPONENTS[:4], value="PC1", label="Component")
    return (demo_component,)


@app.cell(hide_code=True)
def demo_weights(demo_component, mo, plot_weights):
    mo.vstack([demo_component, plot_weights(demo_component.value)])
    return


@app.cell(hide_code=True)
def scores_intro(mo):
    mo.md(r"""
    Each person also gets a score on each component, from the fitted model's `transform`. The
    people who score highest and lowest on a component are the best check on a description of it:
    if PC1 means what you think it means, their ratings should show it.
    """)
    return


@app.cell
def scores(COMPONENTS, pca_model, pd, ratings):
    component_scores = pd.DataFrame(pca_model.transform(ratings), columns=COMPONENTS,
                                    index=ratings.index)
    component_scores.head().round(2)
    return (component_scores,)


@app.cell(hide_code=True)
def extremes_helper(component_scores, ratings):
    def extremes(component, n=5):
        """The n people who score highest on a component and the n who score lowest."""
        _order = component_scores[component].sort_values(ascending=False).index
        _rows = list(_order[:n]) + list(_order[-n:])
        return (ratings.loc[_rows]
                .assign(score=component_scores.loc[_rows, component].round(2)))

    return (extremes,)


@app.cell(hide_code=True)
def demo_extremes(demo_component, extremes):
    extremes(demo_component.value)
    return


@app.cell(hide_code=True)
def question(mo):
    mo.md(r"""
    ---
    ## Today's question

    **How do these people's tastes in music differ? Each of you will describe one component, and
    your team will decide how many components it takes to describe the differences.**

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop. Please take the components in
    order, one each: the first of you describes PC1, the next PC2, and so on, so that your team
    covers PC1 up to as many components as it has members. Your team should decide together how many
    components to keep, but the answer you submit is your own.

    In Step 1 you will choose your component, in Step 2 read its weights, and in Step 3 check your
    reading against the people at either end. Step 4 asks for your answer.
    """)
    return


@app.cell
def step1_choose(COMPONENTS, mo):
    # Step 1: choose your component. Your team takes them in order, one each: PC1, PC2, PC3,
    # and so on.
    answer_component = mo.ui.dropdown(COMPONENTS, value="PC1", label="Component")
    answer_component
    return (answer_component,)


@app.cell
def step2_weights(answer_component, plot_weights):
    # Step 2: which genres move together on this component, and which are set against each other?
    plot_weights(answer_component.value)
    return


@app.cell
def step3_extremes(answer_component, extremes):
    # Step 3: do the people at the top and the bottom fit your description? The first five rows
    # are the highest scores, and the last five are the lowest.
    extremes(answer_component.value)
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L17_pca.py` to *AE 15* on Canvas before the end of class.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_meaning(mo):
    mo.md(r"""
    **What your component means, in terms of the people who score high and low on it**
    """)
    return


@app.cell
def step4_answer_meaning(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_evidence(mo):
    mo.md(r"""
    **How much of the variance your component explains, and whether the people at either end bore out your description**
    """)
    return


@app.cell
def step4_answer_evidence(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_number(mo):
    mo.md(r"""
    **With your teammates' components alongside yours, how many components your team would keep, and why**
    """)
    return


@app.cell
def step4_answer_number(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_limitation(mo):
    mo.md(r"""
    **One limitation of your description**
    """)
    return


@app.cell
def step4_answer_limitation(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def signs_intro(mo):
    mo.md(r"""
    ---
    ## After the question: a component's sign

    We split the people into two random halves and fit PCA to each half separately. Both halves come from the same 240 people, so their components should describe the same tastes.
    """)
    return


@app.cell
def halves(PCA, StandardScaler, make_pipeline, np, pd, ratings):
    _order = np.random.default_rng(2).permutation(len(ratings))
    _half = len(ratings) // 2
    _first = make_pipeline(StandardScaler(), PCA(3)).fit(ratings.iloc[_order[:_half]])
    _second = make_pipeline(StandardScaler(), PCA(3)).fit(ratings.iloc[_order[_half:]])
    half_weights = pd.DataFrame({
        "PC2, first half": _first.named_steps["pca"].components_[1],
        "PC2, second half": _second.named_steps["pca"].components_[1],
    }, index=ratings.columns)
    half_weights.round(2)
    return (half_weights,)


@app.cell(hide_code=True)
def signs_note(half_weights, mo, np):
    _agree = np.sign(half_weights.iloc[:, 0] @ half_weights.iloc[:, 1]) > 0
    _seen = ("In this run the two halves give PC2 the same signs. Try another seed in the "
             "cell above, and you will soon find a pair that does not."
             if _agree else
             "In this run every weight on PC2 has changed sign between the two halves, while the "
             "sizes stay much the same.")
    mo.md(f"""
    {_seen} Both versions describe the same axis, and only the direction along it has flipped, so
    the genres that move together still move together. That is why a description of a component
    should say which genres are set against which, rather than relying on the sign of a single
    weight.
    """)
    return


@app.cell(hide_code=True)
def scaling_intro(mo):
    mo.md(r"""
    ---
    ## After the question: scaling

    Every genre is rated on the same 1-to-10 scale, so it might seem that standardizing changes
    nothing. The standard deviations below show why it does: some genres divide people far more
    than others.
    """)
    return


@app.cell
def spreads(ratings):
    ratings.std().sort_values(ascending=False).round(2)
    return


@app.cell
def scaled_vs_raw(PCA, pd, ratings, weights):
    _raw = PCA().fit(ratings)
    raw_vs_scaled = pd.DataFrame({
        "PC3, standardized": weights["PC3"],
        "PC3, not standardized": _raw.components_[2],
    }, index=ratings.columns)
    raw_vs_scaled.round(2)
    return


@app.cell(hide_code=True)
def scaling_note(mo):
    mo.md(r"""
    Without standardizing, PCA treats a genre with a larger spread as more important, because it
    contributes more variance. Please compare the two columns above and say which genre the
    unstandardized PC3 is mostly about.
    """)
    return


@app.cell(hide_code=True)
def round_two(mo):
    mo.md(r"""
    ---
    ## RAT 13, round 2

    Please open *RAT 13, round 2* on Canvas now. You will have one attempt and 10 minutes, and it
    will close at 9:50.
    """)
    return


if __name__ == "__main__":
    app.run()
