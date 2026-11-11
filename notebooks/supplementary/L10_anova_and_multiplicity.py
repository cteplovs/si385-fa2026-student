# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo>=0.23.3",
#     "matplotlib>=3.9",
#     "numpy>=2.0",
#     "pandas>=3.0.5",
#     "scipy>=1.13",
#     "statsmodels>=0.14",
# ]
# ///

import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def title(mo):
    mo.md(r"""
    # SI 385: Data Exploration

    ## Session 10: Hypothesis testing II, ANOVA and the multiplicity problem

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Monday, October 5, 2026

    **Reading due today:** Bruce et al., *AI-Assisted Statistics for Data Scientists*, ch. 3,
    §§ *Multiple Testing*, *Degrees of Freedom* and *ANOVA*

    ---

    ### Today you will be able to

    - Explain why testing every pair of groups finds differences that are not there, and how a
      correction for multiple comparisons works
    - Run a one-way ANOVA, by permutation and with the F distribution, and read its F-statistic,
      degrees of freedom and p-value
    - Say what a small ANOVA p-value shows and what it does not: that some groups differ, but not
      which ones or by how much
    - Use post-hoc comparisons and the share of variation between groups to say which differences
      matter

    ### Timing

    | Part | Minutes |
    |---|---:|
    | Data | 5 |
    | Many comparisons | 10 |
    | One-way ANOVA | 15 |
    | After the ANOVA: effect size, post-hoc comparisons, the top group | 15 |
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
    from itertools import combinations

    from scipy import stats
    from statsmodels.stats.multitest import multipletests

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

    return combinations, course_csv, mo, multipletests, np, pd, plt, stats


@app.cell(hide_code=True)
def code_on_its_own_note(mo):
    mo.md(r"""
    ### Sections headed *The code on its own*

    Each technique ends with a section headed *The code on its own*. The sliders, dropdowns and
    plots above it call functions written for this notebook, which you will not have when you work
    on your own data. The code in those sections uses only pandas, SciPy and statsmodels, starts
    from a data frame, and does the computation without any controls, so that you can copy it into
    your project or another notebook. Each code cell starts with a comment listing the imports it
    uses, and its variable names start with `_`, which keeps them local to the cell.
    """)
    return


@app.cell(hide_code=True)
def data_intro(mo):
    mo.md(r"""
    ---
    ## Data

    The file holds 2,530 chocolate bars rated by *Flavors of Cacao* between 2006 and 2021, one row
    per bar. Each bar has a rating from 1 (unpleasant) to 4 (outstanding), in steps of a quarter
    point, and the columns below describe where it came from and how it was made.

    | Column | Description |
    |---|---|
    | `company_manufacturer`, `company_location` | Who made the bar, and in which country |
    | `review_date` | The year the bar was rated |
    | `country_of_bean_origin` | Where the cocoa beans were grown; `Blend` means more than one country |
    | `cocoa_percent` | The share of the bar that is cocoa |
    | `ingredients` | How many ingredients, then which: B beans, S sugar, S* another sweetener, C cocoa butter, V vanilla, L lecithin, Sa salt |
    | `rating` | The rating, from 1 to 4 |

    After reading the file, we add three columns for grouping the bars: the cocoa percentage as a
    number and in five bands, and the number of ingredients.
    """)
    return


@app.cell
def load_bars(course_csv, pd):
    bars = course_csv("chocolate.csv")
    bars["cocoa"] = bars["cocoa_percent"].str.rstrip("%").astype(float)
    bars["cocoa_band"] = pd.cut(bars["cocoa"], [0, 65, 69, 72, 79, 100],
                                labels=["65% or less", "66 to 69%", "70 to 72%", "73 to 79%",
                                        "80% or more"]).astype(str)
    # The ingredient count is the digit before the dash; 87 bars do not list their ingredients.
    bars["ingredient_count"] = bars["ingredients"].str.extract(r"^(\d)", expand=False)
    bars[["company_location", "country_of_bean_origin", "cocoa_percent", "cocoa_band",
          "ingredient_count", "rating"]].head()
    return (bars,)


@app.cell(hide_code=True)
def groupings_intro(mo):
    mo.md(r"""
    Today's question is which of these groupings goes with differences in rating. Each grouping
    below keeps only the groups with at least 30 bars, so that every group average is based on
    enough bars to compare, and the bean-origin grouping leaves out `Blend`, which is not a
    country.
    """)
    return


@app.cell
def define_groupings(bars):
    GROUPINGS = {
        "Country of bean origin": "country_of_bean_origin",
        "Cocoa percentage, in bands": "cocoa_band",
        "Maker's country": "company_location",
        "Number of ingredients": "ingredient_count",
    }


    def grouped(column, min_bars=30):
        """The bars in the groups of this column that have at least min_bars bars."""
        _rows = bars.dropna(subset=[column])
        _rows = _rows[_rows[column] != "Blend"]
        _counts = _rows[column].value_counts()
        return _rows[_rows[column].isin(_counts[_counts >= min_bars].index)]

    return GROUPINGS, grouped


@app.cell(hide_code=True)
def rating_plot_intro(mo):
    mo.md(r"""
    Consider the ratings themselves first. Most bars sit between 2.75 and 3.75, so differences
    between groups, if there are any, will be measured in fractions of a point.
    """)
    return


@app.cell
def rating_plot(bars, plt):
    _fig, _ax = plt.subplots(figsize=(7, 3))
    _ax.hist(bars["rating"], bins=[_b / 4 - 0.125 for _b in range(4, 18)], color="#1f4e79",
             edgecolor="white")
    _ax.set_xlabel("Rating")
    _ax.set_ylabel("Bars")
    _ax.set_title("Ratings of 2,530 bars")
    _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def many_comparisons_intro(mo):
    mo.md(r"""
    ---
    ## Many comparisons

    Session 9's t-test compares two groups. There are 21 countries of bean origin with at least 30
    bars, and comparing every pair of them takes 210 t-tests. If none of the origins differed at
    all, each test would still have a 5% chance of a p-value below 0.05, so a scan of 210 tests
    would turn up about ten "significant" pairs by chance alone. The reading calls this the
    multiple testing problem: the more comparisons you make, the more likely it is that some of
    them will be significant by chance.

    To make this concrete, we take the origins with the most bars, shuffle the ratings among those
    bars so that origin can make no difference, run a t-test on every pair, and repeat this 300
    times. Please move the slider and watch how often at least one
    pair comes out "significant" when no real difference exists.
    """)
    return


@app.cell
def comparison_controls(mo):
    # mo.ui.slider is a marimo function that makes a slider; its .value is the chosen setting.
    origin_count = mo.ui.slider(start=2, stop=21, value=5, label="Origins compared",
                                show_value=True)
    # mo.ui.switch is a marimo function that makes an on-off switch.
    use_bonferroni = mo.ui.switch(value=False, label="Bonferroni correction")
    # mo.hstack is a marimo function that puts outputs side by side.
    mo.hstack([origin_count, use_bonferroni], justify="start", gap=3)
    return origin_count, use_bonferroni


@app.cell
def define_pairwise_p(np, pd, stats):
    def pairwise_p(labels, values):
        """Welch t-test p-values for every pair of groups, as a Series indexed by pair."""
        _codes, _names = pd.factorize(labels)
        _k = len(_names)
        _n = np.bincount(_codes, minlength=_k)
        _mean = np.bincount(_codes, weights=values, minlength=_k) / _n
        _sq = np.bincount(_codes, weights=values ** 2, minlength=_k)
        _var = (_sq - _n * _mean ** 2) / (_n - 1)
        _i, _j = np.triu_indices(_k, 1)
        _a, _b = _var[_i] / _n[_i], _var[_j] / _n[_j]
        _t = (_mean[_i] - _mean[_j]) / np.sqrt(_a + _b)
        _df = (_a + _b) ** 2 / (_a ** 2 / (_n[_i] - 1) + _b ** 2 / (_n[_j] - 1))
        _pairs = [f"{_names[_x]} vs {_names[_y]}" for _x, _y in zip(_i, _j)]
        return pd.Series(2 * stats.t.sf(np.abs(_t), _df), index=_pairs)

    return (pairwise_p,)


@app.cell
def many_comparisons_simulation(
    grouped,
    mo,
    np,
    origin_count,
    pairwise_p,
    use_bonferroni,
):
    _rows = grouped("country_of_bean_origin")
    _largest = _rows["country_of_bean_origin"].value_counts().index[:origin_count.value]
    _rows = _rows[_rows["country_of_bean_origin"].isin(_largest)]
    _labels = _rows["country_of_bean_origin"].to_numpy()
    _ratings = _rows["rating"].to_numpy()
    _pairs = origin_count.value * (origin_count.value - 1) // 2
    _cutoff = 0.05 / _pairs if use_bonferroni.value else 0.05

    _rng = np.random.default_rng(385)
    _any = np.mean([(pairwise_p(_labels, _rng.permutation(_ratings)) < _cutoff).any()
                    for _ in range(300)])

    # mo.md is a marimo function that displays Markdown text.
    mo.md(f"""
    With **{origin_count.value}** origins there are **{_pairs}** pairs, and each test counts as
    "significant" below **{_cutoff:.4f}**. In **{_any:.0%}** of the 300 shuffles, at least one pair
    came out significant, although origin can make no difference once the ratings are shuffled.
    """)
    return


@app.cell(hide_code=True)
def bonferroni_reading(mo):
    mo.md(r"""
    The Bonferroni correction divides the cutoff by the number of tests, so that the chance of *any*
    false positive across the whole scan stays near 5%. Please turn it on and move the slider again.
    It keeps that chance near or below 5% however many origins you compare, at the price of a much
    stricter cutoff for each pair: with 21 origins, a pair needs p below 0.00024 to count, so real
    but small differences are harder to detect too.

    A correction is one remedy, and asking a single question about all the groups at once is
    another. That is what an ANOVA does.
    """)
    return


@app.cell(hide_code=True)
def anova_intro(mo):
    mo.md(r"""
    ---
    ## One-way ANOVA

    An analysis of variance replaces the 210 pairwise questions with one: are the group averages
    more spread out than they would be if the grouping made no difference? The reading tests it
    by permutation, in the same way as session 9's shuffle test:

    1. Compute a statistic that measures how far apart the group averages are.
    2. Shuffle the group labels, so that the grouping can make no difference, and compute the
       statistic again. Repeat many times.
    3. The p-value is the share of shuffles whose statistic is at least as large as the real one.

    The usual statistic is the *F-statistic*, the variation between the group averages divided by
    the variation within the groups:

    $$F = \frac{\text{variation between groups} / (k - 1)}{\text{variation within groups} / (n - k)}$$

    where *k* is the number of groups and *n* the number of bars. The two divisors are the
    *degrees of freedom*. With *k* group averages, only *k* − 1 of them are free to differ from the
    overall average once it is fixed, and each group's spread is measured around its own average,
    which uses up one degree of freedom per group. When the grouping makes no difference, F is
    usually near 1. A large F means the averages are further apart than the spread within the
    groups would lead you to expect.

    Because F has a known distribution when the grouping makes no difference (the F distribution,
    with *k* − 1 and *n* − *k* degrees of freedom), software can also compute the p-value from a
    formula, without shuffling. Both p-values are given below.
    """)
    return


@app.cell
def anova_controls(GROUPINGS, mo):
    # mo.ui.dropdown is a marimo function that makes a drop-down menu. Given a dictionary, it shows
    # the keys and its .value is the value of the chosen key.
    grouping_pick = mo.ui.dropdown(options=GROUPINGS, value="Country of bean origin",
                                   label="Group the bars by")
    grouping_pick
    return (grouping_pick,)


@app.cell
def define_anova(np, pd, stats):
    def f_statistic(codes, values, k):
        """The F-statistic for values in k groups, given each value's group code."""
        _n = np.bincount(codes, minlength=k)
        _mean = np.bincount(codes, weights=values, minlength=k) / _n
        _between = (_n * (_mean - values.mean()) ** 2).sum()
        _within = ((values - _mean[codes]) ** 2).sum()
        return (_between / (k - 1)) / (_within / (len(values) - k))


    def anova(rows, column, shuffles=1000, seed=385):
        """One-way ANOVA of rating on column: F, degrees of freedom, both p-values, the share
        of the variation that lies between groups, and the shuffled F values."""
        _codes, _names = pd.factorize(rows[column])
        _ratings = rows["rating"].to_numpy(dtype=float)
        _k, _n = len(_names), len(_ratings)
        _f = f_statistic(_codes, _ratings, _k)
        _rng = np.random.default_rng(seed)
        _shuffled = np.array([f_statistic(_rng.permutation(_codes), _ratings, _k)
                              for _ in range(shuffles)])
        _means = rows.groupby(column)["rating"].transform("mean")
        _between = ((_means - _ratings.mean()) ** 2).sum()
        _total = ((_ratings - _ratings.mean()) ** 2).sum()
        return {
            "groups": _k, "bars": _n, "F": _f, "df between": _k - 1, "df within": _n - _k,
            "p (F distribution)": stats.f.sf(_f, _k - 1, _n - _k),
            "p (shuffles)": (_shuffled >= _f).mean(),
            "share between groups": _between / _total,
            "shuffled F": _shuffled,
        }

    return (anova,)


@app.cell
def anova_result(anova, grouped, grouping_pick):
    grouping_rows = grouped(grouping_pick.value)
    grouping_anova = anova(grouping_rows, grouping_pick.value)
    {_key: round(_value, 4) for _key, _value in grouping_anova.items() if _key != "shuffled F"}
    return grouping_anova, grouping_rows


@app.cell(hide_code=True)
def anova_plots(grouping_anova, grouping_pick, grouping_rows, mo, plt):
    _summary = (grouping_rows.groupby(grouping_pick.value)["rating"]
                .agg(["mean", "sem", "count"]).sort_values("mean"))
    _fig, (_left, _right) = plt.subplots(1, 2, figsize=(11, 0.28 * len(_summary) + 2.5),
                                         gridspec_kw={"width_ratios": [1.2, 1]})
    _left.errorbar(_summary["mean"], range(len(_summary)), xerr=1.96 * _summary["sem"],
                   fmt="o", color="#1f4e79", capsize=3)
    _left.axvline(grouping_rows["rating"].mean(), color="#9ca3af", linestyle="--", linewidth=1)
    _left.set_yticks(range(len(_summary)),
                     [f"{_g} ({_n})" for _g, _n in zip(_summary.index, _summary["count"])])
    _left.set_xlabel("Average rating, with 95% interval")
    _left.set_title("Group averages; the dashed line is all bars")

    _right.hist(grouping_anova["shuffled F"], bins=40, color="#9ca3af")
    _right.axvline(grouping_anova["F"], color="#c2410c", linewidth=2)
    _right.set_xlabel("F")
    _right.set_title("F in 1,000 shuffles; the line is the real F")
    for _ax in (_left, _right):
        _ax.spines[["top", "right"]].set_visible(False)
    _fig.tight_layout()
    _zero = (" A shuffled p-value of 0.000 means only that none of the 1,000 shuffles reached the "
             "real F." if grouping_anova["p (shuffles)"] == 0 else "")

    # mo.vstack is a marimo function that stacks outputs one above the other.
    mo.vstack([_fig, mo.md(f"""
    F is **{grouping_anova['F']:.2f}** on **{grouping_anova['df between']}** and
    **{grouping_anova['df within']:,}** degrees of freedom. The share of shuffles with an F at least
    that large is **{grouping_anova['p (shuffles)']:.3f}**, and the F distribution gives
    **{grouping_anova['p (F distribution)']:.2g}**.{_zero}
    """)])
    return


@app.cell(hide_code=True)
def practice_two_groups_intro(mo):
    mo.md(r"""
    ### Practice: ANOVA with two groups

    With only two groups, an ANOVA and session 9's t-test (the version that assumes equal spread)
    are the same test, and F is the square of t. Please check this yourself. Below, we compare bars
    of 66 to 69% cocoa with bars of 80% or more. Replace `None` with the t-statistic from
    `stats.ttest_ind(lower, higher).statistic`, and compare its square with F.
    """)
    return


@app.cell
def practice_two_groups(bars, stats):
    lower = bars.loc[bars["cocoa_band"] == "66 to 69%", "rating"]
    higher = bars.loc[bars["cocoa_band"] == "80% or more", "rating"]
    print("F from the ANOVA:", round(stats.f_oneway(lower, higher).statistic, 3))
    my_t = None
    my_t
    return


@app.cell(hide_code=True)
def anova_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we keep the groups of one column that have at least 30 bars, run a one-way
    ANOVA with `stats.f_oneway`, which gives F and its p-value from the F distribution, and then
    compute the p-value by shuffling the ratings among the bars 1,000 times, as the reading does.
    To use it on other data, you would change `_column`, the minimum and the column of values.
    """)
    return


@app.cell
def anova_code(bars, np, stats):
    # Uses: import numpy as np
    #       from scipy import stats
    _column = "cocoa_band"
    _counts = bars[_column].value_counts()
    _rows = bars[bars[_column].isin(_counts[_counts >= 30].index)]
    _labels = _rows[_column].to_numpy()
    _values = _rows["rating"].to_numpy(dtype=float)
    _names = sorted(set(_labels))

    _result = stats.f_oneway(*[_values[_labels == _g] for _g in _names])
    print(f"{len(_names)} groups, {len(_values)} rows")
    print(f"F = {_result.statistic:.2f} on {len(_names) - 1} and {len(_values) - len(_names)} "
          f"degrees of freedom, p = {_result.pvalue:.2g}")

    _rng = np.random.default_rng(385)
    _shuffled = [stats.f_oneway(*[_values[_rng.permutation(_labels) == _g] for _g in _names])
                 .statistic for _ in range(1000)]
    print(f"p from 1,000 shuffles: {np.mean(np.array(_shuffled) >= _result.statistic):.3f}")
    return


@app.cell(hide_code=True)
def after_anova_intro(mo):
    mo.md(r"""
    ---
    ## After the ANOVA

    A small ANOVA p-value means that the group averages are further apart than shuffling makes them.
    It does not say which groups differ, or whether the differences are large enough to matter.
    Three further steps answer those questions.

    ### The share of variation between groups

    With 2,530 bars, a difference of a few hundredths of a point can give a very small p-value, so
    the p-value is a poor guide to size. The *share of variation between groups* (often written η²,
    "eta squared") is the variation between the group averages divided by the total variation in
    the ratings. It runs from 0, where every group has the same average, to 1, where every bar in a
    group has the same rating. The table below gives it for all four groupings, alongside F and the
    p-value.
    """)
    return


@app.cell
def compare_groupings(GROUPINGS, anova, grouped, pd):
    _rows = {}
    for _label, _column in GROUPINGS.items():
        _result = anova(grouped(_column), _column, shuffles=200)
        _rows[_label] = {
            "Groups": _result["groups"],
            "Bars": _result["bars"],
            "F": round(_result["F"], 2),
            "p (F distribution)": f"{_result['p (F distribution)']:.2g}",
            "Share between groups": f"{_result['share between groups']:.1%}",
        }
    pd.DataFrame(_rows).T
    return


@app.cell(hide_code=True)
def share_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we compute the share of the variation between groups for one column: each
    bar's group average is compared with the overall average, and the sum of those squared
    differences is divided by the total variation in the ratings.
    """)
    return


