# SI 385: Data Exploration

## Application exercise 5, pre-read: what does this degree pay?

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 7, Wednesday September 23, 2026*

---

This document is half of an application exercise: it sets out the data and the question,
while the answer options are held back until Wednesday, when you meet them for the first
time in the room. Nothing in it is submitted or graded, and it is posted several days ahead so that you can
decide for yourself how much time it gets.

Session 7 is the synthesis session, which means there is no assigned reading and no
readiness test, and the full period belongs to the exercise. What you bring to it is the
four weeks behind you.

## The data

The file is one you have not worked with before. The **College Scorecard** is published by
the United States Department of Education and exists for a single purpose, which is to tell
prospective students what particular degrees at particular institutions are worth. What
follows is the release of June 2026, cut down to bachelor's degrees awarded by institutions
in the United States.

```python
import pandas as pd

degrees = pd.read_parquet("data/college_scorecard_bachelors.parquet")
degrees.head()
```

There are 70,557 rows, each one an institution paired with a field of study, drawn from
2,537 institutions and 388 fields.

| Column | What it holds |
|---|---|
| `institution` | the college |
| `field` | the field of study, e.g. `Computer Science.` |
| `control` | public, private nonprofit, or private for-profit |
| `n_awards` | how many degrees that program awarded |
| `earn_median_1yr` | median earnings one year after graduating |
| `earn_median_4yr` | the same, four years out |
| `debt_median` | median debt at graduation |

Seventeen further columns sit behind those. Nine of the columns carrying money come in
pairs, and the second member of each pair records why the first is or is not there:

```python
degrees[["field", "earn_median_1yr", "earn_median_1yr_status"]].head()
```

## What is not in the file

Most of this dataset is empty. Of the 70,557 bachelor's programs it covers, only 25,737 —
a little over a third — report any earnings figure at all, which leaves 63.5% of the file
with nothing in the column that the whole exercise of publishing it was meant to fill.

The empty cells are not empty for the same reason, and that is why each column carrying
money is shadowed by a `_status` column recording which kind of absence you are looking at:

| `earn_median_1yr_status` | Programs | What it means |
|---|---:|---|
| `reported` | 25,737 | there is a number |
| `suppressed` | 41,387 | the Department holds the number and declines to publish it |
| `not reported` | 3,433 | nothing was collected |

Suppression is a privacy measure rather than an oversight. If the Department were to publish
the median earnings of a program that graduated three people, it would in effect be
publishing something very close to three named individuals' incomes, so cells below a
certain size are withheld. The consequence is visible in the file: where earnings are
reported the median graduating class is 37 people, and where they are absent it is four.

Wednesday's question turns on one particular consequence of that.

| Field | Programs | How many report earnings |
|---|---:|---:|
| **Data Science** | **144** | **0** |
| **Data Analytics** | **135** | **0** |
| Computer Science | 782 | 355 |

Every bachelor's program in data science that the file covers has been suppressed, as has
every program in data analytics, and the median one among them graduated two people. The
federal dataset built to establish what degrees are worth turns out to have nothing whatever
to say about the degree you are currently enrolled in.

## The question

Someone asks you a direct question — a younger sibling deciding where to apply, or a
student at a college fair, or some earlier version of yourself.

> **What does a data science degree pay?**

You have in front of you the file that exists to answer precisely that.

> **What do you tell them?**

On Wednesday your team will settle on one answer from a small fixed set, write a short
justification for it, and reveal at the same moment as every other team in the room. The
options differ from one another in what each is prepared to accept as a substitute for a
number that does not exist.

## Four analysts

Wednesday divides your team four ways, giving each member one lens on the same file, and the
four lenses are the four sessions you have just worked through.

| Analyst | Looks at |
|---|---|
| 1 | The distribution — centre, spread, shape |
| 2 | The plot — what the picture shows that the summary does not |
| 3 | What is missing, and whether the missingness is itself a finding |
| 4 | Conditioning — whether the story survives a third variable |

These four accounts are unlikely to agree with one another, and reconciling them is where
most of the period goes. The exercise is designed around a team of four and remains
workable with fewer, in which case you name the lens you did not get to and say what you
would have wanted from it. That belongs in the submission, and it is read as evidence that
you know the shape of your own argument.

There is no need to settle who takes which lens before Wednesday, since the notebook offers
a dropdown and the first eight minutes of the period are set aside for exactly that.

## If you want to spend time on this beforehand

What follows is neither a checklist nor a requirement, and none of it is inspected.

You could look at what else in the file has been suppressed, since there are 388 fields
and the pattern across them is not arbitrary, or work out what a suppressed cell actually
entitles you to say about the people counted in it, given that the file establishes only
that a program is small while remaining silent on what its graduates go on to earn. It is
also worth locating the fields nearest to data science that do report a figure, to see how
far apart from one another they are, and thinking about what the person asking you the
question actually needs from you.

## Wednesday asks for three to five lines of code

As in AE 4, the justification your team submits has to cite a number that the notebook does
not show you, together with the lines that produced it, and it has to give counts alongside
medians. A single `groupby` or `pivot_table` will carry most of the work.

It does not matter which member of the team writes those lines, or whether you have help in
writing them, provided that they run against the file and produce the table you go on to
cite. The notebook has an empty cell waiting for them.

One piece of housekeeping, in advance. When you paste code into the Canvas text box,
please select the pasted lines, open the **Format** menu, and choose **Code**; the text will turn monospaced and your indentation will survive. Left as ordinary
text, Canvas collapses the leading spaces that tell Python what belongs inside a block and
converts straight quotes into curly ones, so that what reaches the marker is something
nobody can run.

If anything here fails to run on your machine, please ask on Slack, which reaches all three
of us. GSI office hours are Thursday 2–3 with Shan and Sunday 7–8 with Zach.

## What happens on Wednesday

| Time | What |
|---|---|
| 0:00–0:08 | The question, and your team decides who takes which lens |
| 0:08–0:20 | Silent and individual. You work your lens on your own |
| 0:20–0:45 | The four accounts go on the table, and your team argues its way to one answer |
| 0:45–1:05 | Every team reveals at once, and several are asked to defend |
| 1:05–1:10 | Consolidation |
| 1:10–1:20 | **DoU 1 is assigned** |

Only the justification is graded, not the choice itself.

The justification is written by the team rather than by any one of you, and it asks for
three things: what each of the four lenses found, which of those accounts most contradicted
the others and what you decided to do about it, and a number drawn from the file
that the notebook does not display, accompanied by the code that produced it. Working a
single lens applies to the silent twelve minutes only; once your team convenes, the whole
file is open to all of you.

The last ten minutes of the period are given over to the first Demonstration of
Understanding, which is an individual piece of work due on Monday October 5. The hour that
precedes it in the room is deliberate preparation for it, so please stay for those ten
minutes.

## The other half, and where to find it

**The notebook** is posted on Tuesday evening, somewhat earlier than in previous weeks.
Please run `uv run update.py` from inside the course folder, which will pull
`notebooks/lectures/L07_synthesis.py` down to you. It holds the four analyst views, an empty
cell for your own lines of code, and the answer options.

**The Canvas assignment**, *AE 5: What does this degree pay?*, opens when class does. One
person submits on behalf of the whole team and the mark reaches everyone. Sli.do carries a
single question this session, which is the reveal: one click per team, and the histogram is
what the room looks at before anybody speaks. It carries no marks, and the Canvas
submission is the one that counts.
