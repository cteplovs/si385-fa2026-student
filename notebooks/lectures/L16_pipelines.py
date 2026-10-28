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

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 16: Pipelines, and what a model can explain

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, October 28, 2026

    **Reading due today:** Géron, *Hands-On Machine Learning*, ch. 2, *End-to-End Machine Learning
    Project*; or the scikit-learn User Guide pages *Common pitfalls and recommended practices* and
    *Pipelines and composite estimators*

    ---

    ### Today you will be able to

    - Explain how scikit-learn's estimators, transformers and pipelines fit together, and what
      fitting one of them to data does
    - Build a pipeline that imputes, scales and encodes the columns and then fits a linear
      regression, so that cross-validation fits every step on the training folds only
    - Use a train-test split and cross-validation to say how far to trust a score
    - Read the coefficients of a linear regression, and use them with the cross-validated score to
      explain what sets a district's house value

    ### Timing

    | Part | Minutes |
    |---|---:|
    | The data | 5 |
    | scikit-learn: estimators, transformers and fitting | 10 |
    | Each transformer, and the pipeline | 10 |
    | Train-test splits and cross-validation | 10 |
    | Coefficients | 10 |
    | Today's question, in teams | 15 |
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    import matplotlib.pyplot as plt
    import pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    from sklearn.model_selection import KFold, cross_validate, train_test_split
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler

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

    return (
        ColumnTransformer,
        KFold,
        LinearRegression,
        OneHotEncoder,
        SimpleImputer,
        StandardScaler,
        course_csv,
        cross_validate,
        make_pipeline,
        mo,
        pd,
        plt,
        r2_score,
        train_test_split,
    )


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## The data

    These are the data from Géron's chapter 2: the 1990 United States census for California,
    summarised for each of 20,640 districts (census block groups, each typically of 600 to 3,000
    people). Each row describes a district rather than a house, so a model fitted to them explains
    differences between districts.

    | Column | Description |
    |---|---|
    | `longitude`, `latitude` | Where the district is |
    | `housing_median_age` | Median age of the houses, in years |
    | `total_rooms`, `total_bedrooms` | Rooms and bedrooms in the whole district |
    | `population`, `households` | People and households in the district |
    | `median_income` | Median household income, in tens of thousands of dollars |
    | `ocean_proximity` | How near the district is to the ocean, in five categories |
    | `median_house_value` | Median house value, in dollars: the value to explain |
    """)
    return


@app.cell
def load_housing(course_csv):
    housing = course_csv("housing.csv")
    # The .T transposes the table, so that the variables are the rows of the output.
    # Try it without the .T to see the difference.
    housing.describe().T.round(1)
    return (housing,)


@app.cell(hide_code=True)
def ratios_intro(mo):
    mo.md(r"""
    `total_bedrooms` has 207 missing values; every other column is complete. Géron also builds three
    ratios from the totals, since a district's total rooms says more about its size than about its
    houses. The cell below adds them. Each ratio is computed from the values in its own row only, so
    it can be added before the data are split.
    """)
    return


@app.cell
def add_ratios(housing):
    districts = housing.assign(
        rooms_per_household=housing["total_rooms"] / housing["households"],
        bedrooms_per_room=housing["total_bedrooms"] / housing["total_rooms"],
        people_per_household=housing["population"] / housing["households"],
    )
    house_value = districts["median_house_value"]
    NUMERIC = ["longitude", "latitude", "housing_median_age", "total_rooms", "total_bedrooms",
               "population", "households", "median_income"]
    RATIOS = ["rooms_per_household", "bedrooms_per_room", "people_per_household"]
    return NUMERIC, RATIOS, districts, house_value


@app.cell(hide_code=True)
def income_value_intro(mo):
    mo.md(r"""
    ---
    ## Income and value

    Consider one column against the value first. Each point below is a district.
    """)
    return


@app.cell
def income_value_plot(districts, plt):
    _fig, _ax = plt.subplots(figsize=(7, 4.5))
    _ax.scatter(districts["median_income"], districts["median_house_value"] / 1000,
                s=3, alpha=0.15)
    _ax.set_xlabel("Median income (tens of thousands of dollars)")
    _ax.set_ylabel("Median house value (thousands of dollars)")
    _ax.set_title("Median income against median house value, 20,640 districts")
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def sklearn_ecosystem(mo):
    mo.md(r"""
    ---
    ## The scikit-learn ecosystem

    The rest of this notebook builds a model from parts of scikit-learn, the library most Python data
    scientists use for machine learning. Its parts fit together like building blocks: an imputer, a
    scaler, an encoder and a regression are separate objects, and a pipeline joins them into one
    object that can be used wherever any one of them could.

    They fit together because every part follows the same small set of conventions, which is what
    people mean by *the scikit-learn API*. Every object is created with its settings, as in
    `SimpleImputer(strategy="median")`; it is fitted to data with `fit`; and it then either changes
    data with `transform` or makes predictions with `predict`. A pipeline follows the same
    conventions, so it can go anywhere a single model can, including into cross-validation.

    scikit-learn began in 2007 as a Google Summer of Code project by David Cournapeau, and a team at
    INRIA, the French national institute for research in computer science, made its first public
    release in 2010. Buitinck and colleagues set out its conventions in 2013, in *API design for
    machine learning software: experiences from the scikit-learn project*.

    scikit-learn was built on NumPy, and its objects work in NumPy arrays. A transformer given a
    pandas DataFrame returns a NumPy array, without the DataFrame's column names or index, which is
    why the output of a transformer is often an unlabelled grid of numbers. Since version 1.2,
    `set_output(transform="pandas")` asks a transformer to return a DataFrame instead, as the cell
    below shows. This notebook uses it wherever you need to read what comes out, but you are likely to
    encounter older code that does not use this feature, so you'll often see a lot of acrobatics to
    convert to and from NumPy arrays.
    """)
    return


@app.cell
def numpy_or_pandas_output(StandardScaler, housing, mo):
    _two_columns = housing[["median_income", "housing_median_age"]]
    _as_array = StandardScaler().fit_transform(_two_columns)
    _as_frame = StandardScaler().set_output(transform="pandas").fit_transform(_two_columns)

    # mo.hstack is a marimo function that puts outputs side by side.
    mo.hstack([
        # mo.md is a marimo function that displays Markdown text.
        # mo.vstack is a marimo function that stacks outputs one above the other.
        mo.vstack([mo.md("The default output, a NumPy array"), _as_array[:3].round(2)]),
        mo.vstack([mo.md('With `set_output(transform="pandas")`'), _as_frame.head(3).round(2)]),
    ], justify="start", gap=3)
    return


@app.cell(hide_code=True)
def estimators_and_fitting(mo):
    mo.md(r"""
    ---
    ## Estimators and transformers

    scikit-learn calls every object with a `fit` method an *estimator*. There are two kinds of
    estimators:

    - A *transformer* changes data, such as `SimpleImputer`, `StandardScaler` and `OneHotEncoder`.
    - A *predictor* makes predictions, such as `LinearRegression`.

    A `ColumnTransformer` and a `Pipeline` are estimators built from other estimators. A
    `ColumnTransformer` sends different columns to different transformers and puts their outputs side
    by side. A `Pipeline` runs its steps in order and can do whatever its last step can, so a
    pipeline that ends in a `LinearRegression` can `predict`.

    ## Fitting

    Creating an estimator, as in `SimpleImputer(strategy="median")`, only records its settings. The
    estimator has not yet been fitted to any data, and it cannot transform or predict anything.
    *Fitting* it runs its calculation on a set of data and stores the results inside the object: a
    `SimpleImputer` computes the median of each column, a `StandardScaler` computes each column's
    mean and standard deviation, and a `LinearRegression` estimates its coefficients. That makes
    estimators *stateful*: later calls use the stored results instead of looking at the fitting data
    again.

    | Method | Effect | Use |
    |---|---|---|
    | `fit(X, y)` | Computes from `X` (and `y`, for a predictor) and stores the results | On the training data |
    | `transform(X)` | Changes `X` using the stored results | On any data, after `fit` |
    | `fit_transform(X)` | `fit`, then `transform`, on the same data | On the training data |
    | `predict(X)` | Predicts for `X` using the stored results | On test data or new data, after `fit` |
    | `fit_predict(X)` | `fit`, then `predict`, on the same data | When the result for the fitting data is the point, as in clustering (sessions 19 and 20) |

    A pipeline uses both. Call its `fit` on the training data: each transformer runs `fit_transform`
    in turn and the last step runs `fit`. Then call its `predict` on the test data or on new data:
    each transformer runs `transform` with what it stored, and the last step runs `predict`. A
    `SimpleImputer` in a pipeline therefore fills gaps in the test data with the *training* medians,
    which keeps the test data out of everything computed during fitting.

    ## Fitted attributes, and the trailing underscore

    scikit-learn marks the attributes that `fit` sets with a trailing underscore. The settings you
    chose have plain names, such as `strategy`, and the fitted attributes end in `_`, such as
    `statistics_`, `mean_` and `coef_`. They do not exist until the estimator has been fitted, as the
    cell below shows.
    """)
    return


@app.cell
def fitting_demo(SimpleImputer, housing):
    demo_imputer = SimpleImputer(strategy="median")
    # demo_imputer is instantiated (created, with its settings) but not yet fitted to data.
    print("Before fit, has statistics_:", hasattr(demo_imputer, "statistics_"))

    demo_imputer.fit(housing[["total_bedrooms", "total_rooms"]])
    print("After fit, has statistics_: ", hasattr(demo_imputer, "statistics_"))
    print("strategy    =", demo_imputer.strategy)
    print("statistics_ =", demo_imputer.statistics_)
    return


@app.cell(hide_code=True)
def practice_median_intro(mo):
    mo.md(r"""
    ### Practice: check the imputer by hand

    Please type this one yourself rather than copying it. Replace `None` in the cell below with the
    median of `total_bedrooms` computed with pandas, `housing["total_bedrooms"].median()`, and check
    that it matches the first value of `statistics_` above.
    """)
    return


@app.cell
def practice_median():
    my_median = None
    my_median
    return


@app.cell(hide_code=True)
def transformers_intro(mo):
    mo.md(r"""
    ---
    ## Each transformer, before and after

    The tables below follow five districts through each transformer: the rows that go in on the left,
    the rows that come out on the right, and the fitted attributes the transformer stored. Each
    transformer is fitted on all 20,640 districts and then transforms the five, the same order of
    events as fitting on training data and transforming test data. Two of the five districts are
    missing `total_bedrooms`.
    """)
    return


@app.cell(hide_code=True)
def teaching_display_helpers(housing, mo, pd):
    # These two functions only lay out the tables for teaching; you would not write them in your own
    # analysis.
    sample = pd.concat([housing[housing["total_bedrooms"].isna()].head(2),
                        housing.drop_duplicates("ocean_proximity").head(3)])


    def show(frame):
        """A small table as HTML, so that two of them can sit side by side."""
        # mo.Html is a marimo function that displays a string of HTML.
        return mo.Html(frame.to_html(na_rep="NaN", float_format="{:,.2f}".format))


    def before_after(fitted, columns, attributes):
        """The sample rows going into a fitted transformer, the rows coming out, and its attributes."""
        after = fitted.transform(sample[columns])
        after = after.apply(lambda c: c.astype(int) if set(c.unique()) <= {0, 1} else c)
        stored = "  \n".join(f"`{a}` = `{getattr(fitted, a)!r}`" for a in attributes)
        # mo.vstack is a marimo function that stacks outputs one above the other.
        return mo.vstack([
            # mo.md is a marimo function that displays Markdown text.
            # mo.hstack is a marimo function that puts outputs side by side.
            mo.hstack([show(sample[columns]), mo.md("→ `transform` →"), show(after)],
                      justify="start", align="center", gap=1.5),
            mo.md("Stored during `fit`:  \n" + stored),
        ])

    return (before_after,)


@app.cell(hide_code=True)
def imputer_intro(mo):
    mo.md(r"""
    ### SimpleImputer

    When it is fitted, a `SimpleImputer` computes the median of each column it is given and stores
    it. When it transforms, it fills each missing value with the stored median.
    """)
    return


@app.cell
def imputer_before_after(SimpleImputer, before_after, housing):
    _imputer = SimpleImputer(strategy="median").set_output(transform="pandas")
    _imputer.fit(housing[["total_bedrooms", "households"]])
    before_after(_imputer, ["total_bedrooms", "households"], ["statistics_"])
    return


@app.cell(hide_code=True)
def scaler_intro(mo):
    mo.md(r"""
    ### StandardScaler

    When it is fitted, a `StandardScaler` computes the mean and the standard deviation of each column
    and stores them. When it transforms, it subtracts the mean and divides by the standard deviation,
    so that every value says how many standard deviations the district is above or below the average
    district.
    """)
    return


@app.cell
def scaler_before_after(StandardScaler, before_after, housing):
    _scaler = StandardScaler().set_output(transform="pandas")
    _scaler.fit(housing[["median_income", "housing_median_age"]])
    before_after(_scaler, ["median_income", "housing_median_age"], ["mean_", "scale_"])
    return


@app.cell(hide_code=True)
def encoder_intro(mo):
    mo.md(r"""
    ### OneHotEncoder

    A regression needs numbers, and `ocean_proximity` is text. When it is fitted, a `OneHotEncoder`
    records the categories it finds. When it transforms, it makes one column of 0s and 1s for each
    category, with a 1 in the column of the district's own category. Here it leaves out the column
    for `<1H OCEAN` (within an hour of the ocean): a district with 0 in every column is in that
    category, and each of the other columns is compared with it.
    """)
    return


@app.cell
def encoder_before_after(OneHotEncoder, before_after, housing):
    _encoder = OneHotEncoder(drop=["<1H OCEAN"], sparse_output=False).set_output(transform="pandas")
    _encoder.fit(housing[["ocean_proximity"]])
    before_after(_encoder, ["ocean_proximity"], ["categories_"])
    return


@app.cell(hide_code=True)
def column_transformer_intro(mo):
    mo.md(r"""
    ### ColumnTransformer

    A `ColumnTransformer` sends each list of columns to its own transformer and puts the outputs side
    by side, naming each output column after the transformer that made it. By default it drops every
    column it was not given, which is why `population` goes in below and does not come out. Its
    fitted attribute `named_transformers_` gives each inner transformer, fitted.
    """)
    return


@app.cell
def column_transformer_before_after(
    ColumnTransformer,
    OneHotEncoder,
    SimpleImputer,
    StandardScaler,
    before_after,
    housing,
    make_pipeline,
):
    _transformer = ColumnTransformer([
        ("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
         ["total_bedrooms", "median_income"]),
        ("ocean", OneHotEncoder(drop=["<1H OCEAN"], sparse_output=False), ["ocean_proximity"]),
    ]).set_output(transform="pandas")
    _transformer.fit(housing)
    before_after(_transformer, ["total_bedrooms", "median_income", "ocean_proximity", "population"],
                 ["named_transformers_"])
    return


@app.cell(hide_code=True)
def pipeline_intro(mo):
    mo.md(r"""
    ---
    ## The pipeline as a whole

    The diagram shows how the parts fit together, and what each one stores when it is fitted. When the
    pipeline is fitted, each step is fitted in turn on the output of the step before it, and the
    regression is fitted last. When the pipeline predicts, nothing is refitted: each transformer
    applies what it stored, and the regression turns the result into a value in dollars.
    """)
    return


@app.cell(hide_code=True)
def pipeline_diagram(mo):
    # mo.mermaid is a marimo function that draws a diagram from Mermaid's text format.
    mo.mermaid("""
    flowchart LR
        data["DataFrame<br/>one row per district<br/>the columns you chose"] --> ct
        subgraph ct["ColumnTransformer: drops any column it is not given"]
            direction TB
            num["numeric columns"] --> imp["SimpleImputer<br/>fit stores statistics_, the medians<br/>transform fills missing values"]
            imp --> sc["StandardScaler<br/>fit stores mean_ and scale_<br/>transform puts each column in standard deviations"]
            cat["ocean_proximity"] --> oh["OneHotEncoder<br/>fit stores categories_<br/>transform makes one 0/1 column per category"]
        end
        ct --> grid["one table of numbers<br/>the scaled columns and the 0/1 columns, side by side"]
        grid --> lr["LinearRegression<br/>fit estimates coef_ and intercept_"]
        lr --> out["predict<br/>a median house value, in dollars,<br/>for each district"]
    """)
    return


@app.cell(hide_code=True)
def pipeline_function_intro(mo):
    mo.md(r"""
    The function below builds this pipeline for whichever columns you give it, and marimo shows its
    steps. Click on a step to see its settings.
    """)
    return


@app.cell
def define_pipeline(
    ColumnTransformer,
    LinearRegression,
    NUMERIC,
    OneHotEncoder,
    RATIOS,
    SimpleImputer,
    StandardScaler,
    make_pipeline,
):
    def pipeline(columns):
        """Impute and scale the numeric columns, encode ocean_proximity, fit a linear model."""
        numeric = [c for c in columns if c != "ocean_proximity"]
        steps = [("numeric", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()),
                   numeric)]
        if "ocean_proximity" in columns:
            steps.append(("ocean", OneHotEncoder(drop=["<1H OCEAN"], handle_unknown="ignore"),
                           ["ocean_proximity"]))
        return make_pipeline(ColumnTransformer(steps), LinearRegression())

    ALL_COLUMNS = NUMERIC + ["ocean_proximity"] + RATIOS
    pipeline(ALL_COLUMNS)
    return ALL_COLUMNS, pipeline


@app.cell(hide_code=True)
def define_coefficients(pd):
    def coefficients(fitted):
        """A fitted pipeline's coefficients, labelled with the column each one belongs to."""
        names = [n.split("__")[1] for n in fitted[0].get_feature_names_out()]
        return pd.Series(fitted[-1].coef_, index=names, name="coefficient").round(0)

    return (coefficients,)