@app.cell
def share_code(bars):
    _column = "cocoa_band"
    _counts = bars[_column].value_counts()
    _rows = bars[bars[_column].isin(_counts[_counts >= 30].index)]
    _overall = _rows["rating"].mean()
    _group_means = _rows.groupby(_column)["rating"].transform("mean")
    _between = ((_group_means - _overall) ** 2).sum()
    _total = ((_rows["rating"] - _overall) ** 2).sum()
    print(f"share of the variation between groups: {_between / _total:.1%}")
    return


@app.cell(hide_code=True)
def posthoc_intro(mo):
    mo.md(r"""
    ### Post-hoc comparisons

    Once the ANOVA shows that some groups differ, a *post-hoc* ("after this") comparison tests each
    pair, with a correction for the number of pairs. The Bonferroni correction from the first section
    is the simplest. The Holm correction is a little less strict and equally safe: it sorts the
    p-values from smallest to largest, compares the smallest with 0.05/*m*, the next with
    0.05/(*m* − 1), and so on, and stops at the first one that fails.

    The table lists the pairs for the grouping you chose above, with the difference between the two
    averages, the uncorrected p-value and the corrected one. Please choose a correction and see how
    many pairs survive it.
    """)
    return


@app.cell
def posthoc_controls(mo):
    correction_pick = mo.ui.dropdown(
        options={"None": None, "Bonferroni": "bonferroni", "Holm": "holm"},
        value="Holm", label="Correction")
    correction_pick
    return (correction_pick,)


