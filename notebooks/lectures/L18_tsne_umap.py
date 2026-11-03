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

    ## Session 18: t-SNE, UMAP, and how embedding plots mislead

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, November 4, 2026

    The reading due today is Géron, *Hands-On Machine Learning with Scikit-Learn and PyTorch*, ch. 7,
    *Dimensionality Reduction*, from *LLE* to the end of the chapter.

    ---

    ### Today you will be able to

    - Say what t-SNE is for, and what its perplexity changes
    - Explain why the size of a clump in a t-SNE map, and the distance between two clumps, cannot be
      read as the size of a group or the distance between groups
    - Check whether a group in a t-SNE map is in the data, by changing the seed and the perplexity
      and by colouring the map
    - Decide whether a set of people fall into distinct groups, and defend the decision

    ### The main idea

    t-SNE shows which rows are similar to which when there are too many columns to plot, and it can
    show groups that PCA cannot. Before you believe a group it shows, check that the group comes back
    with other seeds and at other perplexities, and that the colour changes sharply at its edge.

    ### Timing

    | Part | Minutes |
    |---|---:|
    | What t-SNE is for | 5 |
    | Perplexity | 6 |
    | Data with no groups | 6 |
    | Three checks | 2 |
    | The music data | 4 |
    | Today's question, in teams | 35 |
    | After the question: generating the data | 7 |

    UMAP, a second method for making the same kind of map, is in an optional section at the end.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    from sklearn.datasets import load_digits
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.preprocessing import StandardScaler

    return PCA, StandardScaler, TSNE, load_digits, mo, np, pd, plt


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
    reveal any of it. To show or hide one cell's code, click the cell and press Ctrl+H (⌘H on a
    Mac), or hover over the cell, open its menu with the **⋯** button, and choose
    **Show code**. To show all of it at once, open the command palette with
    Ctrl+K (⌘K on a Mac) and choose **Show all code**. The notebook is also a plain Python file, so
    you can read every cell by opening `L18_tsne_umap.py` in any text editor.
    """)
    return


@app.cell(hide_code=True)
def digits_intro(mo):
    mo.md(r"""
    ---
    ## What t-SNE is for

    scikit-learn includes 1,797 small images of handwritten digits, each 8 pixels by 8. Each image is
    stored as one row of 64 columns, the grey level of each pixel, and `load_digits` also returns the
    digit that each image shows. One image of each digit is shown below.
    """)
    return


@app.cell
def digits(load_digits):
    digits_X, digits_y = load_digits(return_X_y=True)
    digits_X.shape
    return digits_X, digits_y


@app.cell(hide_code=True)
def digit_examples(digits_X, digits_y, plt):
    _fig, _axes = plt.subplots(1, 10, figsize=(10, 1.4))
    for _digit, _ax in enumerate(_axes):
        _ax.imshow(digits_X[digits_y == _digit][0].reshape(8, 8), cmap="gray_r")
        _ax.set_title(str(_digit))
        _ax.axis("off")
    _fig
    return


@app.cell(hide_code=True)
def pixels_intro(mo):
    mo.md(r"""
    Consider the first image in the data, a 0. Each of its 64 pixels has a grey level from 0 (white)
    to 16 (black), and the figure below shows that number in each pixel's square.
    """)
    return


@app.cell(hide_code=True)
def pixels_plot(digits_X, plt):
    _image = digits_X[0].reshape(8, 8)
    _fig, _ax = plt.subplots(figsize=(4, 4))
    _ax.imshow(_image, cmap="gray_r", vmin=0, vmax=16)
    for _r in range(8):
        for _c in range(8):
            _v = int(_image[_r, _c])
            _ax.text(_c, _r, str(_v), ha="center", va="center", fontsize=10,
                     color="white" if _v > 8 else "black")
    _ax.set_xticks([])
    _ax.set_yticks([])
    _fig
    return


@app.cell(hide_code=True)
def pixels_row_intro(mo):
    mo.md(r"""
    Reading the squares row by row, left to right and from the top row down, gives the 64 numbers
    that make up the image's row in the data, printed below. Columns 0 to 7 contain the top row of
    pixels, columns 8 to 15 the second row, and so on down to columns 56 to 63, the bottom row.
    """)
    return


@app.cell
def pixels_row(digits_X):
    digits_X[0]
    return


@app.cell(hide_code=True)
def pixels_reshape_note(mo):
    mo.md(r"""
    To draw an image, we reverse the process: `digits_X[0].reshape(8, 8)` rearranges the 64 numbers
    into eight rows of eight.
    """)
    return


@app.cell(hide_code=True)
def digits_maps_intro(mo):
    mo.md(r"""
    Sixty-four columns are too many to plot, so we reduce them to two, once with PCA and once with
    t-SNE. Neither method is given the digits, which we use only afterwards, to colour each point
    and to write each digit at the middle of its points.
    """)
    return


@app.cell
def digits_maps(PCA, TSNE, digits_X):
    digits_pca = PCA(2).fit_transform(digits_X)
    digits_tsne = TSNE(perplexity=30, init="random", random_state=0).fit_transform(digits_X)
    return digits_pca, digits_tsne


@app.cell(hide_code=True)
def digits_label_helper(np, plt):
    def draw_digits(ax, coords, labels, title):
        """Scatter a map coloured by digit, with each digit written at the median of its points."""
        ax.scatter(coords[:, 0], coords[:, 1], c=labels, cmap="tab10", s=5, vmin=0, vmax=9)
        for digit in range(10):
            x, y = np.median(coords[labels == digit], axis=0)
            ax.text(x, y, str(digit), fontsize=14, weight="bold", ha="center", va="center")
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])

    return (draw_digits,)


@app.cell(hide_code=True)
def digits_plot(digits_pca, digits_tsne, digits_y, draw_digits, plt):
    _fig, _axes = plt.subplots(1, 2, figsize=(10, 4.6))
    draw_digits(_axes[0], digits_pca, digits_y, "PCA")
    draw_digits(_axes[1], digits_tsne, digits_y, "t-SNE, perplexity 30")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def digits_note(mo):
    mo.md(r"""
    In PCA's map most of the digits overlap, because the two directions along which the images vary
    most do not separate them. t-SNE places each image near the images that look most like it, so
    almost every digit forms its own clump. t-SNE is used to see which rows are similar to which when
    there are too many columns to plot, and to find groups that PCA cannot show in two dimensions.
    """)
    return


@app.cell(hide_code=True)
def digits_select_intro(mo):
    mo.md(r"""
    To look at the images in any part of the t-SNE map, please drag a box around a clump in the map
    below, or hold Shift and drag to draw an outline. Underneath the map, you will see a count of
    each digit among the images you selected, followed by up to 40 of the images themselves.
    """)
    return


@app.cell(hide_code=True)
def digits_selectable(digits_tsne, digits_y, draw_digits, mo, plt):
    _fig, _ax = plt.subplots(figsize=(6, 5.5))
    draw_digits(_ax, digits_tsne, digits_y, "t-SNE, perplexity 30")
    digits_selection = mo.ui.matplotlib(_ax)
    digits_selection
    return (digits_selection,)


@app.cell
def digits_selected(digits_selection, digits_tsne, digits_y, pd):
    # We mark each image inside your selection with True, then count the digits among them.
    digits_mask = digits_selection.value.get_mask(digits_tsne[:, 0], digits_tsne[:, 1])
    pd.Series(digits_y[digits_mask]).value_counts().sort_index().rename("images selected")
    return (digits_mask,)


@app.cell(hide_code=True)
def digits_selected_images(digits_X, digits_mask, mo, np, plt):
    _chosen = np.flatnonzero(digits_mask)[:40]
    if len(_chosen) == 0:
        _shown = mo.md("*No images are selected yet.*")
    else:
        _fig, _axes = plt.subplots(4, 10, figsize=(10, 4.4))
        for _ax in _axes.flat:
            _ax.axis("off")
        for _ax, _i in zip(_axes.flat, _chosen):
            _ax.imshow(digits_X[_i].reshape(8, 8), cmap="gray_r")
        _shown = _fig
    _shown
    return


@app.cell(hide_code=True)
def perplexity_intro(mo):
    mo.md(r"""
    ---
    ## Perplexity

    t-SNE's *perplexity* sets roughly how many neighbours of each point it keeps close, about five at
    a perplexity of 5 and about fifty at 50. To keep the map quick to redraw, we use a random sample
    of 400 images. Please move the slider through its five settings and watch the clumps, the gaps
    between them, and how many clumps each digit forms.
    """)
    return


@app.cell
def digits_sample(digits_X, digits_y, np):
    _sample = np.random.default_rng(0).choice(len(digits_X), size=400, replace=False)
    sample_X = digits_X[_sample]
    sample_y = digits_y[_sample]
    return sample_X, sample_y


@app.cell(hide_code=True)
def sample_perplexity_control(mo):
    sample_perplexity = mo.ui.slider(steps=[5, 10, 20, 30, 50], value=5, label="Perplexity")
    return (sample_perplexity,)


@app.cell
def sample_map(TSNE, sample_X, sample_perplexity):
    sample_tsne = TSNE(perplexity=sample_perplexity.value, init="random",
                       random_state=0).fit_transform(sample_X)
    return (sample_tsne,)


@app.cell(hide_code=True)
def sample_plot(draw_digits, mo, plt, sample_perplexity, sample_tsne, sample_y):
    _fig, _ax = plt.subplots(figsize=(5.2, 4.6))
    draw_digits(_ax, sample_tsne, sample_y, f"t-SNE, perplexity {sample_perplexity.value}")
    mo.vstack([sample_perplexity, _fig])
    return


@app.cell(hide_code=True)
def perplexity_note(mo):
    mo.md(r"""
    The images are the same at every setting, but the gaps between the clumps and the size of each
    clump change from one setting to the next. The size of a clump in a t-SNE map therefore cannot
    be read as the spread of a group, nor the distance between two clumps as the distance between two
    groups. At a perplexity of 5, several digits also break into two or more clumps, most of which
    form a single clump again at 30, although the 1s stay in pieces at every setting. A clump that
    appears at only one perplexity is weak evidence of a group.
    """)
    return


@app.cell(hide_code=True)
def cloud_intro(mo):
    mo.md(r"""
    ---
    ## Data with no groups

    Now consider 240 rows that contain no groups. Each row has a position along a single
    continuous scale, drawn from a normal distribution, and each of its eleven columns is that
    position plus some random noise. These data have no group to colour by, so we colour each point
    by the mean of its eleven values instead.
    """)
    return


@app.cell
def cloud(np):
    _rng = np.random.default_rng(18)
    _position = _rng.normal(size=240)
    cloud_X = _position[:, None] + _rng.normal(size=(240, 11))
    cloud_mean = cloud_X.mean(axis=1)
    return cloud_X, cloud_mean


@app.cell(hide_code=True)
def cloud_perplexity_control(mo):
    cloud_perplexity = mo.ui.slider(steps=[5, 10, 20, 30, 50], value=5, label="Perplexity")
    return (cloud_perplexity,)


@app.cell
def cloud_map(TSNE, cloud_X, cloud_perplexity):
    cloud_tsne = TSNE(perplexity=cloud_perplexity.value, init="random",
                      random_state=0).fit_transform(cloud_X)
    return (cloud_tsne,)


@app.cell(hide_code=True)
def cloud_plot(cloud_mean, cloud_perplexity, cloud_tsne, mo, plt):
    _fig, _ax = plt.subplots(figsize=(5.2, 4.2))
    _points = _ax.scatter(cloud_tsne[:, 0], cloud_tsne[:, 1], c=cloud_mean, cmap="viridis", s=8)
    _fig.colorbar(_points, ax=_ax, label="mean of the eleven values")
    _ax.set_title(f"t-SNE, perplexity {cloud_perplexity.value}")
    _ax.set_xticks([])
    _ax.set_yticks([])
    mo.vstack([cloud_perplexity, _fig])
    return


@app.cell(hide_code=True)
def cloud_note(mo):
    mo.md(r"""
    At a perplexity of 5, the map breaks into strands and small clumps with gaps between them,
    although the data contain no groups. The colour changes smoothly across those gaps, so the
    points on either side of a gap have similar values. From a perplexity of 20 upwards, the same
    rows form a single cloud.
    """)
    return


@app.cell(hide_code=True)
def checks(mo):
    mo.md(r"""
    ---
    ## Three checks

    Before you believe a group in a t-SNE map, please check the following:

    1. Does the group come back when you change the seed?
    2. Does it come back at other perplexities?
    3. When you colour the map by the columns, or by a summary of them such as a principal
       component score, does the colour change sharply at the group's edge, or smoothly across the
       gap? Selecting the group and comparing it with everyone does not settle this, because any
       region of a map will differ from the average.

    Most of the digits' clumps come back at every perplexity from 10 upwards, and the points in each
    are mostly one colour. The clumps in the cloud at a perplexity of 5 disappear at 20, and the
    colour changes smoothly across their gaps.
    """)
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## The music data

    The data are Monday's: 240 people's ratings of eleven genres, each from 1 to 10. We standardize
    the ratings as we did on Monday. Like the data in the last section, the music data come with no
    groups to colour by, so we colour each person by their score on one of Monday's principal
    components. A person's PC2 score, for instance, places them between a preference for
    contemporary genres and a preference for traditional ones.
    """)
    return


