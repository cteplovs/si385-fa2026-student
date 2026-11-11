# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "scipy>=1.13",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 11: Categorical data, contingency tables and the chi-square test

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, October 7, 2026

    **Reading due today:** Bruce et al., *AI-Assisted Statistics for Data Scientists*, ch. 3,
    § *Chi-Square Test*

    ---

    ### Today you will be able to

    - Build a contingency table and read it as rates within groups
    - Compute the counts you would expect if two variables were unrelated, and the chi-square
      statistic from them
    - Run the chi-square test by resampling and with the chi-square distribution, and say what its
      degrees of freedom count
    - Tell how strong an association is from how sure you can be of it, and say what a scan of many
      tables does to a p-value

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Data | 5 |
    | Contingency tables | 10 |
    | Expected counts and the chi-square statistic | 10 |
    | The chi-square test | 10 |
    | Strength, certainty and many tables | 10 |
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
    import numpy as np
    import pandas as pd
    from scipy import stats

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

    return course_csv, mo, np, pd, plt, stats


@app.cell(hide_code=True)
def code_on_its_own_note(mo):
    mo.md(r"""
    ### Sections headed *The code on its own*

    Each technique ends with a section headed *The code on its own*. The dropdowns, sliders and
    plots above it call functions written for this notebook, which you will not have when you work
    on your own data. The code in those sections uses only pandas, NumPy and SciPy, starts from a
    data frame, and does the computation without any controls, so that you can copy it into your
    project or another notebook. Each code cell starts with a comment listing the imports it uses,
    and its variable names start with `_`, which keeps them local to the cell.
    """)
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## Data

    The file holds the 2018 Central Park Squirrel Census. Between 6 and 20 October 2018, volunteers
    walked every part of the park, morning and afternoon, and recorded each squirrel they saw: one
    row per sighting, 3,023 in all. Each sighting records four facts about the squirrel and the
    moment, and a list of things the squirrel was doing, each true or false.

    | Facts about the sighting | Description |
    |---|---|
    | `primary_fur_color` | Gray, Cinnamon or Black |
    | `age` | Adult or Juvenile |
    | `shift` | AM or PM |
    | `location` | Ground Plane, or Above Ground (in a tree or on a structure) |

    | Behaviours | Description |
    |---|---|
    | `running`, `chasing`, `climbing`, `eating`, `foraging` | What the squirrel was doing |
    | `kuks`, `quaas`, `moans` | Calls: a kuk is a short bark, and quaas and moans are alarm calls |
    | `tail_flags`, `tail_twitches` | Tail movements, also used as signals |
    | `approaches`, `indifferent`, `runs_from` | How the squirrel responded to the volunteer |

    Some sightings leave a fact blank, and four record the age as `?`. Each table below uses the
    sightings that record the fact it is about.
    """)
    return


@app.cell
def load_squirrels(course_csv):
    squirrels = course_csv("nyc_squirrels.csv")
    squirrels["age"] = squirrels["age"].where(squirrels["age"].isin(["Adult", "Juvenile"]))
    FACTORS = {"Fur colour": "primary_fur_color", "Age": "age", "Time of day": "shift",
               "Where it was seen": "location"}
    BEHAVIOURS = ["running", "chasing", "climbing", "eating", "foraging", "kuks", "quaas",
                  "moans", "tail_flags", "tail_twitches", "approaches", "indifferent",
                  "runs_from"]
    squirrels[list(FACTORS.values()) + BEHAVIOURS[:5]].head()
    return BEHAVIOURS, FACTORS, squirrels


@app.cell(hide_code=True)
def tables_intro(mo):
    mo.md(r"""
    ---
    ## Contingency tables

    A *contingency table* counts the rows that fall in each combination of two categorical
    variables: here, one fact about the sighting against one behaviour. The counts alone are hard to
    compare when the groups differ in size (there are 2,473 gray squirrels and 103 black ones), so
    the usual next step is to turn each row of the table into rates: the share of the gray squirrels
    that were running, the share of the black ones, and so on. If the fact made no difference to the
    behaviour, the rates would be about the same in every row.

    Please choose a fact and a behaviour, and switch between the counts and the rates.
    """)
    return


@app.cell
def table_controls(BEHAVIOURS, FACTORS, mo):
    # mo.ui.dropdown is a marimo function that makes a drop-down menu. Given a dictionary, it shows
    # the keys and its .value is the value of the chosen key.
    factor_pick = mo.ui.dropdown(options=FACTORS, value="Fur colour", label="Fact")
    behaviour_pick = mo.ui.dropdown(options=BEHAVIOURS, value="approaches", label="Behaviour")
    # mo.ui.radio is a marimo function that makes a set of buttons, of which one can be chosen.
    table_view = mo.ui.radio(options=["Counts", "Rates within each row"], value="Counts",
                             inline=True)
    # mo.hstack is a marimo function that puts outputs side by side.
    mo.hstack([factor_pick, behaviour_pick, table_view], justify="start", gap=2)
    return behaviour_pick, factor_pick, table_view


@app.cell
def define_contingency(pd, squirrels):
    def contingency(factor, behaviour):
        """Count the sightings in each combination of a fact and a behaviour."""
        _rows = squirrels.dropna(subset=[factor, behaviour])
        return pd.crosstab(_rows[factor], _rows[behaviour].map({True: "yes", False: "no"}))

    return (contingency,)


@app.cell
def contingency_view(behaviour_pick, contingency, factor_pick, plt, table_view, mo):
    observed_table = contingency(factor_pick.value, behaviour_pick.value)
    _rates = observed_table["yes"] / observed_table.sum(axis=1)

    if table_view.value == "Counts":
        _shown = observed_table.assign(total=observed_table.sum(axis=1))
    else:
        _shown = observed_table.div(observed_table.sum(axis=1), axis=0).round(3)

    _fig, _ax = plt.subplots(figsize=(6, 0.5 * len(_rates) + 1.2))
    _ax.barh(_rates.index.astype(str), _rates, color="#1f4e79")
    for _i, (_rate, _n) in enumerate(zip(_rates, observed_table.sum(axis=1))):
        _ax.text(_rate, _i, f"  {_rate:.1%} of {_n:,}", va="center", fontsize=9)
    _ax.set_xlim(0, min(1, _rates.max() * 1.6))
    _ax.set_xlabel(f"Share of sightings with {behaviour_pick.value}")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    mo.hstack([_shown, _fig], justify="start", align="center", gap=2)
    return (observed_table,)


@app.cell(hide_code=True)
def table_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we count the sightings for each combination of fur colour and one behaviour
    with `pd.crosstab`, with the totals in the margins, and then give the same table as shares of
    each row. To use it on other data, you would change the two columns.
    """)
    return


