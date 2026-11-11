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

    ## Session 17, the code on its own: principal component analysis

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L17_pca.py`. The session notebook uses dropdowns,
    plots and helper functions written for it, which you will not have when you work on your own
    data. Each section below does one of the session's computations with only pandas and
    scikit-learn, starting from a data frame, so that you can copy it into your project or another
    notebook. The data are the ratings of eleven genres of music from session 17, which were
    generated for the course, so no row describes a real person.

    Each code cell starts with a comment listing the imports it uses, and its variable names start
    with `_`, which keeps them local to the cell, so you can paste a cell anywhere in a marimo
    notebook without a clash with names in other cells.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import pandas as pd
    from sklearn.decomposition import PCA
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    return PCA, StandardScaler, make_pipeline, mo, pd


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
def variance_intro(mo):
    mo.md(r"""
    ---
    ## Fitting PCA and the variance explained

    In the cell below, we standardize the columns and fit PCA in one pipeline, then compute the
    share of the variance that each component explains, the running total, and the number of
    components needed for 95% of the variance. To use it on other data, you would put your own
    numeric columns in place of `ratings`.
    """)
    return


@app.cell
def variance_code(PCA, StandardScaler, make_pipeline, pd, ratings):
    # Uses: import pandas as pd
    #       from sklearn.decomposition import PCA
    #       from sklearn.pipeline import make_pipeline
    #       from sklearn.preprocessing import StandardScaler
    _model = make_pipeline(StandardScaler(), PCA()).fit(ratings)
    _ratio = _model.named_steps["pca"].explained_variance_ratio_
    _table = pd.DataFrame({"explained": _ratio, "cumulative": _ratio.cumsum()},
                          index=[f"PC{_i}" for _i in range(1, len(_ratio) + 1)])
    print("components for 95% of the variance:", int((_table["cumulative"] >= 0.95).argmax()) + 1)
    _table.round(3)
    return


@app.cell(hide_code=True)
def weights_intro(mo):
    mo.md(r"""
    ---
    ## The weights of each component

    In the cell below, we put the fitted model's `components_` into a table with one row for each
    original column and one column for each component, keeping the first three, and sort it by the
    weights on the first component.
    """)
    return


@app.cell
def weights_code(PCA, StandardScaler, make_pipeline, pd, ratings):
    # Uses: import pandas as pd
    #       from sklearn.decomposition import PCA
    #       from sklearn.pipeline import make_pipeline
    #       from sklearn.preprocessing import StandardScaler
    _model = make_pipeline(StandardScaler(), PCA(n_components=3)).fit(ratings)
    _weights = pd.DataFrame(_model.named_steps["pca"].components_.T, index=ratings.columns,
                            columns=["PC1", "PC2", "PC3"])
    _weights.sort_values("PC1").round(2)
    return


@app.cell(hide_code=True)
def scores_intro(mo):
    mo.md(r"""
    ---
    ## Scores, and the rows at each end of a component

    In the cell below, we compute each row's score on the first three components with `transform`,
    then list the five rows that score highest on one component and the five that score lowest,
    with their original values, which is how you would check a description of that component. To
    look at another component, you would change `_component`.
    """)
    return


@app.cell
def scores_code(PCA, StandardScaler, make_pipeline, pd, ratings):
    # Uses: import pandas as pd
    #       from sklearn.decomposition import PCA
    #       from sklearn.pipeline import make_pipeline
    #       from sklearn.preprocessing import StandardScaler
    _model = make_pipeline(StandardScaler(), PCA(n_components=3)).fit(ratings)
    _scores = pd.DataFrame(_model.transform(ratings), index=ratings.index,
                           columns=["PC1", "PC2", "PC3"])
    _component = "PC1"
    _order = _scores[_component].sort_values(ascending=False).index
    _ends = list(_order[:5]) + list(_order[-5:])
    ratings.loc[_ends].assign(score=_scores.loc[_ends, _component].round(2))
    return


if __name__ == "__main__":
    app.run()