@app.cell
def load_tastes(course_csv):
    tastes = course_csv("music_tastes.csv")
    ratings = tastes.drop(columns="respondent")
    ratings.head()
    return (ratings,)


@app.cell
def scale_and_score(PCA, StandardScaler, pd, ratings):
    ratings_z = StandardScaler().fit_transform(ratings)
    pc_scores = pd.DataFrame(PCA(3).fit_transform(ratings_z), columns=["PC1", "PC2", "PC3"])
    return pc_scores, ratings_z


@app.cell(hide_code=True)
def seed_intro(mo):
    mo.md(r"""
    t-SNE starts by placing the points at random and then moves them, so the map depends partly on
    where the points started. The `random_state` argument, the seed, fixes those starting positions.
    A clump that appears with one seed but not with another comes from the starting positions, not
    from the data.
    """)
    return


@app.cell(hide_code=True)
def map_drawer(pc_scores, plt, ratings):
    def draw_map(coords, title, colour_by=None):
        """Scatter a two-column map, coloured by a PC score or a genre if colour_by is given."""
        fig, ax = plt.subplots(figsize=(5.2, 4.2))
        if colour_by is None:
            ax.scatter(coords[:, 0], coords[:, 1], s=8, color="tab:blue")
        else:
            values = pc_scores[colour_by] if colour_by in pc_scores else ratings[colour_by]
            points = ax.scatter(coords[:, 0], coords[:, 1], s=8, c=values, cmap="viridis")
            fig.colorbar(points, ax=ax, label=colour_by)
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_yticks([])
        return fig

    return (draw_map,)