@app.cell(hide_code=True)
def train_test_intro(mo):
    mo.md(r"""
    ---
    ## Train-test splits

    A model always fits the data it was fitted on better than it fits new data, so a score computed
    on the fitting data overstates how well it will do. The usual remedy is a *train-test split*: set
    some of the districts aside as a *test set* before fitting, fit on the rest (the *training set*),
    and score the predictions on the test set. `train_test_split` does this at random;
    `test_size=0.2` sets aside 20% of the rows, and `random_state` fixes the random choice so that
    the split comes out the same every time the cell runs.
    """)
    return


@app.cell
def make_train_test_split(districts, train_test_split):
    train_districts, test_districts = train_test_split(districts, test_size=0.2,
                                                       random_state=385)
    len(train_districts), len(test_districts)
    return test_districts, train_districts


@app.cell
def fit_and_predict(
    ALL_COLUMNS,
    pipeline,
    r2_score,
    test_districts,
    train_districts,
):
    split_model = pipeline(ALL_COLUMNS)
    split_model.fit(train_districts, train_districts["median_house_value"])  # fit: training set only
    test_predictions = split_model.predict(test_districts)                  # predict: test set
    r2_score(test_districts["median_house_value"], test_predictions)
    return


@app.cell(hide_code=True)
def reliability_intro(mo):
    mo.md(r"""
    The score above is R², the share of the variation in house value between districts that the
    predictions account for: 0 is no better than predicting the average for every district, and 1 is
    perfect. It comes from one random choice of test districts, and a different choice would give a
    different score. Before relying on it, it is worth knowing how much it would move.

    The cell under the slider makes twenty different random splits, fits the pipeline on each training
    set, and scores it on each test set. Please move the slider to use fewer districts and watch how
    far apart the twenty scores spread.
    """)
    return


