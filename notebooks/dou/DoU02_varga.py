# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "pandas>=3.0.5",
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

    return course_csv, mo, smf


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # What does a mile cost? A second look

    ## Note for the lending committee

    *S. Varga, Risk Analytics.*

    ---

    The committee asked Risk Analytics to check Auto Lending's mileage figure before
    next year's rates are set.  This notebook works from the same listings file.

    **Finding: once implausible listings are set aside and the car's age is held
    fixed, every 10,000 miles takes about $630 off the asking price (p < 0.001).**
    That is more than twice the figure the committee currently uses.
    """)
    return


@app.cell
def _(course_csv):
    listings = course_csv("craigslist_vehicles_sample.csv")
    listings.head()
    return (listings,)


@app.cell
def _(listings):
    # Set aside listings that cannot be real sales: asking prices under $500 and
    # odometer readings under 100 or over 500,000 miles.
    cars = listings[(listings["price"] >= 500)
                    & listings["odometer"].between(100, 500_000)].copy()
    cars["miles_10k"] = cars["odometer"] / 10_000
    cars["age"] = 2020 - cars["year"]
    print(f"{len(listings):,} listings, {len(cars):,} kept")
    return (cars,)


@app.cell
def _(cars, smf):
    # Mileage and age move together, so hold age fixed.
    varga_model = smf.ols("price ~ miles_10k + age", data=cars).fit()
    _slope = varga_model.params["miles_10k"]
    _low, _high = varga_model.conf_int().loc["miles_10k"]
    print(f"each 10,000 miles takes ${-_slope:,.0f} off the price  (95% CI ${-_high:,.0f} to ${-_low:,.0f})")
    print(f"each year of age takes ${-varga_model.params['age']:,.0f} off")
    print(f"p = {varga_model.pvalues['miles_10k']:.1e}, n = {int(varga_model.nobs):,}, "
          f"R² = {varga_model.rsquared:.2f}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## For the note

    Suggest the adjustment be raised to $630 per 10,000 miles.  The current $280
    understates what mileage costs, because it mixes mileage with age and keeps
    listings that cannot be real.
    """)
    return


if __name__ == "__main__":
    app.run()