@app.cell(hide_code=True)
def question(mo):
    mo.md(r"""
    ---
    ## Today's question

    **Do these people fall into distinct groups of musical taste? Each of you will map them at one
    perplexity before your team decides.**

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop. Please take the perplexities
    in order, one each: the first of you should take 5, the next 10, and so on, so that your team
    covers as many perplexities as it has members. Your team should decide together whether these
    people fall into distinct groups, but the answer you submit is your own.

    In Step 1 you will choose your perplexity, in Step 2 apply the first check by changing the seed,
    and in Step 3 apply the third by colouring your map and selecting a clump. Your team will apply
    the second check by comparing its members' maps, which use different perplexities. In Step 4 you
    will write your answer.
    """)
    return


@app.cell
def step1_choose(mo):
    # Step 1: choose your perplexity. Your team should take them in order, one each: 5, 10, 20,
    # 30, 50.
    answer_perplexity = mo.ui.dropdown(["5", "10", "20", "30", "50"], value="5",
                                       label="Perplexity")
    answer_perplexity
    return (answer_perplexity,)


@app.cell(hide_code=True)
def step2_control(mo):
    answer_seed = mo.ui.slider(0, 9, value=0, label="Seed")
    return (answer_seed,)


@app.cell
def step2_map(TSNE, answer_perplexity, answer_seed, ratings_z):
    # Step 2: we compute your map at your perplexity, with the seed set by the slider below. Does
    # it show separate clumps? Move the seed: do the same clumps come back?
    my_map = TSNE(perplexity=int(answer_perplexity.value), init="random",
                  random_state=answer_seed.value).fit_transform(ratings_z)
    return (my_map,)