@app.cell
def define_posthoc(multipletests, np, pairwise_p, pd):
    def posthoc(rows, column, correction):
        """Every pair of groups: the difference in averages, and the raw and corrected p."""
        _raw = pairwise_p(rows[column].to_numpy(), rows["rating"].to_numpy(dtype=float))
        _means = rows.groupby(column)["rating"].mean()
        _gaps = [_means[_a] - _means[_b] for _a, _b in (p.split(" vs ") for p in _raw.index)]
        _adjusted = (_raw.to_numpy() if correction is None
                     else multipletests(_raw.to_numpy(), method=correction)[1])
        return (pd.DataFrame({"Difference": np.round(_gaps, 3), "p": _raw.round(4),
                              "Corrected p": np.round(_adjusted, 4)}, index=_raw.index)
                .sort_values("p"))

    return (posthoc,)


@app.cell
def posthoc_table(correction_pick, grouping_pick, grouping_rows, mo, posthoc):
    _table = posthoc(grouping_rows, grouping_pick.value, correction_pick.value)
    _survive = int((_table["Corrected p"] < 0.05).sum())
    mo.vstack([
        mo.md(f"**{_survive}** of **{len(_table)}** pairs have a corrected p-value below 0.05."),
        _table.head(15),
    ])
    return


@app.cell(hide_code=True)
def posthoc_code_intro(mo):
    mo.md(r"""
    ### The code on its own

    In the cell below, we run a Welch t-test on every pair of groups, which does not assume that the
    groups have the same spread, and then correct the p-values for the number of pairs with
    `multipletests`. Changing `"holm"` to `"bonferroni"` gives the stricter correction.
    """)
    return


