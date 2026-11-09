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

    ## Session 19: Clustering I: k-means, distance, and scaling

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, November 9, 2026

    The reading due today is James, Witten, Hastie, Tibshirani and Taylor, *An Introduction to
    Statistical Learning with Applications in Python*, sections 12.4.1 and 12.4.3.

    ---

    ### Today you will be able to

    - Say what k-means does at each step, and why its result can depend on where it starts
    - Explain how the units of the columns change the distances k-means uses, and what standardizing
      changes
    - Describe the clusters k-means finds in terms of the data, and say what a clustering cannot show

    ### The main idea

    k-means divides the rows into K clusters so that the rows in each cluster are as close as
    possible to their cluster's mean. Closeness is measured in the units of the columns, so the units
    determine which differences count, and standardizing is a decision about which differences
    should count.

    ### Timing

    | Part | Minutes |
    |---|---:|
    | k-means, step by step | 8 |
    | Different starts, different results | 4 |
    | The penguins | 3 |
    | Distance and units | 7 |
    | Today's question, in teams | 35 |
    | After the question: what standardizing changed | 5 |
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    return KMeans, StandardScaler, mo, np, pd, plt


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


@app.cell(hide_code=True)
def palette():
    # Okabe and Ito's colours, which stay distinct for the common forms of colour blindness.
    CLUSTER_COLOURS = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]
    return (CLUSTER_COLOURS,)


@app.cell(hide_code=True)
def hidden_code_note(mo):
    mo.md(r"""
    ### Hidden and visible code

    The code you need to follow today's analysis is visible. Code that only draws a chart, loads a
    file or defines a helper function is hidden, and you see only its output. You are welcome to
    reveal any of it. To show or hide one cell's code, click the cell and press Ctrl+H (⌘H on a
    Mac), or hover over the cell, open its menu with the **⋯** button, and choose
    **Show code**. To show all of it at once, open the command palette with
    Ctrl+K (⌘K on a Mac) and choose **Show all code**. The notebook is also a plain Python file, so
    you can read every cell by opening `L19_kmeans.py` in any text editor.
    """)
    return


@app.cell(hide_code=True)
def steps_intro(mo):
    mo.md(r"""
    ---
    ## k-means, step by step

    The points below were generated for this demonstration, 150 of them in two columns, `x` and
    `y`, so that we can watch k-means work in a plot, and we use K = 3. The algorithm is the one in
    the reading (Algorithm 12.2):

    1. Give each point a cluster at random.
    2. Repeat until no point changes cluster:
        - (a) compute each cluster's *centroid*, the mean of its points in each column;
        - (b) move each point to the cluster whose centroid is closest.

    Please move the step slider from left to right. The start slider changes the random
    assignment in step 1.
    """)
    return


@app.cell
def toy(np):
    # Three groups of 50 points around three centres.
    _rng = np.random.default_rng(12)
    _centres = np.array([[0, 0], [4, 1], [1.5, 4]])
    toy_X = np.vstack([_c + _rng.normal(0, 1.3, (50, 2)) for _c in _centres])
    return (toy_X,)


@app.cell(hide_code=True)
def kmeans_helper(np):
    def run_kmeans(X, k, start):
        """Algorithm 12.2 from a random assignment. Returns the steps and the final objective."""
        rng = np.random.default_rng(start)
        labels = rng.integers(0, k, len(X))
        history = [("Step 1: each point is given a cluster at random", labels, None)]
        centres = None
        for i in range(1, 51):
            centres = np.array([X[labels == j].mean(axis=0) if (labels == j).any() else centres[j]
                                for j in range(k)])
            history.append((f"Iteration {i}, step 2(a): each centroid moves to the mean of its "
                            "points", labels, centres))
            new = ((X[:, None, :] - centres[None]) ** 2).sum(axis=2).argmin(axis=1)
            moved = int((new != labels).sum())
            moves = "1 point moves" if moved == 1 else f"{moved} points move"
            history.append((f"Iteration {i}, step 2(b): {moves} to a closer centroid",
                            new, centres))
            if moved == 0:
                break
            labels = new
        objective = sum(((X[labels == j] - X[labels == j].mean(axis=0)) ** 2).sum()
                        for j in range(k) if (labels == j).any())
        return history, float(objective)

    return (run_kmeans,)


@app.cell(hide_code=True)
def steps_start_control(mo):
    steps_start = mo.ui.slider(0, 19, value=0, label="Start")
    return (steps_start,)


@app.cell
def steps_run(run_kmeans, steps_start, toy_X):
    steps_history, steps_objective = run_kmeans(toy_X, 3, steps_start.value)
    return steps_history, steps_objective


@app.cell(hide_code=True)
def steps_step_control(mo, steps_history):
    steps_step = mo.ui.slider(0, len(steps_history) - 1, value=0, label="Step")
    return (steps_step,)


