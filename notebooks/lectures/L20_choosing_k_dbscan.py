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

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 20: Clustering II: choosing K, and density-based clustering

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, November 11, 2026

    The reading due today is Géron, *Hands-On Machine Learning with Scikit-Learn and PyTorch*,
    chapter 8: *Finding the optimal number of clusters*, *Limits of k-Means*, *DBSCAN*, and the
    paragraph on agglomerative clustering.

    ---

    ### Today you will be able to

    - Read an inertia curve and a silhouette score, and say what each shows about a choice of K
    - Say which rows DBSCAN labels as core instances, cluster members and anomalies, and how its
      two settings change the result
    - Judge whether a clustering describes groups in the data, and say what that judgement leaves
      open about whether the clustering is useful

    ### The main idea

    k-means returns as many clusters as you ask for, whether or not the data contain groups. The
    elbow and the silhouette score measure how well separated those clusters are, and DBSCAN finds
    clusters only where the rows are dense. None of the three can show whether a clustering is
    useful, because that depends on what it will be used for.

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Choosing K: the elbow | 4 |
    | Choosing K: the silhouette score | 6 |
    | DBSCAN | 6 |
    | Today's question, in teams | 35 |
    | After the question: the three methods together | 7 |
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.datasets import make_moons
    from sklearn.metrics import silhouette_samples, silhouette_score
    from sklearn.preprocessing import StandardScaler

    return (
        DBSCAN,
        KMeans,
        StandardScaler,
        make_moons,
        mo,
        np,
        pd,
        plt,
        silhouette_samples,
        silhouette_score,
    )


@app.cell(hide_code=True)
def data_helper(pd):
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    REMOTE = ("https://raw.githubusercontent.com/"
              "cteplovs/si385-fa2026-student/main/data/")


    def course_csv(name, **kwargs):
        """Read one of the course data files, passing any keyword arguments to pd.read_csv.

        The copy in the course folder is the one to prefer, and it is what you get if you are
        running this the documented way. The fallback to the public repository is there so that
        the notebook also runs on molab, provided you have a network.
        """
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_csv(local, **kwargs)
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as response:
            return pd.read_csv(BytesIO(response.read()), **kwargs)

    return (course_csv,)