@app.cell
def posthoc_code(bars, combinations, multipletests, pd, stats):
    # Uses: from itertools import combinations
    #       import pandas as pd
    #       from scipy import stats
    #       from statsmodels.stats.multitest import multipletests
    _column = "cocoa_band"
    _counts = bars[_column].value_counts()
    _rows = bars[bars[_column].isin(_counts[_counts >= 30].index)]
    _pairs = []
    for _a, _b in combinations(sorted(_rows[_column].unique()), 2):
        _x = _rows.loc[_rows[_column] == _a, "rating"]
        _y = _rows.loc[_rows[_column] == _b, "rating"]
        _pairs.append({"pair": f"{_a} vs {_b}", "difference": _x.mean() - _y.mean(),
                       "p": stats.ttest_ind(_x, _y, equal_var=False).pvalue})
    _table = pd.DataFrame(_pairs).set_index("pair")
    _table["corrected p"] = multipletests(_table["p"], method="holm")[1]
    _table.sort_values("p").round(4)
    return


@app.cell(hide_code=True)
def winner_intro(mo):
    mo.md(r"""
    ### The top group, measured again

    The group with the highest average is there partly because its bars are good and partly because,
    among many averages, some will be high by chance, and the top spot is where chance high scores
    collect. Its lead is therefore likely to shrink when it is measured again on new bars, and it
    shrinks most when the differences between the groups are mostly chance.

    For the grouping you chose above, we find the group with the highest average among the bars
    reviewed before the year you choose (counting only groups with at least 10 bars in that period),
    and then measure the same group's lead among the bars reviewed from that year on. Please move the slider, and then try the cocoa bands as well as the origins.
    """)
    return


