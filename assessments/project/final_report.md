# SI 385: Team Project Final Report

*Dr. Chris Teplovs, School of Information, University of Michigan*

**Due Friday December 11, 2026 at 23:59. Team work. 180 points.**

---

## Overview

The final report completes the investigation your team proposed in October. Your team should
submit a single marimo notebook in which you work from the raw data to a written answer to your
question, with the report written into the notebook as markdown cells rather than in a separate
document.

The notebook should run top to bottom from a clean kernel, and the report should be about 1,500
words, divided among the sections below.

| Section | Roughly | Points |
|---|---:|---:|
| 1. Question and context | 150 words | 20 |
| 2. Exploratory data analysis | 400 words | 45 |
| 3. Analysis | 450 words | 55 |
| 4. Limitations | 250 words | 30 |
| 5. One decision defended | 250 words | 30 |

The word counts are a guide to where the effort belongs rather than a limit, and code cells do not
count towards them.

## Sections

### 1. Question and context

State the question your team set out to answer and say who would care about the answer. A good
question names a population, a measurement and a comparison or relationship, and it can come out
more than one way. If your question changed after the proposal, please say how and why; a question
that narrowed once you saw the data is usually a better one.

We will give most marks to a question the data can answer, scoped to what your team could do in
six weeks.

### 2. Exploratory data analysis

Describe the data honestly before you model it. Show the distributions of the variables your
question depends on, how much is missing and whether the missingness looks random, and the outliers,
with a judgement about whether each is real or an artifact. Please say what surprised you, because
that is usually where the analysis should have changed course, and say whether it did.

We will give most marks to EDA whose findings change what you do in the analysis, and few to a plot
of every column with nothing said about any of them. This is not the place for a *tour-de-force*
demonstration of your visualization abilities.

### 3. Analysis

Carry out at least one inferential or model-based analysis, such as a hypothesis test, a
regression, a clustering or a classifier. The method should be the one your question and your data
can support, which is not always the most advanced one the course has covered. Check its
assumptions, report its results in units a reader can use, and say what the result means for your
question.

We will give most marks to a method that suits the question, applied correctly, with its output
interpreted rather than pasted.

### 4. Limitations

Say what your analysis cannot support and why: what the data do not cover, which assumptions held
only approximately or not at all, and what a sceptical reader would want to see before believing
your conclusion, and then say what you would do with more time or better data.

We will give most marks to limitations specific to your analysis, and few to ones that could be
written about anybody's project, such as "the sample may not be representative", unless you say how
it is unrepresentative and how that would affect your result.

### 5. One decision defended

Choose the single analytical decision your team would defend, and the alternative you rejected.
Please write this section in the same way as a DoU memo: name the cell where you made the choice,
quote the numbers your notebook produced under both versions, and argue against the alternative in
its strongest form.

We will give most marks to a decision that changed the result, defended with numbers from your own
notebook.

## Using an agent

You may use one, as everywhere in this course, and you should say so in your AI disclosure. This is
more of a record for you and any future use of the material in other contexts. I am completely fine
with the use of AI; other readers of your work may not be.

From a practical perspective, an agent can fit a regression, check its residuals and write a
paragraph about them faster than your team can, but whether the question was worth asking, which
outliers belong in the data and which limitation matters most to the people your answer is for are
judgements your team has to make, and most of the marks are for them.

## Project clinic

Session 26, on Monday December 7, will be an open lab and project clinic. Please bring the notebook
in whatever state it is in, and we will spend the session going through drafts with teams.

## Submitting

One member should submit for the whole team on Canvas, uploading the notebook as
`project_<teamname>.py`. If your data are small enough to upload, please include them; if not, the
notebook should download them in a cell, so that it runs for us as it ran for you.

We will adjust each member's share of the 180 points only in exceptional cases, because the peer
evaluation framework I trialled was a failure.