@app.cell
def district_slider(mo):
    # mo.ui.slider is a marimo function that makes a slider; its .value is the chosen setting.
    district_count = mo.ui.slider(steps=[200, 500, 1000, 2000, 5000, 10000, 20640], value=1000,
                                   label="Districts used", show_value=True)
    district_count
    return (district_count,)


@app.cell(hide_code=True)
def twenty_splits(
    ALL_COLUMNS,
    district_count,
    districts,
    mo,
    pipeline,
    plt,
    r2_score,
    train_test_split,
):
    _used = districts.sample(n=district_count.value, random_state=385)
    _scores = []
    for _seed in range(20):
        _train, _test = train_test_split(_used, test_size=0.2, random_state=_seed)
        _fitted = pipeline(ALL_COLUMNS).fit(_train, _train["median_house_value"])
        _scores.append(r2_score(_test["median_house_value"], _fitted.predict(_test)))

    _fig, _ax = plt.subplots(figsize=(7, 1.8))
    _ax.scatter(_scores, [0] * len(_scores), alpha=0.6)
    _ax.set_xlim(0.3, 0.8)
    _ax.set_yticks([])
    _ax.set_xlabel("R² on the test set")
    _ax.set_title(f"Twenty random test sets, {district_count.value:,} districts")
    _fig.tight_layout()
    # mo.md is a marimo function that displays Markdown text.
    # mo.vstack is a marimo function that stacks outputs one above the other.
    mo.vstack([_fig, mo.md(f"The twenty scores run from **{min(_scores):.2f}** to "
                           f"**{max(_scores):.2f}**.")])
    return


