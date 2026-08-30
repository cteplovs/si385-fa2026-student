# SI 385 FA 2026 --- Schedule of Topics and Readings

Mondays & Wednesdays, 08:30–09:50. **27 meetings: first Mon Aug 31, last Wed Dec 9.**

**Calendar notes.** No class Mon Sep 7 (Labour Day). No class Mon Oct 19 / Tue Oct 20
(Fall Study Break --- only the Monday affects us). No class Wed Nov 25 (Thanksgiving
recess).

**Reading the columns.** *RAP* = there is an individual iRAT on the assigned reading,
**taken on Canvas**, opening 09:50 two days ahead (Friday for a Monday class, Monday for
a Wednesday one) and **due 20:59 the night before** --- Sunday or Tuesday. Each AE's
dataset and question are posted separately, at least two days before the session and
usually earlier. The session itself opens with clarification built from the iRAT results. There is no team RAT.
*AE* = application exercise number. Sessions marked **Synthesis** have no new reading and
no RAT; the whole period is one extended team problem.

---

## Module 0 --- Launch and bridge

| # | Date | Topic | Reading (before class) | RAP | Due |
|---|---|---|---|---|---|
| 1 | Mon Aug 31 | Course launch. What exploratory data analysis actually is. TBL orientation, ungraded diagnostic | None | --- | --- |
| 2 | Wed Sep 02 | Tooling: marimo and reactive notebooks, molab as the no-install fallback. **Self-selected teams formed this session.** | marimo *Getting Started*; *R for Data Science* 2e §10.1–10.2 | Practice RAT (ungraded) | --- |

> Session 2 is tooling only: marimo and molab. By the end of that class everyone should have a working
> environment or a molab tab. Teams also form this session --- self-selected groups of 4,
> with a suggestion to mix SI 345 sections.


## Module 1 --- Description and sensemaking

> **Bruce et al. ch. 1 is split across four sessions.** It is a long chapter and you read
> a part of it at a time, following the chapter's own structure. When a session assigns
> part of ch. 1, that part is all you are expected to have read.
>
> | Sections | Session |
> |---|---|
> | Elements of Structured Data → Exploring the Data Distribution | 3 (centre, spread, shape) |
> | Exploring Two or More Variables | 6 (multivariate exploration) |
> | Exploring Binary and Categorical Data | 11 (categorical data) |
> | Correlation | 12 (correlation and OLS) |
>
> Sections 10 and 12 --- *Interpreting Visualization Results with AI* and *Exploration
> with AI* --- are not assigned.


| # | Date | Topic | Reading (before class) | RAP | Due |
|---|---|---|---|---|---|
| 3 | Wed Sep 09 | Describing a distribution: centre, spread, shape, and what each licenses you to say | Bruce et al. ch. 1, **through *Exploring the Data Distribution*** (§§1–6) | RAT 1 · AE 1 | --- |
| 4 | Mon Sep 14 | Anscombe's quartet and the limits of summary statistics. Visual reasoning as evidence | Tufte (excerpt) | RAT 2 · AE 2 | --- |
| 5 | Wed Sep 16 | Missingness, outliers, and data quality as an analytical judgement rather than a cleaning step | McKinney ch. 7 (review); Segel & Heer | RAT 3 · AE 3 | --- |
| 6 | Mon Sep 21 | Multivariate exploration: conditioning, faceting, and finding structure without a model | Bruce et al. ch. 1 §*Exploring Two or More Variables* | RAT 4 · AE 4 | --- |
| 7 | Wed Sep 23 | **Synthesis** --- full-period team exploration of an unfamiliar dataset | None | AE 5 | **DoU 1 assigned** |

## Module 2 --- From exploration to inference

| # | Date | Topic | Reading (before class) | RAP | Due |
|---|---|---|---|---|---|
| 8 | Mon Sep 28 | Sampling, uncertainty, and the exploratory/confirmatory boundary. Why the order you look matters | *Statistics is Easy* ch. 1 | RAT 5 · AE 6 | --- |
| 9 | Wed Sep 30 | Hypothesis testing I: the t-test, and what a p-value does and does not tell you | *Statistics is Easy* ch. 3; Grus ch. 7 | RAT 6 · AE 7 | --- |
| 10 | Mon Oct 05 | Hypothesis testing II: ANOVA, post-hoc comparisons, and the multiplicity problem | Grus ch. 7 (cont.) | RAT 7 · AE 8 | **DoU 1 due** |
| 11 | Wed Oct 07 | Categorical data: contingency tables, crosstabs, chi-square | Bruce et al. ch. 1 §*Exploring Binary and Categorical Data* | RAT 8 · AE 9 | --- |
| 12 | Mon Oct 12 | Correlation and ordinary least squares regression | Bruce et al. ch. 1 §*Correlation*; Bruce et al. ch. 4 (simple and multiple linear regression) | RAT 9 · AE 10 | --- |
| 13 | Wed Oct 14 | Regression diagnostics: residuals, leverage, influence, and model criticism | Géron ch. 2 (§ evaluation) | RAT 10 · AE 11 | **Project proposal** (ungraded) |
| --- | Mon Oct 19 | *No class --- Fall Study Break* | | | |
| 14 | Wed Oct 21 | **Synthesis** --- competing analyses of one contested dataset | None | AE 12 | **DoU 2 assigned** |