@app.cell
def winner_controls(mo):
    split_year = mo.ui.slider(start=2010, stop=2018, step=2, value=2014,
                              label="Measure again from", show_value=True)
    split_year
    return (split_year,)


@app.cell
def winner_demo(grouping_pick, grouping_rows, mo, split_year):
    _column = grouping_pick.value
    _before = grouping_rows[grouping_rows["review_date"] < split_year.value]
    _after = grouping_rows[grouping_rows["review_date"] >= split_year.value]
    _means = _before.groupby(_column)["rating"].agg(["mean", "count"])
    _top = _means[_means["count"] >= 10]["mean"].idxmax()
    _lead_before = _means.loc[_top, "mean"] - _before["rating"].mean()
    _lead_after = (_after.loc[_after[_column] == _top, "rating"].mean()
                   - _after["rating"].mean())
    mo.md(f"""
    Among the **{len(_before):,}** bars reviewed before {split_year.value}, the top group is
    **{_top}**, **{_lead_before:+.3f}** points from the average. Among the **{len(_after):,}** bars
    reviewed from {split_year.value} on, the same group is **{_lead_after:+.3f}** points from the
    average.
    """)
    return


@app.cell(hide_code=True)
def todays_question(mo):
    mo.md(r"""
    ---
    ## Today's question

    A chocolate shop near campus wants to know what to look for when it stocks bars. The owner can
    sort the shelves by where the beans were grown, by the cocoa percentage, by the maker's country,
    or by the number of ingredients.

    > **Use ANOVA and post-hoc comparisons to say what makes one bar rate higher than another, and
    > how much of the difference in ratings it explains.**

    You need nothing beyond this notebook. A good answer uses three things from it:

    1. The table in *The share of variation between groups*, to say which groupings go with
       differences in rating (F and its p-value) and how much of the variation each explains (the
       share between groups).
    2. The post-hoc comparisons for the grouping you would recommend, with a correction, to say
       which particular groups differ and by how much.
    3. One limitation of your explanation: something an ANOVA of these data cannot tell the owner.

    Then compare your results with your teammates', who started from different groupings, and say
    what their results showed that yours did not, and whether that changes your explanation.

    You will write your answer in Step 4 at the end of this notebook, a few sentences under each
    prompt, in your own words and with the numbers from your own runs. Each of you should then
    upload your own copy of this notebook to *AE 8* on Canvas, by 23:59 on Tuesday.

    | Part of your answer | Points |
    |---|---:|
    | Your explanation: the groupings, F and the share between groups, the post-hoc comparisons, and one limitation | 4 |
    | Comparing with your team: what your teammates' results added | 2 |

    ## Working as a team

    Your team's time is for talking through the problem, trying out ideas, and helping each other
    with the code. Each of you should run the code on your own laptop rather than watching one
    screen, and start from a different grouping from your teammates, then compare what you find.
    Your team may agree on an explanation, but the answer you submit is your own.

    The cells below are a scaffold for your answer. Please replace the placeholder in Step 1, run
    the cells, and write your answer in Step 4.
    """)
    return