@app.cell(hide_code=True)
def step2_plot(answer_perplexity, answer_seed, draw_map, mo, my_map):
    mo.vstack([answer_seed,
               draw_map(my_map, f"t-SNE, perplexity {answer_perplexity.value}, "
                                f"seed {answer_seed.value}")])
    return


@app.cell(hide_code=True)
def step3_control(mo, ratings):
    answer_colour = mo.ui.dropdown(["PC1", "PC2", "PC3"] + list(ratings.columns), value="PC1",
                                   label="Colour by")
    return (answer_colour,)


@app.cell
def step3_colour(answer_colour, answer_perplexity, answer_seed, draw_map, mo, my_map):
    # Step 3: colour your map by each component and by a few genres. Does the colour change
    # sharply at a gap, or smoothly across it? Then drag a box around a clump, or hold Shift and
    # drag to draw an outline, to see in the table below what the people you selected like.
    # Because any region of the map will differ from everyone, the table cannot show that a clump
    # is a group.
    music_selection = mo.ui.matplotlib(
        draw_map(my_map, f"t-SNE, perplexity {answer_perplexity.value}, "
                         f"seed {answer_seed.value}", answer_colour.value).axes[0])
    mo.vstack([answer_colour, music_selection])
    return (music_selection,)


@app.cell
def step3_compare(music_selection, my_map, pd, ratings):
    # The table shows each genre's mean rating among the people you selected, beside its mean
    # among everyone.
    _mask = music_selection.value.get_mask(my_map[:, 0], my_map[:, 1])
    pd.DataFrame({f"selected ({_mask.sum()} people)": ratings[_mask].mean(),
                  "everyone": ratings.mean()}).round(1)
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with what you saw in your own runs. Then save the notebook and upload your copy of
    `L18_tsne_umap.py` to *AE 16* on Canvas before the end of class.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_map(mo):
    mo.md(r"""
    **What your map showed at your perplexity, and whether any clumps in it came back when you changed the seed**
    """)
    return