@app.cell(hide_code=True)
def cross_validation_intro(mo):
    mo.md(r"""
    ## Cross-validation

    With all 20,640 districts the twenty scores agree closely, but with a few hundred a single test
    set could make the same model look good or poor. Cross-validation, as the scikit-learn User Guide
    describes it in *Cross-validation: evaluating estimator performance*, uses the data more fully. In
    *k-fold* cross-validation the districts are divided into *k* parts, or folds; the model is fitted
    on *k* − 1 folds and scored on the fold left out, and this is repeated until every fold has been
    left out once. Every district is then used for testing exactly once, and the *k* scores show both
    the typical score and how much it varies. The figure shows 5 folds, the number used below.

    The User Guide makes a second point that matters as much: the data left out must be kept out of
    the preprocessing too, not only out of the model, because an imputer or a scaler fitted on all the
    data has already used the test fold. Passing the whole pipeline to `cross_validate` arranges that,
    since every step is refitted on the training folds each time. The guide also notes that random
    folds suit data like these, in which the rows do not come in groups or in time order.
    """)
    return


@app.cell(hide_code=True)
def folds_figure(plt):
    _fig, _ax = plt.subplots(figsize=(7, 2.4))
    for _round in range(5):
        for _fold in range(5):
            _ax.barh(_round, 1, left=_fold, color="#d95f02" if _fold == _round else "#7570b3",
                     edgecolor="white")
    _ax.set_yticks(range(5), [f"Round {_r + 1}" for _r in range(5)])
    _ax.invert_yaxis()
    _ax.set_xticks([_f + 0.5 for _f in range(5)], [f"Fold {_f + 1}" for _f in range(5)])
    _ax.set_title("5-fold cross-validation: fit on the purple folds, score on the orange one")
    for _side in ("top", "right", "left", "bottom"):
        _ax.spines[_side].set_visible(False)
    _fig.tight_layout()
    _fig
    return