## Module 3 --- Models as instruments of exploration

| # | Date | Topic | Reading (before class) | RAP | Due |
|---|---|---|---|---|---|
| 15 | Mon Oct 26 | Framing a machine learning problem. Train/test discipline and how leakage happens | Géron ch. 1 | RAT 11 · AE 13 | --- |
| 16 | Wed Oct 28 | Pipelines and feature engineering: making a workflow you can trust twice | Géron ch. 2 | RAT 12 · AE 14 | --- |
| 17 | Mon Nov 02 | Dimension reduction I: principal components, and what a component means | Géron ch. 8 | RAT 13 · AE 15 | **DoU 2 due** |
| 18 | Wed Nov 04 | Dimension reduction II: t-SNE, UMAP, and how embedding plots mislead | Géron ch. 8 (cont.) | RAT 14 · AE 16 | --- |
| 19 | Mon Nov 09 | Clustering I: k-means, distance, and scaling | Grus ch. 19; Géron ch. 9 | RAT 15 · AE 17 | --- |
| 20 | Wed Nov 11 | Clustering II: hierarchical and density methods. How many clusters, and does this clustering mean anything? | Géron ch. 9 (cont.) | RAT 16 · AE 18 | --- |
| 21 | Mon Nov 16 | Classification I: logistic regression, trees, forests, and choosing a model class | Grus ch. 13; Géron ch. 3 | RAT 17 · AE 19 | --- |
| 22 | Wed Nov 18 | Classification II: evaluation beyond accuracy --- imbalance, thresholds, and the cost of an error | Géron ch. 3 (cont.) | RAT 18 · AE 20 | **DoU 3 assigned** |
| 23 | Mon Nov 23 | **Synthesis** --- model bake-off with a defended recommendation | None | AE 21 | --- |
| --- | Wed Nov 25 | *No class --- Thanksgiving recess* | | | |

## Module 4 --- Text and generative models

| # | Date | Topic | Reading (before class) | RAP | Due |
|---|---|---|---|---|---|
| 24 | Mon Nov 30 | Text as data beyond SI 345: spaCy pipelines, word embeddings, semantic scales | spaCy 101 | RAT 19 · AE 22 | **DoU 3 due** |
| 25 | Wed Dec 02 | Large language models as analytical instruments: where they help, where they fabricate, and how to verify | Bruce et al. ch. 10–11 | RAT 20 · AE 23 | --- |

## Closing sessions

| # | Date | Topic | Reading (before class) | RAP | Due |
|---|---|---|---|---|---|
| 26 | Mon Dec 07 | Open lab and project clinic --- bring your notebook, get feedback | --- | --- | --- |
| 27 | Wed Dec 09 | Course wrap-up: what you can do now, what comes next in SI 485 | --- | --- | **Final report** (Dec 11) |

---

## Totals for grading

- **RATs:** 20 graded (sessions 3–22, 24–25), due on Canvas the night before each;
  plus one ungraded practice due before session 2
- **Application exercises:** 23 (AE 1–23), scored on completion only
- **DoUs:** 3, each notebook (40) + decision memo, 400 words (80)
- **Project proposal:** required, ungraded
- **Peer evaluations:** 2 (after session 14, after session 25)

Grading uses *best-of* counts below these totals so that absence, illness, and one
bad morning are absorbed without an appeals process. See the syllabus.


## Readings

Available through the U-M O'Reilly portal:
<https://www.lib.umich.edu/announcements/oreilly-safari-books-online>

- Peter Bruce, Andrew Bruce & Peter Gedeck, *AI-Assisted Statistics for Data
  Scientists*, 3rd ed. --- cited as **Bruce et al.** Successor to *Practical Statistics
  for Data Scientists*; ch. 1 is still "Exploratory Data Analysis"
- Aurélien Géron, *Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow*
- Joel Grus, *Data Science from Scratch*, 2nd ed.
- Jake VanderPlas, *Python Data Science Handbook*
- Wes McKinney, *Python for Data Analysis* --- review only; SI 345 is the primary venue
- Dennis Shasha & Manda Wilson, *Statistics is Easy*
- Hadley Wickham, Mine Çetinkaya-Rundel & Garrett Grolemund, *R for Data Science*,
  2nd ed. --- §10.1–10.2 only, for the framing. Also free at <https://r4ds.hadley.nz>


**On the R4DS excerpt.** Session 2's reading is two sections of an R textbook, assigned
to a Python course on purpose. §10.1–10.2 are prose --- the R code starts at §10.3, which
is not assigned, and **you do not need to install R.** It is the best short statement in
print of what EDA is for, and EDA is not a feature of any one language or library.