@app.cell
def step4_answer_map(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_colour(mo):
    mo.md(r"""
    **How the colours changed across any gaps in your map, and what the people in a clump you selected had in common**
    """)
    return


@app.cell
def step4_answer_colour(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_verdict(mo):
    mo.md(r"""
    **With your teammates' maps alongside yours, whether any clumps came back at other perplexities, and whether these people fall into distinct groups of musical taste**
    """)
    return


@app.cell
def step4_answer_verdict(mo):
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
def made_intro(mo):
    mo.md(r"""
    ---
    ## After the question: generating the data

    The ratings were generated from three tastes that vary continuously from person to person: how
    much someone likes music at all, how far they prefer contemporary genres to traditional ones,
    and how much they like country, folk, rock and blues. Each person's position on each taste was
    drawn from a normal distribution, so the data contain no separate groups, only people spread
    continuously along three directions. The histograms of the scores on the first three
    components, below, each have a single peak.
    """)
    return


@app.cell(hide_code=True)
def score_histograms(pc_scores, plt):
    _fig, _axes = plt.subplots(1, 3, figsize=(10, 3))
    for _ax, _name in zip(_axes, pc_scores.columns):
        _ax.hist(pc_scores[_name], bins=20, color="tab:blue")
        _ax.set_title(_name)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def made_note(mo):
    mo.md(r"""
    Any gaps in a t-SNE map of these people therefore came from the method and its setting, not from
    the people. On Monday, in the session on clustering, we will ask the same question with methods
    that assign each person to a group.

    ### The main idea, again

    t-SNE shows which rows are similar to which when there are too many columns to plot, and it can
    show groups that PCA cannot, as it did with the digits. Before you believe a group it shows,
    check that the group comes back with other seeds and at other perplexities, and that the colour
    changes sharply at its edge.
    """)
    return


@app.cell(hide_code=True)
def umap_intro(mo):
    mo.md(r"""
    ---
    ## Optional: UMAP

    This section is not part of today's exercise. UMAP is a second method for making the same kind
    of map, described in a tip near the end of the reading. Its setting `n_neighbors` corresponds
    roughly to perplexity in t-SNE.

    UMAP is not part of scikit-learn. It comes from a separate package, `umap-learn`, which depends
    on `numba` and `llvmlite`, two large packages that compile Python code into machine code and
    have to match your operating system and your version of Python. Adding them to the course
    environment now would require each of you to update your environment before class, with the risk
    that an installation fails on a laptop where we cannot repair it in the room. Instead, we ran
    UMAP once on the same standardized ratings, at the same five settings, and saved the
    coordinates in `data/music_umap.csv`. The maps below show UMAP beside t-SNE at the setting you
    choose, coloured by PC1, but you cannot run UMAP on other data in this notebook.
    """)
    return


@app.cell
def load_umap(course_csv):
    umap_coords = course_csv("music_umap.csv")
    umap_coords.head()
    return (umap_coords,)


@app.cell(hide_code=True)
def umap_control(mo):
    umap_setting = mo.ui.slider(steps=[5, 10, 20, 30, 50], value=30,
                                label="Perplexity (t-SNE) and n_neighbors (UMAP)")
    return (umap_setting,)


@app.cell
def umap_compare(TSNE, ratings_z, umap_coords, umap_setting):
    # We take the UMAP rows for one setting, in respondent order so that they line up with
    # ratings_z.
    _rows = umap_coords[umap_coords["n_neighbors"] == umap_setting.value].sort_values("respondent")
    umap_xy = _rows[["umap_1", "umap_2"]].to_numpy()
    tsne_xy = TSNE(perplexity=umap_setting.value, init="random",
                   random_state=0).fit_transform(ratings_z)
    return tsne_xy, umap_xy


@app.cell(hide_code=True)
def umap_plot(draw_map, mo, tsne_xy, umap_setting, umap_xy):
    _n = umap_setting.value
    mo.vstack([umap_setting,
               mo.hstack([draw_map(tsne_xy, f"t-SNE, perplexity {_n}", "PC1"),
                          draw_map(umap_xy, f"UMAP, n_neighbors {_n}", "PC1")])])
    return


if __name__ == "__main__":
    app.run()