@app.cell
def define_cv_scores(
    KFold,
    cross_validate,
    districts,
    house_value,
    pd,
    pipeline,
):
    def cv_scores(columns):
        """Cross-validated R² (mean and spread over the five folds) and RMSE for these columns."""
        result = cross_validate(pipeline(columns), districts, house_value,
                                 cv=KFold(n_splits=5, shuffle=True, random_state=385),
                                 scoring=("r2", "neg_root_mean_squared_error"))
        return pd.Series({"R²": round(result["test_r2"].mean(), 3),
                          "Spread": round(result["test_r2"].std(), 3),
                          "RMSE": round(-result["test_neg_root_mean_squared_error"].mean())})

    return (cv_scores,)


@app.cell(hide_code=True)
def comparison_intro(mo):
    mo.md(r"""
    The table compares four sets of columns by 5-fold cross-validation. *R²* is the mean over the five
    folds, *Spread* is its standard deviation over the folds, and *RMSE* is the typical size of a
    prediction's error, in dollars.
    """)
    return


@app.cell
def compare_column_sets(ALL_COLUMNS, NUMERIC, cv_scores, pd):
    pd.DataFrame({
        "Median income alone": cv_scores(["median_income"]),
        "Income and location": cv_scores(["median_income", "longitude", "latitude",
                                          "ocean_proximity"]),
        "The nine original columns": cv_scores(NUMERIC + ["ocean_proximity"]),
        "The nine, with Géron's three ratios": cv_scores(ALL_COLUMNS),
    }).T
    return