@app.cell
def palette():
    # Okabe and Ito's colours, which stay distinct for the common forms of colour blindness.
    CLUSTER_COLOURS = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00",
                       "#F0E442", "#000000"]
    return (CLUSTER_COLOURS,)


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
    you can read every cell by opening `L20_choosing_k_dbscan.py` in any text editor.

    Each technique ends with a section headed *The code on its own*. The sliders and plots above
    it call helper functions written for this notebook, which you will not have when you work on
    your own data. The code in those sections uses only pandas and scikit-learn, starts from a data
    frame or an array, and does the computation without any controls, so that you can copy it into
    your project or another notebook.
    """)
    return


@app.cell(hide_code=True)
def elbow_intro(mo):
    mo.md(r"""
    ---
    ## Choosing K: the elbow

    We start with Monday's penguins, standardized, because we know that they contain three species
    and can check each method against them. For each K from 1 to 8, we fit k-means from ten starts
    and record its inertia, which is scikit-learn's name for the total within-cluster variation.
    """)
    return


@app.cell
def load_penguins(StandardScaler, course_csv):
    MEASUREMENTS = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    penguins = course_csv("penguins.csv").dropna(subset=MEASUREMENTS).reset_index(drop=True)
    penguins_X = StandardScaler().fit_transform(penguins[MEASUREMENTS])
    return MEASUREMENTS, penguins, penguins_X


@app.cell(hide_code=True)
def scan_helper(KMeans, pd, silhouette_score):
    def scan_k(X, ks=range(1, 9)):
        """Fit k-means at each K from ten starts, and return its inertia and silhouette score."""
        rows = []
        for k in ks:
            model = KMeans(n_clusters=k, n_init=10, random_state=0).fit(X)
            score = silhouette_score(X, model.labels_) if k > 1 else float("nan")
            rows.append({"K": k, "inertia": round(model.inertia_),
                         "silhouette": round(score, 3)})
        return pd.DataFrame(rows).set_index("K")

    return (scan_k,)


@app.cell
def penguins_scan(penguins_X, scan_k):
    penguins_by_k = scan_k(penguins_X)
    penguins_by_k
    return (penguins_by_k,)


@app.cell(hide_code=True)
def elbow_plot(penguins_by_k, plt):
    _fig, _ax = plt.subplots(figsize=(5.5, 3.6))
    _ax.plot(penguins_by_k.index, penguins_by_k["inertia"], marker="o", color="#0072B2")
    _ax.set_xlabel("K")
    _ax.set_ylabel("inertia")
    _ax.set_title("Inertia by K, penguins standardized", fontsize=10)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def elbow_note(mo, penguins_by_k):
    _drops = -penguins_by_k["inertia"].diff()
    mo.md(rf"""
    The inertia falls at every K, because more centroids can always sit closer to the rows, so the
    K with the lowest inertia is always the largest one we try. The elbow is the K after which
    another cluster lowers the inertia much less than the one before it did. Going from 1 to 2
    clusters lowers the inertia by {_drops[2]:.0f}, from 2 to 3 by {_drops[3]:.0f}, and from 3 to 4
    by {_drops[4]:.0f}, so the clearest elbow is at 2, with a smaller one at 3, and choosing
    between them is a judgement about the curve.
    """)
    return


@app.cell(hide_code=True)
def elbow_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the same inertias without the plot or the helper function,
    starting from the data frame. To use it on other data, for example in your project, you would
    put your own numeric columns in place of `penguins[MEASUREMENTS]`.
    """)
    return


@app.cell
def elbow_code(KMeans, MEASUREMENTS, StandardScaler, penguins):
    # Uses: from sklearn.cluster import KMeans
    #       from sklearn.preprocessing import StandardScaler
    _X = StandardScaler().fit_transform(penguins[MEASUREMENTS])
    for _k in range(1, 9):
        _model = KMeans(n_clusters=_k, n_init=10, random_state=0).fit(_X)
        print(_k, round(_model.inertia_))
    return


@app.cell(hide_code=True)
def silhouette_intro(mo):
    mo.md(r"""
    ---
    ## Choosing K: the silhouette score

    For each row, the *silhouette coefficient* compares *a*, the row's mean distance to the other
    rows in its own cluster, with *b*, its mean distance to the rows of the next closest cluster,
    which is the other cluster with the smallest mean distance:

    $$s = \frac{b - a}{\max(a, b)}$$

    It runs from −1 to +1. A row near +1 is much closer to its own cluster than to any other, a
    row near 0 is about as close to the next cluster as to its own, and a row below 0 is closer to
    another cluster than to its own. The *silhouette score* is the mean over all the rows. The
    table above has it for each K, and the diagram below shows every penguin's coefficient at the
    K you choose, sorted within each cluster, with the score as a dashed line.
    """)
    return


@app.cell(hide_code=True)
def silhouette_helper(CLUSTER_COLOURS, KMeans, np, plt, silhouette_samples):
    def silhouette_diagram(X, k, title):
        """Draw the silhouette diagram for k-means at K = k, as in Géron's Figure 8-9."""
        labels = KMeans(n_clusters=k, n_init=10, random_state=0).fit_predict(X)
        values = silhouette_samples(X, labels)
        fig, ax = plt.subplots(figsize=(5.5, 4.2))
        bottom = 0
        for c in range(k):
            these = np.sort(values[labels == c])
            ax.fill_betweenx(np.arange(bottom, bottom + len(these)), 0, these,
                             color=CLUSTER_COLOURS[c], alpha=0.85)
            ax.text(-0.05, bottom + len(these) / 2, str(c + 1), ha="right", va="center",
                    fontsize=9)
            bottom += len(these) + 4
        ax.axvline(values.mean(), color="black", linestyle="--", linewidth=1)
        ax.set_xlim(-0.3, 1)
        ax.set_yticks([])
        ax.set_xlabel("silhouette coefficient")
        ax.set_ylabel("rows, by cluster")
        ax.set_title(f"{title}, K = {k}: silhouette score {values.mean():.2f}", fontsize=10)
        fig.tight_layout()
        return fig

    return (silhouette_diagram,)