@app.cell(hide_code=True)
def steps_plot(
    CLUSTER_COLOURS,
    mo,
    np,
    plt,
    steps_history,
    steps_objective,
    steps_start,
    steps_step,
    toy_X,
):
    _caption, _labels, _centres = steps_history[steps_step.value]
    _fig, _ax = plt.subplots(figsize=(5.5, 4.6))
    _ax.scatter(toy_X[:, 0], toy_X[:, 1], s=18,
                c=[CLUSTER_COLOURS[_j] for _j in _labels])
    if _centres is not None:
        _ax.scatter(_centres[:, 0], _centres[:, 1], s=260, marker="X",
                    c=CLUSTER_COLOURS[:3], edgecolors="black", linewidths=1.5)
    _ax.set_title(_caption, fontsize=10)
    _ax.set_xlabel("x")
    _ax.set_ylabel("y")
    _last = steps_step.value == len(steps_history) - 1
    _note = (f"No point changed cluster, so the algorithm stopped. The total within-cluster "
             f"variation is {steps_objective:.0f}." if _last else "")
    mo.vstack([mo.hstack([steps_start, steps_step], justify="start"), _fig, mo.md(_note)])
    return


@app.cell(hide_code=True)
def steps_note(mo):
    mo.md(r"""
    The colours of the clusters have no order; they are labels. Neither step 2(a) nor step 2(b) can
    raise the *total within-cluster variation*, the sum of the squared distances from each point to
    its cluster's centroid, which is the quantity k-means minimizes. The reading's objective
    (12.17) is twice this sum, so the two rank clusterings in the same order.
    """)
    return


@app.cell(hide_code=True)
def starts_intro(mo):
    mo.md(r"""
    ---
    ## Different starts, different results

    The algorithm stops when no point moves, which is a *local* optimum: no single step can improve
    it, but a different start might have reached a better one. Below, we run the algorithm from each
    of the 20 starts on the slider above and count how many stopped at each value.
    """)
    return


@app.cell
def starts_table(pd, run_kmeans, toy_X):
    _starts = pd.DataFrame({"start": range(20),
                           "total within-cluster variation":
                               [round(run_kmeans(toy_X, 3, _s)[1]) for _s in range(20)]})
    _starts["total within-cluster variation"].value_counts().rename("starts")
    return


@app.cell(hide_code=True)
def starts_note(mo):
    mo.md(r"""
    Please find a start on the slider that ends at the larger value, and look at the clusters it
    found. Because a start can end at a worse clustering, the reading recommends running k-means
    many times from different starts and keeping the run with the smallest objective. scikit-learn
    does this for you: `KMeans(n_init=10)` runs ten starts and keeps the best. Its starts are chosen
    more carefully than at random, so poor results are rarer, but they can still happen.
    """)
    return


@app.cell(hide_code=True)
def seeds_note(mo):
    mo.md(r"""
    ### Random numbers and seeds

    The start slider sets the *seed* of the random number generator that gives each point its first
    cluster. Arithmetic alone cannot produce truly random numbers, so Python and NumPy use
    *pseudo-random* number generators, which compute a long sequence of numbers that pass
    statistical tests of randomness from a single starting value, the seed. The same seed always
    gives the same sequence, which is why start 7 ends at the same clustering every time you choose
    it, on any laptop.

    In NumPy, `np.random.default_rng(seed)` creates a generator, and each call such as
    `rng.integers(...)` or `rng.normal(...)` takes the next numbers from its sequence. Without a
    seed, NumPy takes one from the operating system, so each run gives different numbers; Python's
    built-in `random` module works in the same way, with `random.seed(...)`. scikit-learn takes the
    seed as `random_state`, so `KMeans(n_init=10, random_state=0)` uses the same ten starts every
    time, and your clusters will match a teammate's on the same version and K.

    In the table below, each of ten points is given a first cluster, 0, 1 or 2, by three generators,
    two with seed 7 and one with seed 8.
    """)
    return


@app.cell
def seeds_demo(np, pd):
    _first = np.random.default_rng(7).integers(0, 3, 10)
    _again = np.random.default_rng(7).integers(0, 3, 10)
    _other = np.random.default_rng(8).integers(0, 3, 10)
    pd.DataFrame({"seed 7": _first, "seed 7 again": _again, "seed 8": _other}).T
    return


@app.cell(hide_code=True)
def penguins_intro(mo):
    mo.md(r"""
    ---
    ## The penguins

    The data are 342 penguins measured by Kristen Gorman and the Palmer Station Long Term Ecological
    Research program on three islands near Palmer Station, Antarctica, between 2007 and 2009. Each
    row is one penguin, with its bill length, bill depth and flipper length in millimetres and its
    body mass in grams. The file also records each penguin's species, but k-means is not given it:
    we will use it only afterwards, to compare with the clusters. We drop the two penguins with no
    measurements immediately after we read the file.
    """)
    return