@app.cell(hide_code=True)
def coefficients_intro(mo):
    mo.md(r"""
    ---
    ## Coefficients

    A linear regression predicts with a straight-line formula: the intercept, plus each column's
    value multiplied by that column's coefficient. Fitting estimates the coefficients, and reading them
    is how you say what the model found. Consider the simplest case first, a regression on median
    income alone, with no scaling.
    """)
    return


@app.cell
def fit_income_model(LinearRegression, districts, house_value):
    income_model = LinearRegression().fit(districts[["median_income"]], house_value)
    income_model.coef_, income_model.intercept_
    return (income_model,)


@app.cell(hide_code=True)
def income_line_plot(districts, house_value, income_model, mo, plt):
    _slope, _intercept = income_model.coef_[0], income_model.intercept_
    _fig, _ax = plt.subplots(figsize=(7, 4))
    _ax.scatter(districts["median_income"], house_value / 1000, s=3, alpha=0.1)
    _ax.plot([0, 15], [_intercept / 1000, (_intercept + 15 * _slope) / 1000], color="#d95f02")
    _ax.set_xlabel("Median income (tens of thousands of dollars)")
    _ax.set_ylabel("Median house value (thousands of dollars)")
    _ax.set_title("The fitted line for median income alone")
    _ax.set_ylim(0, 700)
    # The fitted line keeps rising past the highest values in the data.
    _ax.annotate("aside: what's happening up here?",
                 xy=(13, (_intercept + 13 * _slope) / 1000), xytext=(6.5, 640),
                 arrowprops={"arrowstyle": "->"})
    _fig.tight_layout()
    # mo.md is a marimo function that displays Markdown text.
    # mo.vstack is a marimo function that stacks outputs one above the other.
    mo.vstack([_fig, mo.md(f"""
    The coefficient is **{_slope:,.0f}**. Median income is measured in tens of thousands of dollars,
    so for each additional \\$10,000 of a district's median income, the model predicts a median house
    value **\\${_slope:,.0f}** higher. The intercept, **\\${_intercept:,.0f}**, is the prediction for
    a district with a median income of zero; no district has one, so the intercept only fixes where
    the line sits.
    """)])
    return