@app.cell
def table_code(pd, squirrels):
    # Uses: import pandas as pd
    _rows = squirrels.dropna(subset=["primary_fur_color", "approaches"])
    print(pd.crosstab(_rows["primary_fur_color"], _rows["approaches"], margins=True))
    print()
    print(pd.crosstab(_rows["primary_fur_color"], _rows["approaches"], normalize="index").round(3))
    return


@app.cell(hide_code=True)
def expected_intro(mo):
    mo.md(r"""
    ---
    ## Expected counts and the chi-square statistic

    The chi-square test measures how far the table is from the table you would expect if the fact and
    the behaviour were unrelated. That table keeps the row totals and the column totals and spreads
    the counts in proportion. If 6% of all sightings recorded the behaviour, a row of 392 sightings
    would be expected to have 6% of 392 with it. In general, the expected count for each cell is

    $$E = \frac{\text{row total} \times \text{column total}}{\text{grand total}}$$

    The chi-square statistic adds up how far each observed count O is from its expected count E,
    scaled by E so that a gap of 10 counts for more in a small cell than in a large one:

    $$\chi^2 = \sum \frac{(O - E)^2}{E}$$

    The tables below give the observed counts, the expected counts, and each cell's share of the
    statistic, for the fact and the behaviour you chose above. The cells with the largest shares are
    the ones that make the table differ from independence. The last table gives the sign as well,
    as $(O - E)/\sqrt{E}$, so that you can see whether a group has more or fewer than expected.
    """)
    return


@app.cell
def define_chi_square(np, pd):
    def chi_square(table):
        """The chi-square statistic for a table of counts, and the table of expected counts."""
        _observed = table.to_numpy(dtype=float)
        _expected = np.outer(_observed.sum(axis=1), _observed.sum(axis=0)) / _observed.sum()
        _statistic = float(((_observed - _expected) ** 2 / _expected).sum())
        return _statistic, pd.DataFrame(_expected, index=table.index, columns=table.columns)

    return (chi_square,)


