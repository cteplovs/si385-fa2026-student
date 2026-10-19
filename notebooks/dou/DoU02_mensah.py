# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "pandas>=3.0.5",
#     "matplotlib>=3.9",
#     "statsmodels>=0.14",
# ]
# ///

import marimo

__generated_with = "0.25.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    import matplotlib.pyplot as plt
    import pandas as pd
    import statsmodels.formula.api as smf

    REMOTE = ("https://raw.githubusercontent.com/"
              "cteplovs/si385-fa2026-student/main/data/")

    def course_csv(name):
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_csv(local, index_col=0)
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as _response:
            return pd.read_csv(BytesIO(_response.read()), index_col=0)

    return course_csv, mo, plt, smf


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # What does a mile cost?

    ## Note for the lending committee, draft 2

    *D. Mensah, Auto Lending Analytics.  Handed over on moving teams.*

    ---

    The committee sets a mileage adjustment on used-car loans and asked how much
    each additional mile takes off a car's value.  This notebook is the analysis
    behind the figure in the note.

    **Finding: every 10,000 miles knocks about $280 off a used car's asking price,
    and the effect is highly significant (p < 0.001).**

    Anyone picking this up: the numbers regenerate from the listings file, and the
    committee wants the figure confirmed before next year's rates are set.
    """)
    return


@app.cell
def _(course_csv):
    listings = course_csv("craigslist_vehicles_sample.csv")
    listings.head()
    return (listings,)


@app.cell
def _(listings):
    # How big is this thing.
    print(f"{len(listings):,} listings")
    print(f"{listings['manufacturer'].nunique()} manufacturers, "
          f"{listings['state'].nunique()} states")
    print(f"asking prices from ${listings['price'].min():,.0f} to ${listings['price'].max():,.0f}")
    return


@app.cell
def _(listings):
    # Work in units of 10,000 miles so the slope reads directly as the
    # adjustment per 10,000.
    cars = listings.copy()
    cars["miles_10k"] = cars["odometer"] / 10_000
    return (cars,)


@app.cell
def _(cars, smf):
    # The headline regression.
    mileage_model = smf.ols("price ~ miles_10k", data=cars).fit()
    slope = mileage_model.params["miles_10k"]
    low, high = mileage_model.conf_int().loc["miles_10k"]
    print(f"each 10,000 miles takes ${-slope:,.0f} off the price  (95% CI ${-high:,.0f} to ${-low:,.0f})")
    print(f"p = {mileage_model.pvalues['miles_10k']:.1e}, n = {int(mileage_model.nobs):,}")
    return (mileage_model,)


@app.cell
def _(cars, mileage_model, plt):
    # The fit, for the appendix.
    _fig, _ax = plt.subplots(figsize=(7, 4))
    _ax.scatter(cars["miles_10k"], cars["price"], s=4, alpha=0.3, color="#4477aa")
    _x = cars["miles_10k"].dropna().sort_values()
    _ax.plot(_x, mileage_model.params["Intercept"] + mileage_model.params["miles_10k"] * _x,
             color="#ee6677")
    _ax.set_xlabel("odometer (10,000 miles)")
    _ax.set_ylabel("asking price ($)")
    _fig
    return


@app.cell
def _(cars, smf):
    # Holds up for the big makes too.
    _rows = {}
    for _make in ["ford", "chevrolet", "toyota", "nissan", "honda"]:
        _fit = smf.ols("price ~ miles_10k", data=cars[cars["manufacturer"] == _make]).fit()
        _rows[_make] = round(_fit.params["miles_10k"])
    _rows
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## For the note

    Each 10,000 miles takes about $280 off the asking price, and with a p-value
    that small the committee can treat the figure as established.  Suggest the
    adjustment be set at $280 per 10,000 miles across the board.
    """)
    return


if __name__ == "__main__":
    app.run()