@app.cell(hide_code=True)
def scaling_intro(mo):
    mo.md(r"""
    Columns are measured in different units (dollars, years, people, degrees of latitude), so their
    raw coefficients cannot be compared with each other. That is why the pipeline scales them first.
    After a `StandardScaler`, one unit of every column is one standard deviation, and each
    coefficient is the change in the prediction for a district one standard deviation higher on that
    column. The cell below fits the same one-column model with scaling.
    """)
    return


@app.cell
def fit_scaled_income_model(coefficients, districts, house_value, pipeline):
    scaled_income_model = pipeline(["median_income"]).fit(districts, house_value)
    coefficients(scaled_income_model)
    return (scaled_income_model,)


@app.cell(hide_code=True)
def scaled_income_reading(districts, income_model, mo, scaled_income_model):
    _per_sd = scaled_income_model[-1].coef_[0]
    _sd = districts["median_income"].std()
    # mo.md is a marimo function that displays Markdown text.
    mo.md(f"""
    The coefficient is now **{_per_sd:,.0f}**: a district one standard deviation higher in median
    income (about \\${_sd * 10000:,.0f}) is predicted to have a median house value
    **\\${_per_sd:,.0f}** higher. It is the same line as before, since {_sd:.2f} times
    {income_model.coef_[0]:,.0f} is about {_per_sd:,.0f}.
    """)
    return


@app.cell(hide_code=True)
def many_coefficients_intro(mo):
    mo.md(r"""
    With several columns, each coefficient is the change in the prediction for one standard deviation
    more of that column *with the other columns held fixed*. Each `ocean_proximity` coefficient is
    the difference from a district within an hour of the ocean, again with the other columns held
    fixed. The table below reads every coefficient of the model on all the columns in this way.

    Two cautions apply. Columns that move together, such as `population`, `households` and the room
    totals, share the credit between them and can take large coefficients of opposite sign, so they
    are best read as a group. `ISLAND` has only five districts, so its coefficient is difficult to
    interpret.
    """)
    return


@app.cell
def fit_full_model(
    ALL_COLUMNS,
    coefficients,
    districts,
    house_value,
    pipeline,
):
    full_model = pipeline(ALL_COLUMNS).fit(districts, house_value)
    coefficients(full_model)
    return (full_model,)


@app.cell(hide_code=True)
def full_model_readings(coefficients, full_model, pd):
    _rows = []
    for _name, _coef in coefficients(full_model).items():
        _change = f"${abs(_coef):,.0f} {'higher' if _coef > 0 else 'lower'}"
        if _name.startswith("ocean_proximity_"):
            _reading = (f"A district {_name.removeprefix('ocean_proximity_')} is predicted "
                        f"{_change} than one within an hour of the ocean")
        else:
            _reading = f"One standard deviation more {_name} predicts a value {_change}"
        _rows.append({"Column": _name, "Coefficient": f"{_coef:,.0f}", "Reading": _reading})
    pd.DataFrame(_rows).set_index("Column")
    return


@app.cell(hide_code=True)
def practice_columns_intro(mo):
    mo.md(r"""
    ---
    ### Practice: your own columns

    Please write the list of columns yourself in the cell below, then rerun it as you add or remove
    columns, and watch how the score and the coefficients change. The column names are in the table at
    the top of the notebook. Each member of your team should start from different columns, for
    instance one from location, one from the room and population totals, and one from age and income,
    so that between you the team sees more of the data than any one of you would.
    """)
    return


@app.cell
def practice_choose_columns():
    # Replace the placeholder names with columns from the table at the top of the notebook,
    # and delete POSSIBLY_A_THIRD_COLUMN if you want only two.
    my_columns = ["SOME_COLUMN", "SOME_OTHER_COLUMN", "POSSIBLY_A_THIRD_COLUMN"]
    return (my_columns,)