@app.cell(hide_code=True)
def penguins_k_control(mo):
    penguins_k = mo.ui.slider(2, 8, value=3, label="K")
    return (penguins_k,)


@app.cell(hide_code=True)
def penguins_silhouette(mo, penguins_X, penguins_k, silhouette_diagram):
    mo.vstack([penguins_k,
               silhouette_diagram(penguins_X, penguins_k.value, "Penguins standardized")])
    return


@app.cell(hide_code=True)
def silhouette_note(mo, penguins_by_k):
    mo.md(rf"""
    The score is highest at K = 2 ({penguins_by_k.loc[2, "silhouette"]:.2f}), not at the three
    species ({penguins_by_k.loc[3, "silhouette"]:.2f}), because the Adelie and Chinstrap penguins
    are close to each other in these measurements, so a clustering that puts them together has
    well-separated clusters. The silhouette score measures separation, and it does not show which
    groups matter for a question. Both scores are well above zero, and in the silhouette diagram
    at K = 3, nearly every penguin is closer to its own cluster than to any other. Please set K to
    2, 3 and 4 and compare the clusters' sizes and how many of each cluster's penguins fall short
    of the dashed line, which the reading uses to choose between values of K with similar scores.
    """)
    return


@app.cell(hide_code=True)
def silhouette_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the silhouette score for each K, and then, for one K, each
    cluster's size, its mean coefficient and the number of its rows below zero, which are the
    numbers the silhouette diagram shows.
    """)
    return


@app.cell
def silhouette_code(
    KMeans,
    MEASUREMENTS,
    StandardScaler,
    pd,
    penguins,
    silhouette_samples,
    silhouette_score,
):
    # Uses: from sklearn.cluster import KMeans
    #       from sklearn.metrics import silhouette_samples, silhouette_score
    #       from sklearn.preprocessing import StandardScaler
    _X = StandardScaler().fit_transform(penguins[MEASUREMENTS])
    for _k in range(2, 9):
        _labels = KMeans(n_clusters=_k, n_init=10, random_state=0).fit_predict(_X)
        print(_k, round(silhouette_score(_X, _labels), 3))

    _labels = KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(_X)
    _coefficients = pd.Series(silhouette_samples(_X, _labels))
    _coefficients.groupby(_labels).agg(
        rows="size", mean="mean", below_zero=lambda _s: (_s < 0).sum()).round(2)
    return


@app.cell(hide_code=True)
def dbscan_intro(mo):
    mo.md(r"""
    ---
    ## DBSCAN

    DBSCAN does not take a number of clusters. For each row, it counts the rows within a distance
    `eps` of it, including the row itself, and a row with at least `min_samples` of them is a
    *core instance*. All the rows within `eps` of a core instance belong to its cluster, so a
    chain of neighbouring core instances forms one cluster, whatever its shape. A row that is not a
    core instance and has no core instance within `eps` is an anomaly, labelled −1.

    The points below were generated for this demonstration: two interlocking crescents of 300
    points, with 20 points scattered at random. On the left, k-means at K = 2 divides them with a
    straight boundary, because each point goes to the nearer of two centroids. On the right,
    DBSCAN finds the crescents at the settings below. Core instances are the larger dots, the
    other members of a cluster are the smaller ones, and anomalies are grey crosses. Please move
    `eps` down to 0.05 and then up to 0.5.
    """)
    return


@app.cell
def moons(make_moons, np):
    _rng = np.random.default_rng(3)
    _X, _ = make_moons(n_samples=300, noise=0.07, random_state=4)
    moons_X = np.vstack([_X, _rng.uniform([-1.5, -1], [2.5, 1.5], (20, 2))])
    return (moons_X,)


@app.cell(hide_code=True)
def moons_controls(mo):
    moons_eps = mo.ui.slider(0.05, 0.5, step=0.01, value=0.15, label="eps")
    moons_min = mo.ui.slider(2, 20, value=5, label="min_samples")
    return moons_eps, moons_min


@app.cell
def moons_fit(DBSCAN, moons_X, moons_eps, moons_min):
    moons_dbscan = DBSCAN(eps=moons_eps.value, min_samples=moons_min.value).fit(moons_X)
    return (moons_dbscan,)


@app.cell(hide_code=True)
def moons_plot(
    CLUSTER_COLOURS,
    KMeans,
    mo,
    moons_X,
    moons_dbscan,
    moons_eps,
    moons_min,
    np,
    plt,
):
    _fig, (_left, _right) = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
    _km = KMeans(n_clusters=2, n_init=10, random_state=0).fit_predict(moons_X)
    for _c in range(2):
        _left.scatter(*moons_X[_km == _c].T, s=12, color=CLUSTER_COLOURS[_c])
    _left.set_title("k-means, K = 2", fontsize=10)
    _labels = moons_dbscan.labels_
    _core = np.zeros(len(moons_X), dtype=bool)
    _core[moons_dbscan.core_sample_indices_] = True
    for _c in range(_labels.max() + 1):
        _colour = CLUSTER_COLOURS[_c % len(CLUSTER_COLOURS)]
        _right.scatter(*moons_X[(_labels == _c) & _core].T, s=22, color=_colour)
        _right.scatter(*moons_X[(_labels == _c) & ~_core].T, s=7, color=_colour)
    _right.scatter(*moons_X[_labels == -1].T, s=18, marker="x", color="#999999")
    _n = _labels.max() + 1
    _right.set_title(f"DBSCAN: {_n} cluster{'s' if _n != 1 else ''}, "
                     f"{(_labels == -1).sum()} anomalies", fontsize=10)
    _fig.tight_layout()
    mo.vstack([mo.hstack([moons_eps, moons_min], justify="start"), _fig])
    return


@app.cell(hide_code=True)
def dbscan_note(mo):
    mo.md(r"""
    At small values of `eps`, few points have enough neighbours to be core instances, so most are
    anomalies and the crescents break into small clusters. At large values, the core instances of
    the two crescents come within `eps` of each other, and the chain joins them into one cluster.
    Most of the scattered points are labelled as anomalies only in the range between. DBSCAN has no `predict()`
    method, so to place a new row we would train a classifier on the clusters it found, as the
    reading describes.
    """)
    return


@app.cell(hide_code=True)
def dbscan_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we run DBSCAN once and count its clusters, anomalies and core instances,
    and then repeat the count for several values of `eps`, which is how you would look for a
    range of settings that gives a stable result on your own data.
    """)
    return