@app.cell
def expected_view(chi_square, mo, np, observed_table):
    observed_statistic, expected_table = chi_square(observed_table)
    _contribution = (observed_table - expected_table) ** 2 / expected_table
    _signed = (observed_table - expected_table) / np.sqrt(expected_table)


    def _labelled(title, frame, digits):
        # mo.vstack is a marimo function that stacks outputs one above the other.
        return mo.vstack([mo.md(f"**{title}**"), frame.round(digits)])


    mo.vstack([
        mo.hstack([_labelled("Observed, O", observed_table, 0),
                   _labelled("Expected, E", expected_table, 1),
                   _labelled("(O − E)² / E", _contribution, 2),
                   _labelled("(O − E) / √E", _signed, 2)], justify="start", gap=2),
        mo.md(f"The chi-square statistic is the sum of the third table: "
              f"**{observed_statistic:.2f}**."),
    ])
    return expected_table, observed_statistic


@app.cell(hide_code=True)
def practice_expected_intro(mo):
    mo.md(r"""
    ### Practice: one expected count by hand

    Please compute the expected count in the first row's `yes` column yourself, from the observed
    table's totals, and check it against the expected table above. Replace `None` in the cell below.
    `observed_table.sum(axis=1)` gives the row totals, `observed_table.sum(axis=0)` the column
    totals, and `observed_table.to_numpy().sum()` the grand total.
    """)
    return


@app.cell
def practice_expected():
    my_expected = None
    my_expected
    return


@app.cell(hide_code=True)
def expected_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute each cell's expected count from its row total, its column total
    and the grand total, and then the chi-square statistic as the sum of (O − E)² / E over the cells.
    """)
    return


@app.cell
def expected_code(np, pd, squirrels):
    # Uses: import numpy as np
    #       import pandas as pd
    _rows = squirrels.dropna(subset=["primary_fur_color", "approaches"])
    _observed = pd.crosstab(_rows["primary_fur_color"], _rows["approaches"])
    _expected = pd.DataFrame(
        np.outer(_observed.sum(axis=1), _observed.sum(axis=0)) / _observed.to_numpy().sum(),
        index=_observed.index, columns=_observed.columns)
    print(_expected.round(1))
    print()
    print(f"chi-square: {((_observed - _expected) ** 2 / _expected).to_numpy().sum():.2f}")
    return


@app.cell(hide_code=True)
def test_intro(mo):
    mo.md(r"""
    ---
    ## The chi-square test

    A statistic of a few units could be chance. The reading's resampling test measures how large the
    statistic gets when the fact makes no difference:

    1. Put every sighting's yes or no for the behaviour in one box.
    2. Shuffle the box and deal the answers back to the sightings, so that each group keeps its size
       but the behaviour is now unrelated to the fact. Compute the chi-square statistic for the
       dealt table.
    3. Repeat 2,000 times. The p-value is the share of deals whose statistic is at least as large as
       the real one.

    When the expected counts are not too small (a common rule is at least 5 in every cell), the
    statistic also follows a known distribution when the fact makes no difference: the chi-square
    distribution with (*r* − 1)(*c* − 1) *degrees of freedom*, where *r* and *c* are the numbers of
    rows and columns. That is the number of cells you could fill in freely before the row and
    column totals fix the rest. A table of three colours by yes and no has (3 − 1)(2 − 1) = 2. The
    curve in the figure is that distribution, and the formula's p-value is the area under it beyond
    the real statistic.
    """)
    return


@app.cell
def define_resampled(chi_square, np, pd, squirrels):
    def resampled(factor, behaviour, deals=2000, seed=385):
        """The chi-square statistics of the dealt tables, for one fact and one behaviour."""
        _rows = squirrels.dropna(subset=[factor, behaviour])
        _groups = _rows[factor].to_numpy()
        _box = _rows[behaviour].to_numpy()
        _rng = np.random.default_rng(seed)
        return np.array([chi_square(pd.crosstab(_groups, _rng.permutation(_box)))[0]
                         for _ in range(deals)])

    return (resampled,)


@app.cell
def test_view(
    behaviour_pick,
    expected_table,
    factor_pick,
    mo,
    np,
    observed_statistic,
    observed_table,
    plt,
    resampled,
    stats,
):
    # mo.status.spinner is a marimo function that shows a spinner while the indented code runs.
    with mo.status.spinner(title="Dealing 2,000 tables"):
        _dealt = resampled(factor_pick.value, behaviour_pick.value)
    _dof = (observed_table.shape[0] - 1) * (observed_table.shape[1] - 1)
    _p_resampled = (_dealt >= observed_statistic).mean()
    _p_formula = stats.chi2.sf(observed_statistic, _dof)

    _fig, _ax = plt.subplots(figsize=(7, 3.2))
    _top = max(_dealt.max(), observed_statistic) * 1.05
    _ax.hist(_dealt, bins=50, range=(0, _top), density=True, color="#9ca3af",
             label="2,000 dealt tables")
    _x = np.linspace(0.01, _top, 300)
    _ax.plot(_x, stats.chi2.pdf(_x, _dof), color="#1f4e79",
             label=f"chi-square distribution, {_dof} df")
    _ax.axvline(observed_statistic, color="#c2410c", linewidth=2, label="the real statistic")
    _ax.set_xlabel("Chi-square statistic")
    _ax.set_yticks([])
    _ax.legend(frameon=False)
    _ax.spines[["top", "right", "left"]].set_visible(False)
    _fig.tight_layout()

    _small = int((expected_table.to_numpy() < 5).sum())
    _warning = (f" {_small} cell(s) have an expected count below 5, so the formula's p-value is "
                "less reliable than the resampled one here." if _small else "")
    mo.vstack([_fig, mo.md(f"""
    The share of dealt tables at least as far from independence as the real one is
    **{_p_resampled:.4f}**, and the chi-square distribution gives **{_p_formula:.2g}**.{_warning}
    A resampled p-value of 0.0000 means only that none of the 2,000 deals reached the real
    statistic.
    """)])
    return


@app.cell(hide_code=True)
def test_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we run the reading's resampling test, shuffling the behaviour among the
    sightings 2,000 times, and then the formula version with `stats.chi2_contingency`, which gives
    the statistic, the p-value from the chi-square distribution, the degrees of freedom and the
    expected counts. `correction=False` turns off a correction that SciPy applies to tables with two
    rows and two columns, so that its statistic matches the one computed by hand.
    """)
    return