@app.cell
def load_penguins(course_csv):
    penguins = (course_csv("penguins.csv")
                .dropna(subset=["bill_length_mm", "bill_depth_mm", "flipper_length_mm",
                                "body_mass_g"])
                .reset_index(drop=True))
    MEASUREMENTS = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    penguins[MEASUREMENTS].agg(["mean", "std"]).round(1)
    return MEASUREMENTS, penguins


@app.cell(hide_code=True)
def penguins_note(mo):
    mo.md(r"""
    The table gives the mean and standard deviation of each measurement. Body mass, in grams, has a
    standard deviation of about 800, and the three measurements in millimetres have standard
    deviations between 2 and 14.
    """)
    return


@app.cell(hide_code=True)
def species_list(penguins):
    sorted_species = sorted(penguins["species"].unique())
    return (sorted_species,)


@app.cell(hide_code=True)
def distance_intro(mo, sorted_species):
    species_a = mo.ui.dropdown(sorted_species, value="Adelie", label="First species")
    species_b = mo.ui.dropdown(sorted_species, value="Gentoo", label="Second species")
    mo.md(f"""
    ---
    ## Distance and units

    k-means measures how far apart two penguins are with the straight-line distance across all the
    columns it is given: it squares the difference in each column, adds the squares, and takes the
    square root. The table below shows a typical penguin of each of two species, with the median of
    each measurement in that species, and the share of the squared distance between them that each
    measurement contributes, first in the original units and then after standardizing.

    {species_a} {species_b}
    """)
    return species_a, species_b


@app.cell
def distance_table(MEASUREMENTS, pd, penguins, species_a, species_b):
    _a = penguins[penguins["species"] == species_a.value][MEASUREMENTS].median()
    _b = penguins[penguins["species"] == species_b.value][MEASUREMENTS].median()
    _difference = _a - _b
    _in_sds = _difference / penguins[MEASUREMENTS].std()
    pd.DataFrame({
        species_a.value: _a,
        species_b.value: _b,
        "difference": _difference,
        "share, original units": (_difference ** 2 / (_difference ** 2).sum()).round(2),
        "difference in SDs": _in_sds.round(2),
        "share, standardized": (_in_sds ** 2 / (_in_sds ** 2).sum()).round(2),
    })
    return


@app.cell(hide_code=True)
def distance_note(mo):
    mo.md(r"""
    In the original units, a difference of 10 grams counts the same as a difference of 10
    millimetres, so body mass, whose values vary by hundreds of grams, contributes almost all of the
    distance between most pairs of penguins. The exception is pairs of about the same mass, such as
    the typical Adelie and Chinstrap penguins, which is why clusters in the original units mix
    those two species. After standardizing, each difference is measured in standard deviations, so a
    difference counts by how unusual it is among these penguins. The reading's example is shoppers
    who bought socks and computers (Figure 12.16): on the raw counts, socks dominate the distances.
    Please try the other pairs of species.
    """)
    return


@app.cell(hide_code=True)
def question(mo):
    mo.md(r"""
    ---
    ## Today's question

    **What groups do these penguins' measurements show? Each of you will cluster one version of the
    data before your team compares them.**

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop. There are four versions: all
    four measurements, or only the three in millimetres, each in the original units or
    standardized. Please take them in order, one each, so that your team covers as many versions as
    it has members, and if your team has more than four members, the fifth should take the first
    version again with a different K. Your team should decide together what groups the
    measurements show, but the answer you submit is your own.

    In Step 1 you will choose your version, in Step 2 cluster it and look at the clusters, and in
    Step 3 compare the clusters with the species. In Step 4 you will write your answer.
    """)
    return


@app.cell
def step1_choose(mo):
    # Step 1: choose your version. Your team should take them in order, one each.
    answer_version = mo.ui.dropdown(["All four measurements, original units",
                                     "All four measurements, standardized",
                                     "The three in millimetres, original units",
                                     "The three in millimetres, standardized"],
                                    value="All four measurements, original units",
                                    label="Version")
    answer_version
    return (answer_version,)


@app.cell(hide_code=True)
def step2_control(mo):
    answer_k = mo.ui.slider(2, 6, value=3, label="Number of clusters, K")
    return (answer_k,)


