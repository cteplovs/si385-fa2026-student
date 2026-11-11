# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
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

    ## Session 19, the code on its own: k-means, distance, and scaling

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L19_kmeans.py`. The session notebook uses sliders,
    dropdowns and helper functions written for it, which you will not have when you work on your
    own data. Each section below does one of the session's computations with only pandas and
    scikit-learn, starting from a data frame, so that you can copy it into your project or another
    notebook. The data are the Palmer penguins from session 19.

    Each code cell starts with a comment listing the imports it uses, and its variable names start
    with `_`, which keeps them local to the cell, so you can paste a cell anywhere in a marimo
    notebook without a clash with names in other cells.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import pandas as pd
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    return KMeans, StandardScaler, mo, pd


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
def load_penguins(course_csv):
    MEASUREMENTS = ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    penguins = course_csv("penguins.csv").dropna(subset=MEASUREMENTS).reset_index(drop=True)
    penguins.head()
    return MEASUREMENTS, penguins


@app.cell(hide_code=True)
def fit_intro(mo):
    mo.md(r"""
    ---
    ## Fitting k-means

    In the cell below, we standardize the four measurements, fit k-means with K = 3 from ten
    starts, and print each row's cluster, each cluster's centroid and the inertia, which is scikit-learn's name for the total within-cluster
    variation. To use it on other data, you would put your own numeric columns in place of
    `penguins[MEASUREMENTS]`.
    """)
    return


@app.cell
def fit_code(KMeans, MEASUREMENTS, StandardScaler, penguins):
    # Uses: from sklearn.cluster import KMeans
    #       from sklearn.preprocessing import StandardScaler
    _X = StandardScaler().fit_transform(penguins[MEASUREMENTS])
    _model = KMeans(n_clusters=3, n_init=10, random_state=0).fit(_X)

    print("cluster of the first ten rows:", _model.labels_[:10])
    print("inertia:", round(_model.inertia_, 1))
    print("centroids, in standard deviations from each column's mean:")
    print(_model.cluster_centers_.round(2))
    return


@app.cell(hide_code=True)
def starts_intro(mo):
    mo.md(r"""
    ---
    ## Results from different starts

    k-means can stop at a different clustering from each random start. In the cell below, we fit
    it from one start at a time with twenty different seeds and count how often each inertia
    occurs, and then fit it once with `n_init=10`, which runs ten starts and keeps the one with
    the lowest inertia.
    """)
    return


@app.cell
def starts_code(KMeans, MEASUREMENTS, StandardScaler, pd, penguins):
    # Uses: from sklearn.cluster import KMeans
    #       from sklearn.preprocessing import StandardScaler
    _X = StandardScaler().fit_transform(penguins[MEASUREMENTS])
    _inertias = [round(KMeans(n_clusters=3, n_init=1, random_state=_seed).fit(_X).inertia_, 1)
                 for _seed in range(20)]
    print(pd.Series(_inertias).value_counts().rename_axis("inertia").rename("starts"))
    print()
    print("best of ten starts:",
          round(KMeans(n_clusters=3, n_init=10, random_state=0).fit(_X).inertia_, 1))
    return


@app.cell(hide_code=True)
def distance_intro(mo):
    mo.md(r"""
    ---
    ## Distance and units

    k-means measures closeness as the straight-line distance across all the columns, so a column
    whose values vary more contributes more to that distance. In the cell below, we take two rows,
    an Adelie penguin and a Gentoo penguin, and compute each column's share of the squared distance
    between them, first in the original units and then after standardizing. To compare two other rows, you would change the two row
    numbers.
    """)
    return


@app.cell
def distance_code(MEASUREMENTS, StandardScaler, pd, penguins):
    # Uses: from sklearn.preprocessing import StandardScaler
    _first, _second = 0, 200
    _original = penguins[MEASUREMENTS]
    _standardized = pd.DataFrame(StandardScaler().fit_transform(_original), columns=MEASUREMENTS)

    _shares = {}
    for _name, _data in [("original units", _original), ("standardized", _standardized)]:
        _squared = (_data.iloc[_first] - _data.iloc[_second]) ** 2
        _shares[_name] = (_squared / _squared.sum()).round(2)
    pd.DataFrame(_shares)
    return


@app.cell(hide_code=True)
def describe_intro(mo):
    mo.md(r"""
    ---
    ## Describing the clusters

    A clustering is useful only if you can say what each cluster contains. In the cell below, we
    add each penguin's cluster to the data frame, then compute each cluster's size and its mean
    in each measurement, in the original units so that the numbers can be read as grams and
    millimetres. The last table counts the species in each cluster, which is possible here only
    because the species were recorded; with most data there is no such column.
    """)
    return


@app.cell
def describe_code(KMeans, MEASUREMENTS, StandardScaler, pd, penguins):
    # Uses: from sklearn.cluster import KMeans
    #       from sklearn.preprocessing import StandardScaler
    _X = StandardScaler().fit_transform(penguins[MEASUREMENTS])
    _clustered = penguins.assign(
        cluster=KMeans(n_clusters=3, n_init=10, random_state=0).fit_predict(_X))

    print(_clustered.groupby("cluster")[MEASUREMENTS].mean().round(1)
          .assign(penguins=_clustered["cluster"].value_counts().sort_index()))
    print()
    print(pd.crosstab(_clustered["cluster"], _clustered["species"]))
    return


if __name__ == "__main__":
    app.run()