@app.cell
def test_code(np, pd, squirrels, stats):
    # Uses: import numpy as np
    #       import pandas as pd
    #       from scipy import stats
    _rows = squirrels.dropna(subset=["primary_fur_color", "approaches"])
    _groups = _rows["primary_fur_color"].to_numpy()
    _outcome = _rows["approaches"].to_numpy()

    def _statistic(outcome):
        observed = pd.crosstab(_groups, outcome).to_numpy()
        expected = np.outer(observed.sum(axis=1), observed.sum(axis=0)) / observed.sum()
        return ((observed - expected) ** 2 / expected).sum()

    _real = _statistic(_outcome)
    _rng = np.random.default_rng(385)
    _dealt = np.array([_statistic(_rng.permutation(_outcome)) for _ in range(2000)])
    print(f"chi-square {_real:.2f}, resampled p-value {(_dealt >= _real).mean():.4f}")

    _result = stats.chi2_contingency(pd.crosstab(_groups, _outcome), correction=False)
    print(f"chi-square {_result.statistic:.2f}, {_result.dof} degrees of freedom, "
          f"p-value from the chi-square distribution {_result.pvalue:.2g}")
    return


@app.cell(hide_code=True)
def strength_intro(mo):
    mo.md(r"""
    ---
    ## Strength, certainty and many tables

    ### Strength and certainty

    The chi-square statistic grows with the number of sightings as well as with the strength of the
    association. If the census had been ten times larger, with exactly the same rates, every count
    would be ten times larger and so would the statistic, while the rates themselves would not have
    changed at all. A small p-value therefore means that you can be sure there is some association,
    not that the association is strong.

    Two measures of strength do not grow with the sample. The simplest is the gap between the
    highest and the lowest rate, in percentage points. Another is *Cramér's V*, which scales the
    statistic by the number of sightings and the size of the table so that it runs from 0 (no
    association) to 1 (the fact determines the behaviour):

    $$V = \sqrt{\frac{\chi^2}{n \times (\min(r, c) - 1)}}$$

    Please move the slider to pretend that the census was larger, with the same rates, and watch
    which numbers change.
    """)
    return