@app.cell
def practice_scores(cv_scores, mo, my_columns):
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder values.
    mo.stop("_COLUMN" in str(my_columns),
            # mo.md is a marimo function that displays Markdown text.
            mo.md("Replace or delete the placeholder names in the cell above with column names.")
            # .callout is a marimo method that puts a message in a coloured box.
            .callout(kind="info"))
    cv_scores(my_columns)
    return


@app.cell
def practice_coefficients(
    coefficients,
    districts,
    house_value,
    mo,
    my_columns,
    pipeline,
):
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder values.
    mo.stop("_COLUMN" in str(my_columns))
    my_model = pipeline(my_columns).fit(districts, house_value)
    coefficients(my_model)
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    In Géron's chapter, a company wants a model that estimates the median house value of any district
    in California, in place of estimates its experts make by hand. Before anyone relies on such a
    model, somebody has to be able to say what it has found and how far its estimates can be trusted.

    > **Build the pipeline, then use it to say what sets a district's house value, and how much of
    > it you can explain.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. The table in the *Cross-validation* section, to say which columns explain most of the variation
       between districts and how much each addition adds (R²), and how far off the predictions
       typically are (RMSE).
    2. The coefficients of a model you fitted yourself, read the same way as in the *Coefficients*
       section, to say in which direction and by roughly how much the main columns move the prediction.
    3. One limitation of your explanation: something the model cannot tell you, or a coefficient that is
       difficult to interpret.

    Then compare your results with your teammates', who started from different columns, and say what
    their results showed that yours did not, and whether that changes your explanation.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each prompt,
    in your own words and with the numbers from your own runs. Each of you should then upload your own
    copy of this notebook to *AE 14* on Canvas, by 23:59 on Thursday.

    | Part of your answer | Points |
    |---|---:|
    | Your explanation: the columns, R² and RMSE, the coefficients, and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other with
    the code. Each of you should run the code on your own laptop rather than watching one screen, and
    start from different columns from your teammates, then compare what you find. Your team may agree
    on an explanation, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholder column names
    in Step 1, run the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_choose_columns():
    # Step 1: choose two or three columns to start with, different from the ones your teammates
    # choose. Replace the placeholder names with column names from the table at the top, and delete
    # POSSIBLY_A_THIRD_COLUMN if you want only two.
    answer_columns = ["SOME_COLUMN", "SOME_OTHER_COLUMN", "POSSIBLY_A_THIRD_COLUMN"]
    return (answer_columns,)


@app.cell
def step2_scores(answer_columns, cv_scores, mo):
    # Step 2: score these columns by cross-validation, and compare the result with the table in the
    # Cross-validation section. Then add or remove columns in Step 1 and run again.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder values.
    mo.stop("_COLUMN" in str(answer_columns),
            # mo.md is a marimo function that displays Markdown text.
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md("Replace or delete the placeholder names in Step 1 with column names.").callout(kind="info"))
    cv_scores(answer_columns)
    return


@app.cell
def step3_coefficients(
    answer_columns,
    coefficients,
    districts,
    house_value,
    mo,
    pipeline,
):
    # Step 3: fit the pipeline on every district and list the coefficients. Read them the same way
    # as in the Coefficients section above.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder values.
    mo.stop("_COLUMN" in str(answer_columns))
    answer_model = pipeline(answer_columns).fit(districts, house_value)
    coefficients(answer_model)
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your own
    words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L16_pipelines.py` to *AE 14* on Canvas by 23:59 on Thursday. We will cross-reference your claims about
    evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_columns(mo):
    mo.md(r"""
    **The columns that explain the most, and how much R² each one adds**
    """)
    return


@app.cell
def step4_answer_columns(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_error(mo):
    mo.md(r"""
    **The typical error (RMSE), and its meaning for one district's estimate**
    """)
    return


@app.cell
def step4_answer_error(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_coefficients(mo):
    mo.md(r"""
    **The direction and size of the two or three largest coefficients**
    """)
    return


@app.cell
def step4_answer_coefficients(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_limitation(mo):
    mo.md(r"""
    **One limitation of your explanation**
    """)
    return


@app.cell
def step4_answer_limitation(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_teammates(mo):
    mo.md(r"""
    **Your teammates' results, and what they add to yours**
    """)
    return


@app.cell
def step4_answer_teammates(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


if __name__ == "__main__":
    app.run()