@app.cell
def dbscan_code(DBSCAN, moons_X):
    # Uses: from sklearn.cluster import DBSCAN
    _dbscan = DBSCAN(eps=0.15, min_samples=5).fit(moons_X)
    _labels = _dbscan.labels_
    print("clusters:", _labels.max() + 1)
    print("anomalies:", (_labels == -1).sum())
    print("core instances:", len(_dbscan.core_sample_indices_))
    print()

    for _eps in [0.05, 0.1, 0.15, 0.2, 0.3, 0.4]:
        _labels = DBSCAN(eps=_eps, min_samples=5).fit_predict(moons_X)
        print(f"eps {_eps}: {_labels.max() + 1} clusters, {(_labels == -1).sum()} anomalies")
    return


@app.cell(hide_code=True)
def question(mo):
    mo.md(r"""
    ---
    ## Today's question

    **A music streaming service wants to divide these listeners into segments and recommend
    different playlists to each segment. Should it, and if so, how many segments should it use?
    Each of you will use one method before your team decides.**

    The listeners are the 240 people from sessions 17 and 18, who rated eleven genres from 1 to 10.
    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop. There are three methods:
    k-means on the original ratings, k-means on the standardized ratings, and DBSCAN on the
    original ratings. Please take them in order, one each, and if your team has four or five
    members, the others should take k-means on the original ratings again and describe a
    different K. Your team should decide together what to recommend to the service, but the
    answer you submit is your own.

    In Step 1 you will choose your method, in Step 2 run it, and in Step 3 describe the segments it
    gives. In Step 4 you will write your answer.
    """)
    return