@app.cell
def scale_control(mo):
    census_scale = mo.ui.slider(steps=[1, 2, 5, 10, 20], value=1,
                                label="Census size, times the real one", show_value=True)
    census_scale
    return (census_scale,)


@app.cell
def scale_view(census_scale, chi_square, mo, np, observed_table, stats):
    _scaled = observed_table * census_scale.value
    _statistic, _ = chi_square(_scaled)
    _n = _scaled.to_numpy().sum()
    _v = np.sqrt(_statistic / (_n * (min(_scaled.shape) - 1)))
    _rates = _scaled["yes"] / _scaled.sum(axis=1)
    _dof = (_scaled.shape[0] - 1) * (_scaled.shape[1] - 1)
    mo.hstack([
        # mo.stat is a marimo function that displays a single number with a label.
        mo.stat(value=f"{_n:,}", label="Sightings"),
        mo.stat(value=f"{_statistic:,.1f}", label="Chi-square"),
        mo.stat(value=f"{stats.chi2.sf(_statistic, _dof):.2g}", label="p-value"),
        mo.stat(value=f"{(_rates.max() - _rates.min()) * 100:.1f}", label="Gap in rates, points"),
        mo.stat(value=f"{_v:.3f}", label="Cramér's V"),
    ], justify="start", gap=2)
    return


@app.cell(hide_code=True)
def strength_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the two measures of strength for one table: the gap between the
    highest and lowest rate, in percentage points, and Cramér's V.
    """)
    return


@app.cell
def strength_code(np, pd, squirrels, stats):
    # Uses: import numpy as np
    #       import pandas as pd
    #       from scipy import stats
    _rows = squirrels.dropna(subset=["primary_fur_color", "approaches"])
    _table = pd.crosstab(_rows["primary_fur_color"], _rows["approaches"])
    _rates = _table[True] / _table.sum(axis=1)
    _chi2 = stats.chi2_contingency(_table, correction=False).statistic
    _v = np.sqrt(_chi2 / (_table.to_numpy().sum() * (min(_table.shape) - 1)))
    print(f"gap in rates: {100 * (_rates.max() - _rates.min()):.1f} points")
    print(f"Cramér's V: {_v:.3f}")
    return


@app.cell(hide_code=True)
def scan_intro(mo):
    mo.md(r"""
    ### Many tables

    There are four facts and thirteen behaviours, so 52 tables could be tested. Session 10's
    multiplicity problem applies in full: at a cutoff of 0.05, a scan of 52 tables would turn up two
    or three "significant" associations even if no fact made any difference to any behaviour. The
    Bonferroni correction divides the cutoff by the number of tests, here 0.05/52, or about 0.001.

    The table gives Cramér's V for every pair of a fact and a behaviour, with a star where the
    p-value passes the corrected cutoff. Please look for the row or column where the largest values
    sit before you look at the stars.
    """)
    return


@app.cell
def define_scan(BEHAVIOURS, FACTORS, chi_square, contingency, np, pd, stats):
    def scan():
        """Chi-square p-value, Cramér's V and the gap in rates for every fact and behaviour."""
        _records = []
        for _label, _factor in FACTORS.items():
            for _behaviour in BEHAVIOURS:
                _table = contingency(_factor, _behaviour)
                _statistic, _ = chi_square(_table)
                _n = _table.to_numpy().sum()
                _rates = _table["yes"] / _table.sum(axis=1)
                _records.append({
                    "fact": _label, "behaviour": _behaviour,
                    "p": stats.chi2.sf(_statistic, (_table.shape[0] - 1)),
                    "V": np.sqrt(_statistic / (_n * (min(_table.shape) - 1))),
                    "gap in rates": _rates.max() - _rates.min(),
                    "highest": _rates.idxmax(), "lowest": _rates.idxmin(),
                })
        return pd.DataFrame(_records)


    scan_results = scan()
    return (scan_results,)


@app.cell
def scan_view(scan_results):
    _cutoff = 0.05 / len(scan_results)
    _marked = scan_results.assign(
        cell=[f"{_v:.2f}{' *' if _p < _cutoff else ''}"
              for _v, _p in zip(scan_results["V"], scan_results["p"])])
    _marked.pivot(index="behaviour", columns="fact", values="cell").loc[
        scan_results["behaviour"].unique()]
    return


