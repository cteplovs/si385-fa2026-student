# SI 385: Data Exploration

## Application exercise 14, pre-read: house values in California districts

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 16, Wednesday October 28, 2026. Revised Tuesday October 27.*

---

This pre-read replaces the one posted on Monday, which asked about the Economy columns of the
Portalegre student data. Session 16 now uses a different dataset and a different kind of exercise.
The earlier version is kept at the end of this document for reference.

## Data

The data are the ones Géron uses in chapter 2: the 1990 United States census for California,
summarised for each of 20,640 districts. Each row describes a district rather than a house, with
its location, the median age of its houses, its total rooms, bedrooms, population and households,
its median household income, how near it is to the ocean, and its median house value.

## Question

> **Build the pipeline, then use it to say what sets a district's house value, and how much of it
> you can explain.**

There are no answer options this time. In class, the session 16 notebook will take you through
scikit-learn's pipelines, train-test splits, cross-validation and the coefficients of a linear
regression, and then give you a scaffold for your own answer.

## Working and submitting

Your team may work on the question together in class, and each of you should start from different
columns from your teammates and then compare what you find. Each of you should then write your own
answer in Step 4 of the notebook and upload your copy of `L16_pipelines.py` to *AE 14* on Canvas by
23:59 on Wednesday. The answer is worth 6 points: 4 for your explanation, and 2 for comparing your
results with your teammates'.

## Optional preparation

If you have time before Wednesday, the following will help.

- Please read Wednesday's reading, Géron ch. 2 or the two scikit-learn pages named in the RAT 12
  announcement. Géron's chapter works through these same data.
- Consider which of the columns you would expect to matter most for a district's house value, and
  why.

## Before class

Please run `uv run update.py` in your course folder before Wednesday, which brings in the session
16 notebook and the housing data.

*Data: Géron, A. (2022). Hands-On Machine Learning with Scikit-Learn, Keras and TensorFlow, 3rd
ed., ch. 2, from the 1990 United States census for California (Pace, R. K. and Barry, R. (1997).
Sparse spatial autoregressions. Statistics and Probability Letters 33, 291–297).*

---

## The earlier version, replaced on October 27

*The text below is the pre-read posted on Monday, October 26, kept for reference. It no longer
describes Wednesday's exercise.*

This is half of an application exercise: it gives you the question and withholds the answer
options, which you will see for the first time in the room, and nothing here is submitted or graded.

### Data

The data are the same 4,424 Portalegre students as in session 15, and your team keeps the lens it
held then. On Wednesday every team will use only its day-one columns: the group of columns from
Background, Family, Admission or Economy that the institution knows at enrolment. Session 15 already
ruled on the Money and Semester columns, so they are set aside.

The Economy columns are Portugal's national unemployment rate, inflation rate and GDP, for the
year each student enrolled. About a quarter of the teams hold them already, and on Wednesday they
will open to every team, so that every team can work the same question. They will arrive with the
session 16 notebook, as a small file matched to your lens by the `student` number.

Every team will receive the same question, the same three Economy columns, and the same summary
table of them. What your team compares depends on its day-one group, as the table below shows.

| Your team's day-one group | What your team will compare |
|---|---|
| Background, Family or Admission | Your group alone, against your group with the Economy columns added |
| Economy | The Economy columns alone, since they are your group |

Teams whose day-one group is Economy have one comparison fewer than the others, but they hold the
evidence the question is about, and the summary table is the same for everyone.

Each comparison will be scored two ways, using two different ways of splitting the students into
training and test sets, which the notebook will explain.

### Scenario and question

The tutoring team's list is still made once, on day one. On their own, the Economy columns score
an AUC of 0.53 for dropout.

> **What are the Economy columns telling the model, and should the tutoring team's list use them?**

On Wednesday your team will choose one answer from a small fixed set, write a short justification,
and reveal at the same moment as every other team.

### Optional preparation

If you have time before Wednesday, the following will help.

- Please read Wednesday's reading, Géron ch. 2 or the two scikit-learn pages named in the RAT 12
  announcement. The notebook builds a pipeline of the kind both describe.
- Consider what the Economy columns describe, and which students would share the same values.

### Schedule for Wednesday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual. You will take a position and write it down |
| 0:23–0:50 | Your team will argue, converge on one option, and post its note |
| 0:50–1:15 | Every team will reveal at once, and several will be asked to defend |

### Before class

Please run `uv run update.py` in your course folder before Wednesday, which brings in the session
16 notebook and the Economy file. Your team will also need its lens file from its team page on
casefile, as on Monday.

### Submitting

As on Monday, your team will post one note to casefile, and one person will post for the whole
team. The board will stay hidden until the reveal. After the reveal, one team will be drawn at
random to write the session's summary note, which will be that team's work for the session.

*Data: Realinho, V., Vieira Martins, M., Machado, J. and Baptista, L. (2022). Predict students'
dropout and academic success. UCI Machine Learning Repository, CC BY 4.0.*
