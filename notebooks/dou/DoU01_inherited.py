# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
#     "matplotlib>=3.9",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    import pandas as pd
    import matplotlib.pyplot as plt

    REMOTE = ("https://raw.githubusercontent.com/"
              "cteplovs/si385-fa2026-student/main/data/")

    def course_parquet(name):
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_parquet(local)
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as _response:
            return pd.read_parquet(BytesIO(_response.read()))

    return course_parquet, mo, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Are independent restaurants held to a different standard?

    ## Briefing note for the Small Business Services committee — draft 3

    *R. Okonjo, Office of Data Analytics.  Handed over on leaving.*

    ---

    The committee asked whether the chains have an advantage in health
    inspections.  This notebook is the analysis behind the headline number in the
    briefing.

    **Finding: independent restaurants score about 44% worse than chain
    restaurants.**  A higher score is worse — the score counts violation points,
    so zero is a clean inspection.

    Anyone picking this up: the numbers regenerate from the source file, and the
    committee wants the figure updated before the March session.
    """)
    return


@app.cell
def _(course_parquet):
    inspections = course_parquet("nyc_inspections.parquet")
    inspections.head()
    return (inspections,)


@app.cell
def _(inspections):
    # How big is this thing.
    print(f"{len(inspections):,} rows")
    print(f"{inspections['restaurant_id'].nunique():,} restaurants")
    print(f"{inspections['inspection_date'].min()} to {inspections['inspection_date'].max()}")
    return


@app.cell
def _(inspections, pd):
    # The file has no chain flag, so build one from the trading name.  A name
    # operating at ten or more restaurant_ids is a chain.
    locations = inspections.groupby("name")["restaurant_id"].nunique()
    chain_names = set(locations[locations >= 10].index)

    flagged = inspections.copy()
    flagged["kind"] = pd.Categorical(
        flagged["name"].isin(chain_names).map({True: "chain", False: "independent"}),
        categories=["chain", "independent"],
    )

    print(f"{len(chain_names)} chain names, "
          f"{flagged['kind'].value_counts()['chain']:,} of the rows")
    return (flagged,)


@app.cell
def _(flagged):
    # The headline comparison.
    summary = flagged.groupby("kind", observed=True)["score"].agg(["count", "mean"])
    summary["mean"] = summary["mean"].round(2)
    summary
    return (summary,)


@app.cell
def _(summary):
    gap = summary.loc["independent", "mean"] - summary.loc["chain", "mean"]
    pct = 100 * gap / summary.loc["chain", "mean"]
    print(f"independents score {gap:.2f} points worse, which is {pct:.0f}%")
    return


@app.cell
def _(flagged, plt):
    # Distribution behind the two means.
    _fig, _ax = plt.subplots(figsize=(7, 4))
    for _k, _c in [("chain", "#4477aa"), ("independent", "#ee6677")]:
        _ax.hist(flagged.loc[flagged["kind"] == _k, "score"],
                 bins=40, range=(0, 80), alpha=0.55, label=_k,
                 density=True, color=_c)
    _ax.set_xlabel("inspection score (higher is worse)")
    _ax.set_ylabel("density")
    _ax.legend(frameon=False)
    _fig
    return


@app.cell
def _(flagged):
    # Holds up across the boroughs too.
    flagged.groupby(["borough", "kind"], observed=True)["score"].mean().unstack().round(2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## For the briefing

    Independents run about 44% above the chains on inspection score, and the
    pattern holds in every borough. The committee's line can be that the gap is
    real and consistent across the city.

    ### Still to do

    - Update before the March session.
    - Committee asked for a borough breakdown in the appendix; the table above
      will do.
    """)
    return


if __name__ == "__main__":
    app.run()
