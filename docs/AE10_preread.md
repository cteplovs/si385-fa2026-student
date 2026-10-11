# SI 385: Data Exploration

## Application exercise 10, pre-read: does pricier candy win?

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 12, Monday October 12, 2026*

---

This is half of an application exercise: it gives you the question and withholds the answer
options, which you see for the first time in the room, and nothing here is submitted or graded.

## The data

The file holds FiveThirtyEight's *Ultimate Halloween Candy Power Ranking* (2017), for which
visitors to the site were shown two candies at a time and asked which they would rather receive.
It has 85 rows, one per candy, and the data are published under CC BY 4.0, so please credit
FiveThirtyEight if you use them elsewhere.

```python
import pandas as pd

candy = pd.read_csv("data/candy-data.csv")
```

| Kind | Columns |
|---|---|
| Name | `competitorname` |
| What it contains, 1 for yes and 0 for no | `chocolate`, `fruity`, `caramel`, `peanutyalmondy`, `nougat`, `crispedricewafer` |
| What form it takes, 1 for yes and 0 for no | `hard`, `bar`, `pluribus` (one of many in a bag or box) |
| Percentiles within the 85 | `sugarpercent`, `pricepercent` |
| The outcome | `winpercent` |

## Note this:

`winpercent` is the percentage of its head-to-head matchups that a candy won, so 50 means it won
as often as it lost. It records the preferences of the people who voted on FiveThirtyEight's site,
which is not the same thing as what any particular group of people will eat.

`pricepercent` and `sugarpercent` are percentiles, not prices or grams. A candy with a
`pricepercent` of 0.9 costs more per unit than about 90% of the candies in the file, so a change
of 1 in either column runs from the cheapest candy in the set to the most expensive.

Two rows, `One dime` and `One quarter`, are coins rather than candy, and FiveThirtyEight included
them on purpose.

## The scenario and question

Your hall council is buying candy for a Halloween party and wants the candy that people like best.
A council member who has taken a statistics class runs this file and asks your team one thing.

> **Should the council pay more for pricier candy?**

On Monday your team will choose one answer from a small fixed set, write a short justification,
and reveal at the same moment as every other team.

## If you want to spend time on this

If you have time before Monday, the following will help.

- Please read Bruce et al. ch. 1, §*Correlation*, and ch. 4, §§ *Simple Linear Regression* and
  *Multiple Linear Regression*, which are Monday's reading. The notebook's worked example fits a
  regression of the kind the reading describes.
- Look at which kinds of candy are expensive and which kinds win, and ask whether those are the
  same candies.
- RAT 9 asks how to read a coefficient in a model with more than one predictor, and your answer
  there bears on this question.

## The plan for Monday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual. You take a position and write it down |
| 0:23–0:50 | Your team argues, converges on one option, and submits |
| 0:50–1:15 | Every team reveals at once, and several are asked to defend |

Your team submits a piece of code with its justification, and the two are graded together. The
code fits a regression and reports a confidence interval, and the notebook gives you a worked
example to start from.

## The other half, and where to find it

**The notebook** goes up before class, so please run `uv run update.py` from inside the course
folder when you arrive; it pulls the notebook and the data into your course folder.

**The Canvas assignment**, *AE 10: Does pricier candy win?*, opens when class does, and one person
submits for the whole team and the mark reaches everyone. Sli.do draws the histogram the room
looks at before anyone speaks and is not graded; the Canvas submission is the one that counts.
