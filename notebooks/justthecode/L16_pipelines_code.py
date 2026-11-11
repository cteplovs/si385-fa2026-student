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

    ## Session 16, the code on its own: pipelines, train-test splits and cross-validation

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L16_pipelines.py`. The session notebook uses a
    slider, plots and helper functions written for it, which you will not have when you work on
    your own data. Each section below does one of the session's computations with only pandas and
    scikit-learn, starting from a data frame, so that you can copy it into your project or another
    notebook. The data are the California housing districts from session 16.

    Each code cell starts with a comment listing the imports it uses, and its variable names start
    with `_`, which keeps them local to the cell, so you can paste a cell anywhere in a marimo
    notebook without a clash with names in other cells.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    from sklearn.model_selection import KFold, cross_validate, train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

    return (
        ColumnTransformer,
        KFold,
        LinearRegression,
        OneHotEncoder,
        SimpleImputer,
        StandardScaler,
        cross_validate,
        make_pipeline,
        mo,
        pd,
        r2_score,
        train_test_split,
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
def load_housing(course_csv):
    housing = course_csv("housing.csv")
    housing.head()
    return (housing,)


@app.cell(hide_code=True)
def pipeline_intro(mo):
    mo.md(r"""
    ---
    ## A pipeline

    In the cell below, we build a pipeline that fills in missing numeric values with the median,
    standardizes the numeric columns, one-hot encodes a categorical column, and fits a linear
    regression, then fit it to every row. To use it on other data, you would change the two lists
    of columns and the column to predict.
    """)
    return


@app.cell
def pipeline_code(
    ColumnTransformer,
    LinearRegression,
    OneHotEncoder,
    SimpleImputer,
    StandardScaler,
    housing,
    make_pipeline,
):
    # Uses: from sklearn.compose import ColumnTransformer
    #       from sklearn.impute import SimpleImputer
    #       from sklearn.linear_model import LinearRegression
    #       from sklearn.pipeline import make_pipeline
    #       from sklearn.preprocessing import OneHotEncoder, StandardScaler
    _numeric = ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms",
                "population", "households", "median_income"]
    _categorical = ["ocean_proximity"]
    _model = make_pipeline(
        ColumnTransformer([
            ("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
             _numeric),
            ("categorical", OneHotEncoder(drop="first", handle_unknown="ignore"), _categorical),
        ]),
        LinearRegression(),
    )
    _model.fit(housing, housing["median_house_value"])
    _model
    return


@app.cell(hide_code=True)
def split_intro(mo):
    mo.md(r"""
    ---
    ## A train-test split

    In the cell below, we set 20% of the rows aside as a test set, fit the pipeline to the other
    80%, and score its predictions on the test set with R². `random_state` fixes the random choice
    of rows, so the split is the same every time the cell runs.
    """)
    return


@app.cell
def split_code(
    ColumnTransformer,
    LinearRegression,
    OneHotEncoder,
    SimpleImputer,
    StandardScaler,
    housing,
    make_pipeline,
    r2_score,
    train_test_split,
):
    # Uses: the imports in the pipeline cell, and
    #       from sklearn.metrics import r2_score
    #       from sklearn.model_selection import train_test_split
    _numeric = ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms",
                "population", "households", "median_income"]
    _model = make_pipeline(
        ColumnTransformer([
            ("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
             _numeric),
            ("categorical", OneHotEncoder(drop="first", handle_unknown="ignore"), ["ocean_proximity"]),
        ]),
        LinearRegression(),
    )
    _train, _test = train_test_split(housing, test_size=0.2, random_state=385)
    _model.fit(_train, _train["median_house_value"])
    print("rows:", len(_train), "training,", len(_test), "test")
    print("R² on the test set:", round(r2_score(_test["median_house_value"], _model.predict(_test)), 3))
    return


@app.cell(hide_code=True)
def cv_intro(mo):
    mo.md(r"""
    ---
    ## Cross-validation

    In the cell below, we score the same pipeline by 5-fold cross-validation and print the R² and
    the root mean squared error for each fold, with their means. Passing the whole pipeline to
    `cross_validate` refits the imputer and the scaler on the training folds each time, so the
    fold left out is kept out of the preprocessing too.
    """)
    return


@app.cell
def cv_code(
    ColumnTransformer,
    KFold,
    LinearRegression,
    OneHotEncoder,
    SimpleImputer,
    StandardScaler,
    cross_validate,
    housing,
    make_pipeline,
):
    # Uses: the imports in the pipeline cell, and
    #       from sklearn.model_selection import KFold, cross_validate
    _numeric = ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms",
                "population", "households", "median_income"]
    _model = make_pipeline(
        ColumnTransformer([
            ("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
             _numeric),
            ("categorical", OneHotEncoder(drop="first", handle_unknown="ignore"), ["ocean_proximity"]),
        ]),
        LinearRegression(),
    )
    _result = cross_validate(_model, housing, housing["median_house_value"],
                             cv=KFold(n_splits=5, shuffle=True, random_state=385),
                             scoring=("r2", "neg_root_mean_squared_error"))
    print("R² by fold:  ", _result["test_r2"].round(3), "mean", _result["test_r2"].mean().round(3))
    print("RMSE by fold:", (-_result["test_neg_root_mean_squared_error"]).round(0),
          "mean", round(-_result["test_neg_root_mean_squared_error"].mean()))
    return


@app.cell(hide_code=True)
def coefficients_intro(mo):
    mo.md(r"""
    ---
    ## Coefficients from a pipeline

    In the cell below, we fit the pipeline and label each coefficient with the column it belongs
    to. `get_feature_names_out` gives the names after preprocessing, including one name for each
    category of the encoded column except the first, which `drop="first"` leaves out so that the
    other categories' coefficients are measured from it. Because the numeric columns are standardized, each of their
    coefficients is the change in the prediction for one standard deviation of that column.
    """)
    return


@app.cell
def coefficients_code(
    ColumnTransformer,
    LinearRegression,
    OneHotEncoder,
    SimpleImputer,
    StandardScaler,
    housing,
    make_pipeline,
    pd,
):
    # Uses: the imports in the pipeline cell, and
    #       import pandas as pd
    _numeric = ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms",
                "population", "households", "median_income"]
    _model = make_pipeline(
        ColumnTransformer([
            ("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
             _numeric),
            ("categorical", OneHotEncoder(drop="first", handle_unknown="ignore"), ["ocean_proximity"]),
        ]),
        LinearRegression(),
    ).fit(housing, housing["median_house_value"])
    _names = _model[0].get_feature_names_out()
    pd.Series(_model[-1].coef_, index=_names, name="coefficient").round(0)
    return


if __name__ == "__main__":
    app.run()