@app.cell(hide_code=True)
def scan_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we test one fact against every behaviour, list the p-values, and mark the
    ones below the Bonferroni cutoff, 0.05 divided by the number of tests.
    """)
    return


@app.cell
def scan_code(pd, squirrels, stats):
    # Uses: import pandas as pd
    #       from scipy import stats
    _behaviours = ["running", "chasing", "climbing", "eating", "foraging", "kuks", "quaas",
                   "moans", "tail_flags", "tail_twitches", "approaches", "indifferent",
                   "runs_from"]
    _p = {}
    for _behaviour in _behaviours:
        _rows = squirrels.dropna(subset=["primary_fur_color", _behaviour])
        _table = pd.crosstab(_rows["primary_fur_color"], _rows[_behaviour])
        _p[_behaviour] = stats.chi2_contingency(_table, correction=False).pvalue
    _cutoff = 0.05 / len(_p)
    print(f"Bonferroni cutoff for {len(_p)} tests: {_cutoff:.4f}")
    pd.Series(_p, name="p").sort_values().to_frame().assign(passes=lambda _d: _d["p"] < _cutoff)
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    The Central Park Conservancy is writing a short guide for visitors who want to watch squirrels.
    It would like to tell them what squirrels are likely to be doing, and what makes a difference to
    it.

    > **Use contingency tables and the chi-square test to say what the census shows about what
    > squirrels do, and which facts about a sighting go with differences in their behaviour.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. The table in *Many tables*, to say which facts go with differences in behaviour after the
       correction, and how strong each association is (Cramér's V, or the gap in rates).
    2. One contingency table in detail, for the association you would put in the guide: the rates,
       the expected counts, and which cells make the table differ from independence.
    3. One limitation of your explanation: something these tables cannot tell the Conservancy.

    Then compare your results with your teammates', who started from different facts, and say what
    their results showed that yours did not, and whether that changes your explanation.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each
    prompt, in your own words and with the numbers from your own runs. Each of you should then
    upload your own copy of this notebook to *AE 9* on Canvas, by 23:59 on Thursday.

    | Part of your answer | Points |
    |---|---:|
    | Your explanation: the associations that survive correction and their strength, one table in detail, and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop rather than watching one
    screen, and start from a different fact from your teammates, then compare what you find. Your
    team may agree on an explanation, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholders in Step 1, run
    the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_choose():
    # Step 1: choose a fact and a behaviour, starting from a different fact from your teammates.
    # Replace the placeholders: the fact is one of primary_fur_color, age, shift or location, and
    # the behaviour is one of the thirteen behaviour columns listed at the top.
    answer_factor = "SOME_FACT"
    answer_behaviour = "SOME_BEHAVIOUR"
    return answer_behaviour, answer_factor


@app.cell
def step2_table(answer_behaviour, answer_factor, chi_square, contingency, mo, pd):
    # Step 2: the contingency table, the rates within each row, and the expected counts.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder values.
    mo.stop("SOME_" in answer_factor + answer_behaviour,
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md("Replace the placeholders in Step 1 with column names.").callout(kind="info"))
    answer_table = contingency(answer_factor, answer_behaviour)
    _statistic, _expected = chi_square(answer_table)
    pd.concat({"observed": answer_table,
               "rate": answer_table.div(answer_table.sum(axis=1), axis=0).round(3),
               "expected": _expected.round(1)}, axis=1)
    return (answer_table,)


@app.cell
def step3_test(answer_behaviour, answer_factor, answer_table, chi_square, resampled, stats):
    # Step 3: the chi-square statistic, the resampled p-value and the formula's p-value.
    _statistic, _ = chi_square(answer_table)
    _dealt = resampled(answer_factor, answer_behaviour)
    _dof = (answer_table.shape[0] - 1) * (answer_table.shape[1] - 1)
    {"chi-square": round(_statistic, 2), "degrees of freedom": _dof,
     "p (resampled)": (_dealt >= _statistic).mean(),
     "p (chi-square distribution)": stats.chi2.sf(_statistic, _dof)}
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L11_chi_square.py` to *AE 9* on Canvas by 23:59 on Thursday. We will cross-reference your
    claims about evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_scan(mo):
    mo.md(r"""
    **The facts that go with differences in behaviour after correction, and how strong each
    association is**
    """)
    return


@app.cell
def step4_answer_scan(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_table(mo):
    mo.md(r"""
    **The association you would put in the guide, and which cells of its table make it differ from
    independence**
    """)
    return


@app.cell
def step4_answer_table(mo):
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
