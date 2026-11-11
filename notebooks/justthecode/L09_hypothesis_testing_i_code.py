# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "pyarrow>=25.0.1",
# ]
# ///

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 9, the code on its own: the shuffle test and many tests at once

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    This notebook goes with `notebooks/lectures/L09_hypothesis_testing_i.py`. The session notebook
    uses functions written for it, which you will not have when you work on your own data. Each
    section below does one of the session's computations with only pandas and NumPy, starting from
    a data frame, so that you can copy it into your project or another notebook. The data are the
    NBA free-throw trips from sessions 8 and 9, with one row for each pair of free throws.

    Each code cell starts with a comment listing the imports it uses, and its variable names start
    with `_`, which keeps them local to the cell, so you can paste a cell anywhere in a marimo
    notebook without a clash with names in other cells.
    """)
    return


@app.cell
def imports():
    import marimo as mo
    import numpy as np
    import pandas as pd

    return mo, np, pd


@app.cell(hide_code=True)
def data_helper(pd):
    import urllib.request
    from io import BytesIO
    from pathlib import Path

    REMOTE = ("https://raw.githubusercontent.com/"
              "cteplovs/si385-fa2026-student/main/data/")


    def course_parquet(name):
        """Read one of the course Parquet files.

        The copy in the course folder is the one to prefer, and it is what you get if you are
        running this the documented way. The fallback to the public repository is there so that
        the notebook also runs on molab, provided you have a network.
        """
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_parquet(local)
        except (NameError, IndexError, OSError):
            pass
        with urllib.request.urlopen(REMOTE + name) as response:
            return pd.read_parquet(BytesIO(response.read()))

    return (course_parquet,)


@app.cell
def load_trips(course_parquet):
    trips = course_parquet("nba_free_throw_pairs.parquet")
    trips.head()
    return (trips,)


@app.cell(hide_code=True)
def shuffle_intro(mo):
    mo.md(r"""
    ---
    ## A shuffle test

    If one column made no difference to another, its values could be shuffled among the rows
    without changing anything. In the cell below, we compute the observed difference between two
    groups, shuffle the column that defines the groups 2,000 times, recompute the difference each
    time, and report the share of shuffles at least as large as the observed one, which is the
    one-tailed p-value. The two-tailed p-value counts shuffles at least as far from zero in either
    direction. To use it on other data, you would change the rows and the two columns.
    """)
    return


@app.cell
def shuffle_code(np, trips):
    # Uses: import numpy as np
    _rows = trips[trips["player"] == "LeBron James"]
    _group = _rows["first_made"].to_numpy()
    _outcome = _rows["second_made"].to_numpy()

    def _difference(group):
        return 100 * (_outcome[group].mean() - _outcome[~group].mean())

    _observed = _difference(_group)
    _rng = np.random.default_rng(385)
    _shuffled = np.array([_difference(_rng.permutation(_group)) for _ in range(2000)])
    print(f"observed difference {_observed:.1f}")
    print(f"one-tailed p-value {(_shuffled >= _observed).mean():.3f}")
    print(f"two-tailed p-value {(np.abs(_shuffled) >= abs(_observed)).mean():.3f}")
    return


@app.cell(hide_code=True)
def many_intro(mo):
    mo.md(r"""
    ---
    ## The same test on many groups

    In the cell below, we run the shuffle test once for each player with at least 500 trips and
    50 missed first shots, then count how many pass at 5%, next to the number we would expect to
    pass by chance alone if none of them had a real effect. It uses 500 shuffles for each player
    rather than the session's 2,000, so that it runs in a few seconds, and its count can differ
    from the session's by one or two.
    """)
    return


@app.cell
def many_code(np, pd, trips):
    # Uses: import numpy as np
    #       import pandas as pd
    _rng = np.random.default_rng(385)
    _results = []
    for _player, _rows in trips.groupby("player"):
        _group = _rows["first_made"].to_numpy()
        _outcome = _rows["second_made"].to_numpy()
        if len(_rows) < 500 or (~_group).sum() < 50:
            continue
        _observed = 100 * (_outcome[_group].mean() - _outcome[~_group].mean())
        _shuffled = np.array([
            100 * (_outcome[_s].mean() - _outcome[~_s].mean())
            for _s in (_rng.permutation(_group) for _ in range(500))
        ])
        _results.append({"player": _player, "trips": len(_rows), "difference": _observed,
                         "p_value": (_shuffled >= _observed).mean()})
    _table = pd.DataFrame(_results).sort_values("p_value")
    print(f"{len(_table)} players tested, {(_table['p_value'] < 0.05).sum()} pass at 5%, "
          f"about {0.05 * len(_table):.0f} expected by chance alone")
    _table.head(10).round(3)
    return


if __name__ == "__main__":
    app.run()