@app.cell
def step1_choose_grouping():
    # Step 1: choose a grouping to start with, different from the one your teammates choose.
    # Replace the placeholder with one of the column names in GROUPINGS: country_of_bean_origin,
    # cocoa_band, company_location or ingredient_count. You may also change the minimum number of
    # bars a group needs.
    answer_column = "SOME_COLUMN"
    answer_min_bars = 30
    return answer_column, answer_min_bars


@app.cell
def step2_anova(anova, answer_column, answer_min_bars, grouped, mo):
    # Step 2: run the ANOVA for your grouping. Compare it with the table in the section on the share
    # of variation between groups, then try another grouping in Step 1.
    # mo.stop (a marimo function) stops this cell, and the cells that use its results,
    # until you have replaced the placeholder value.
    mo.stop(answer_column == "SOME_COLUMN",
            # .callout is a marimo method that puts a message in a coloured box.
            mo.md("Replace the placeholder in Step 1 with a column name.").callout(kind="info"))
    answer_rows = grouped(answer_column, answer_min_bars)
    {_key: round(_value, 4)
     for _key, _value in anova(answer_rows, answer_column).items() if _key != "shuffled F"}
    return (answer_rows,)


@app.cell
def step3_posthoc(answer_column, answer_rows, posthoc):
    # Step 3: compare every pair of groups with the Holm correction. Change "holm" to
    # "bonferroni" or None to see what the correction changes.
    posthoc(answer_rows, answer_column, "holm")
    return


@app.cell(hide_code=True)
def step4_intro(mo):
    mo.md(r"""
    ### Step 4: your answer

    Please write your answer in the cell under each prompt, replacing the placeholder text, in your
    own words and with the numbers from your own runs. Then save the notebook and upload your copy of
    `L10_anova_and_multiplicity.py` to *AE 8* on Canvas by 23:59 on Tuesday. We will
    cross-reference your claims about evidence from your teammates against the work they submit.
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_groupings(mo):
    mo.md(r"""
    **The groupings that go with differences in rating, and how much of the variation each explains**
    """)
    return


@app.cell
def step4_answer_groupings(mo):
    mo.md(r"""
    *Replace this line with your answer.*
    """)
    return


@app.cell(hide_code=True)
def step4_prompt_pairs(mo):
    mo.md(r"""
    **The particular groups that differ after correction, and by how much**
    """)
    return


@app.cell
def step4_answer_pairs(mo):
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
