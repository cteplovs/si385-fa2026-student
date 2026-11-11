# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
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

    ## Session 18, the code on its own: t-SNE maps and how to check them

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L18_tsne_umap.py`. The session notebook uses sliders, dropdowns, selections and helper functions written for it,
    which you will not have when you work on your own data. Each section below does one
    of the session's computations with only pandas, matplotlib and scikit-learn, starting from a data frame, so that
    you can copy it into your project or another notebook. The data are the handwritten digits that come with scikit-learn and the ratings of
    eleven genres of music from sessions 17 and 18, which were generated for the course, so no row
    describes a real person.

    Each code cell starts with a comment listing the imports it uses, and its variable names start
    with `_`, which keeps them local to the cell, so you can paste a cell anywhere in a marimo
    notebook without a clash with names in other cells.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    from sklearn.datasets import load_digits
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    from sklearn.preprocessing import StandardScaler

    return PCA, StandardScaler, TSNE, load_digits, mo, pd, plt


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
def load_ratings(course_csv):
    ratings = course_csv("music_tastes.csv").set_index("respondent")
    ratings.head()
    return (ratings,)


@app.cell(hide_code=True)
def maps_intro(mo):
    mo.md(r"""
    ---
    ## PCA and t-SNE maps side by side

    In the cell below, we reduce the digits' 64 columns to two with PCA and with t-SNE and plot both,
    coloured by the digit each image shows. The colouring is possible only because the labels are
    known, which is what makes these data useful for seeing what each method does.
    """)
    return


@app.cell
def maps_code(PCA, TSNE, load_digits, plt):
    # Uses: import matplotlib.pyplot as plt
    #       from sklearn.datasets import load_digits
    #       from sklearn.decomposition import PCA
    #       from sklearn.manifold import TSNE
    _X, _y = load_digits(return_X_y=True)
    _maps = {"PCA": PCA(2).fit_transform(_X),
             "t-SNE, perplexity 30": TSNE(perplexity=30, init="random",
                                          random_state=0).fit_transform(_X)}
    _fig, _axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for _ax, (_title, _xy) in zip(_axes, _maps.items()):
        _points = _ax.scatter(_xy[:, 0], _xy[:, 1], c=_y, cmap="tab10", s=5)
        _ax.set_title(_title, fontsize=10)
    _fig.colorbar(_points, ax=_axes, label="digit")
    _fig
    return


@app.cell(hide_code=True)
def settings_intro(mo):
    mo.md(r"""
    ---
    ## The same data at several settings and seeds

    A clump that appears at one perplexity and one seed but not at others is a product of the
    setting. In the cell below, we standardize the music ratings and draw a grid of t-SNE maps, one
    row for each perplexity and one column for each seed. It takes a few seconds.
    """)
    return


@app.cell
def settings_code(StandardScaler, TSNE, plt, ratings):
    # Uses: import matplotlib.pyplot as plt
    #       from sklearn.manifold import TSNE
    #       from sklearn.preprocessing import StandardScaler
    _X = StandardScaler().fit_transform(ratings)
    _perplexities, _seeds = [5, 30], [0, 1, 2]
    _fig, _axes = plt.subplots(len(_perplexities), len(_seeds), figsize=(10, 6.5))
    for _row, _perplexity in enumerate(_perplexities):
        for _col, _seed in enumerate(_seeds):
            _xy = TSNE(perplexity=_perplexity, init="random",
                       random_state=_seed).fit_transform(_X)
            _axes[_row, _col].scatter(_xy[:, 0], _xy[:, 1], s=6)
            _axes[_row, _col].set_title(f"perplexity {_perplexity}, seed {_seed}", fontsize=9)
            _axes[_row, _col].set_xticks([])
            _axes[_row, _col].set_yticks([])
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def colour_intro(mo):
    mo.md(r"""
    ---
    ## Colouring a map by a column, and comparing a region with everyone

    In the cell below, we colour one t-SNE map by the first principal component. If a gap in the map
    separates real groups, the colour changes sharply across it, and if the colour changes smoothly,
    the gap is weaker evidence. Then we take the points on one side of the map, here those with a
    first coordinate above zero, and compare their mean ratings with everyone's. Any region of a map
    will differ from everyone in some columns, so this comparison describes a region but cannot show
    that it is a group.
    """)
    return


@app.cell
def colour_code(PCA, StandardScaler, TSNE, pd, plt, ratings):
    # Uses: import matplotlib.pyplot as plt
    #       import pandas as pd
    #       from sklearn.decomposition import PCA
    #       from sklearn.manifold import TSNE
    #       from sklearn.preprocessing import StandardScaler
    _X = StandardScaler().fit_transform(ratings)
    _xy = TSNE(perplexity=30, init="random", random_state=0).fit_transform(_X)
    _pc1 = PCA(1).fit_transform(_X)[:, 0]
    _fig, _ax = plt.subplots(figsize=(5.5, 4.5))
    _points = _ax.scatter(_xy[:, 0], _xy[:, 1], c=_pc1, cmap="viridis", s=10)
    _fig.colorbar(_points, label="PC1 score")
    _region = _xy[:, 0] > 0
    _comparison = pd.DataFrame({f"region ({_region.sum()} rows)": ratings[_region].mean(),
                                "everyone": ratings.mean()}).round(1)
    print(_comparison)
    _fig
    return


if __name__ == "__main__":
    app.run()