@app.cell
def step2_fit(KMeans, MEASUREMENTS, StandardScaler, answer_k, answer_version, penguins):
    # Step 2: we fit k-means to your version from ten starts and keep the best. Start with K = 3,
    # then try 2 and 4.
    _columns = MEASUREMENTS if answer_version.value.startswith("All") else MEASUREMENTS[:3]
    my_penguins = penguins.copy()
    _X = my_penguins[_columns].to_numpy(dtype=float)
    if answer_version.value.endswith("standardized"):
        _X = StandardScaler().fit_transform(_X)
    _labels = KMeans(n_clusters=answer_k.value, n_init=10, random_state=0).fit_predict(_X)
    # We number the clusters from the lightest to the heaviest, so that the numbers mean something.
    _order = my_penguins.groupby(_labels)["body_mass_g"].mean().rank().astype(int)
    my_penguins["cluster"] = _order.loc[_labels].to_numpy()
    my_penguins.groupby("cluster")[MEASUREMENTS].mean().round(1).assign(
        penguins=my_penguins["cluster"].value_counts().sort_index())
    return (my_penguins,)


@app.cell(hide_code=True)
def step2_plot(CLUSTER_COLOURS, answer_k, answer_version, mo, my_penguins, plt):
    _fig, _ax = plt.subplots(figsize=(6, 4.5))
    for _c in range(1, answer_k.value + 1):
        _rows = my_penguins[my_penguins["cluster"] == _c]
        _ax.scatter(_rows["bill_length_mm"], _rows["bill_depth_mm"], s=16, alpha=0.8,
                    color=CLUSTER_COLOURS[_c - 1], label=f"cluster {_c}")
    _ax.set_xlabel("bill_length_mm")
    _ax.set_ylabel("bill_depth_mm")
    _ax.legend(frameon=False)
    _ax.set_title(f"Bill length and depth, coloured by cluster\n"
                  f"(clusters from {answer_version.value.lower()}, K = {answer_k.value})",
                  fontsize=10)
    _fig.tight_layout()
    mo.vstack([answer_k, mo.md(r"""
    The plot shows two of the four measurements, bill length and bill depth, whichever version you
    clustered, and your clusters were computed from all the columns in your version. We plot this
    pair because the three species form clearly separate groups in it, so you can see whether your
    clusters follow those groups; of the other five pairs, only bill length with flipper length
    separates the species as well.
    """), _fig])
    return


@app.cell
def step3_species(my_penguins, pd):
    # Step 3: we count the penguins of each species in each cluster. k-means was not given the
    # species.
    pd.crosstab(my_penguins["cluster"], my_penguins["species"])
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with what you saw in your own runs. Then save the notebook and upload your copy of
    `L19_kmeans.py` to *AE 17* on Canvas before the end of class.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_clusters(mo):
    mo.md(r"""
    **Each of your clusters at the K you chose: what its penguins are like, and how it compares with the species**
    """)
    return


@app.cell
def step4_answer_clusters(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_k(mo):
    mo.md(r"""
    **What changed when you tried other values of K, and which K you would report**
    """)
    return


@app.cell
def step4_answer_k(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_units(mo):
    mo.md(r"""
    **With your teammates' versions alongside yours, what dropping body mass and standardizing changed, and which version you would use to answer the question, and why**
    """)
    return


@app.cell
def step4_answer_units(mo):
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
    ## After the question: what standardizing changed

    Below, we cluster the penguins on all four measurements both ways at K = 3 and count the
    species in each cluster. In the original units, body mass contributes almost all of most
    distances, so the clusters divide the penguins mainly by mass, and Adelie and Chinstrap penguins,
    which weigh about the same, share clusters. After standardizing, the bill measurements count as
    much as mass, and each species falls mostly in a cluster of its own.
    """)
    return


@app.cell
def after_compare(KMeans, MEASUREMENTS, StandardScaler, pd, penguins):
    _kmeans = KMeans(n_clusters=3, n_init=10, random_state=0)
    _original = penguins[MEASUREMENTS]
    _standardized = StandardScaler().fit_transform(_original)
    _original_clusters = _kmeans.fit_predict(_original)
    _standardized_clusters = _kmeans.fit_predict(_standardized)
    pd.concat({"original units": pd.crosstab(_original_clusters, penguins["species"]),
               "standardized": pd.crosstab(_standardized_clusters, penguins["species"])},
              axis=1).rename_axis("cluster")
    return


@app.cell(hide_code=True)
def after_note(mo):
    mo.md(r"""
    Because the species are known here, we can check whether the clusters match them. With most
    data there is no such column to check against, and k-means returns K clusters whether or not
    the data contain groups. On Wednesday we will cluster data in which we do not know whether
    there are groups, and ask how many clusters there are and whether a clustering describes
    anything real in the data.

    ### The main idea, again

    k-means divides the rows into K clusters so that the rows in each cluster are as close as
    possible to their cluster's mean. Closeness is measured in the units of the columns, so the units
    determine which differences count, and standardizing is a decision about which differences
    should count.
    """)
    return


if __name__ == "__main__":
    app.run()