@app.cell
def load_music(course_csv):
    music = course_csv("music_tastes.csv").set_index("respondent")
    GENRES = list(music.columns)
    music.agg(["mean", "std"]).round(1)
    return GENRES, music


@app.cell
def step1_choose(mo):
    # Step 1: choose your method. Your team should take them in order, one each.
    answer_method = mo.ui.dropdown(["k-means, original ratings",
                                    "k-means, standardized ratings",
                                    "DBSCAN, original ratings"],
                                   value="k-means, original ratings",
                                   label="Method")
    answer_method
    return (answer_method,)


@app.cell
def step2_data(StandardScaler, answer_method, music):
    # Step 2: we prepare the ratings for your method.
    if answer_method.value == "k-means, standardized ratings":
        my_X = StandardScaler().fit_transform(music)
    else:
        my_X = music.to_numpy(dtype=float)
    return (my_X,)


@app.cell(hide_code=True)
def step2_controls(mo):
    answer_k = mo.ui.slider(2, 8, value=2, label="K, for k-means")
    answer_eps = mo.ui.slider(2.5, 6.5, step=0.1, value=4.0, label="eps, for DBSCAN")
    answer_min = mo.ui.slider(3, 20, value=5, label="min_samples, for DBSCAN")
    return answer_eps, answer_k, answer_min


@app.cell
def step2_fit(
    DBSCAN,
    KMeans,
    answer_eps,
    answer_k,
    answer_method,
    answer_min,
    music,
    my_X,
    np,
):
    # We fit your method and label each listener with a segment, numbered from the largest.
    # DBSCAN's anomalies are labelled -1.
    if answer_method.value.startswith("DBSCAN"):
        _labels = DBSCAN(eps=answer_eps.value, min_samples=answer_min.value).fit_predict(my_X)
    else:
        _labels = KMeans(n_clusters=answer_k.value, n_init=10,
                         random_state=0).fit_predict(my_X)
    _sizes = np.bincount(_labels[_labels >= 0]) if (_labels >= 0).any() else np.array([])
    _rank = {old: new for new, old in enumerate(np.argsort(-_sizes, kind="stable"), start=1)}
    my_music = music.copy()
    my_music["segment"] = [_rank.get(_l, -1) for _l in _labels]
    my_music["segment"].value_counts().sort_index().rename("listeners")
    return (my_music,)


@app.cell(hide_code=True)
def step2_show(
    answer_eps,
    answer_k,
    answer_method,
    answer_min,
    mo,
    my_X,
    plt,
    scan_k,
    silhouette_diagram,
):
    if answer_method.value.startswith("DBSCAN"):
        _out = mo.vstack([mo.hstack([answer_eps, answer_min], justify="start"), mo.md(r"""
        The table above gives the number of listeners in each segment, with the anomalies as −1.
        Please try values of `eps` across the slider's range and note how many segments of more
        than a few listeners appear at each.
        """)])
    else:
        _scan = scan_k(my_X)
        _fig, (_a, _b) = plt.subplots(1, 2, figsize=(9, 3.2))
        _a.plot(_scan.index, _scan["inertia"], marker="o", color="#0072B2")
        _a.set_xlabel("K")
        _a.set_ylabel("inertia")
        _b.plot(_scan.index[1:], _scan["silhouette"].iloc[1:], marker="o", color="#E69F00")
        _b.set_xlabel("K")
        _b.set_ylabel("silhouette score")
        _b.set_ylim(0, 0.6)
        _fig.suptitle(answer_method.value, fontsize=10)
        _fig.tight_layout()
        _out = mo.vstack([_scan.T, _fig, answer_k,
                          silhouette_diagram(my_X, answer_k.value, answer_method.value)])
    _out
    return


@app.cell
def step3_profile(GENRES, music, my_music):
    # Step 3: each segment's mean rating of each genre, minus the mean of all 240 listeners, so
    # that a positive number means the segment likes the genre more than listeners in general.
    (my_music.groupby("segment")[GENRES].mean() - music[GENRES].mean()).round(1).assign(
        listeners=my_music["segment"].value_counts().sort_index())
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy
    of `L20_choosing_k_dbscan.py` to *AE 18* on Canvas before the end of class.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_method(mo):
    mo.md(r"""
    **What your method showed about whether these listeners form groups, with the numbers from your runs**
    """)
    return


@app.cell
def step4_answer_method(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_segments(mo):
    mo.md(r"""
    **The segments at the setting you would report: what each segment's listeners like, and how sharply they differ from the next segment**
    """)
    return


@app.cell
def step4_answer_segments(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_team(mo):
    mo.md(r"""
    **With your teammates' methods alongside yours, what you would recommend to the service, and why**
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
    ## After the question: the three methods together

    Below, we put the silhouette scores for the music ratings beside the penguins' scores, and
    count DBSCAN's segments on the original ratings across a range of `eps`.
    """)
    return


@app.cell
def after_silhouettes(StandardScaler, music, pd, penguins_by_k, scan_k):
    pd.DataFrame({
        "penguins, standardized": penguins_by_k["silhouette"],
        "music, original ratings": scan_k(music.to_numpy(dtype=float))["silhouette"],
        "music, standardized": scan_k(StandardScaler().fit_transform(music))["silhouette"],
    }).drop(index=1)
    return


@app.cell
def after_dbscan(DBSCAN, music, np, pd):
    _X = music.to_numpy(dtype=float)
    _rows = []
    for _eps in np.arange(3.0, 6.01, 0.5):
        _labels = DBSCAN(eps=_eps, min_samples=5).fit_predict(_X)
        _sizes = sorted(np.bincount(_labels[_labels >= 0]).tolist(), reverse=True) \
            if (_labels >= 0).any() else []
        _rows.append({"eps": round(_eps, 1), "segments": len(_sizes),
                      "listeners in each": _sizes, "anomalies": int((_labels == -1).sum())})
    pd.DataFrame(_rows).set_index("eps")
    return


@app.cell(hide_code=True)
def after_note(mo):
    mo.md(r"""
    The penguins' scores are more than twice the music scores at every K. The music scores are
    highest at K = 2 and generally lower at larger K, and their inertia curves have no clear elbow.
    At small values of `eps`, DBSCAN labels most listeners as anomalies and finds a few small
    segments, and at larger values it puts nearly all of them in one segment, so at no setting
    does it find two segments of similar size. The ratings were generated from three continuous
    tastes with no groups, and all three methods are consistent with that.

    The methods measure whether the listeners form separate groups, and whether the service should
    segment them is a different question. A clothing company sells small, medium and large although
    people's sizes form no groups, because three sizes fit most people well enough, and a service might
    divide listeners along a continuum for the same reason. The case against is that listeners near
    a boundary would get playlists chosen for people at the far end of their segment. Which of the
    two weighs more depends on what the service wants the segments for.

    ### The main idea, again

    k-means returns as many clusters as you ask for, whether or not the data contain groups. The
    elbow and the silhouette score measure how well separated those clusters are, and DBSCAN finds
    clusters only where the rows are dense. None of the three can show whether a clustering is
    useful, because that depends on what it will be used for.
    """)
    return


if __name__ == "__main__":
    app.run()
