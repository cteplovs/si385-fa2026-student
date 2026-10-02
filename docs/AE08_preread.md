# SI 385: Data Exploration

## Application exercise 8, pre-read: which country grows the best cocoa?

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 10, Monday October 5, 2026*

---

This is half of an application exercise: it gives you the question and withholds the answer
options, which you meet for the first time in the room. Nothing here is submitted or graded.

DoU 1 is due the same day, so Monday is deliberately lighter than usual. Everything you need is
in the room, and if you spend your weekend on the DoU instead of this page, you are not behind.

## The data

The file holds chocolate bar ratings from *Flavors of Cacao*, a review guide in which one
reviewer has rated bars from makers around the world since 2006. It covers 2,530 bars reviewed
from 2006 to 2021, one row per bar.

```python
import pandas as pd

bars = pd.read_csv("data/chocolate.csv")
```

Each row records the maker and the maker's country, the year of the review, the country the
cocoa beans came from, the cocoa percentage, the ingredients, a few words on flavour, and the
rating. The guide describes its scale as follows:

| Rating | Meaning |
|---|---|
| 4.0 and above | Outstanding |
| 3.5 to 3.9 | Highly recommended |
| 3.0 to 3.49 | Recommended |
| 2.0 to 2.9 | Disappointing |
| 1.0 to 1.9 | Unpleasant |

No bar in this file is rated above 4.0, and ratings move in quarter points.

## Note this:

`country_of_bean_origin` is where the beans were grown, which is usually not where the bar was
made. Most of its values are countries, but one is **Blend**, which covers bars made from beans
of more than one origin. Some origins have hundreds of bars and others have one or two, and
on Monday we work with the 21 countries that have at least 30.

Every rating is one person's judgement of one bar from one batch, which the guide itself is
careful to say.

## The scenario and question

A chocolate shop near campus wants to stock the best bars it can. The owner reads the file and
comes to a conclusion about which country grows the best cocoa, backed by an average and an
interval.

> **What do you tell the owner?**

On Monday your team will choose one answer from a small fixed set, write a short justification,
and reveal at the same moment as every other team.

## If you want to spend time on this

None of this is a checklist and nobody is checking.

- Please read the *ANOVA* section of Bruce et al. ch. 3, which is part of Monday's reading. Its
  web-page example asks the same kind of question with four groups instead of 21.
- Ask what it would take for one country out of 21 to come out on top by chance alone.
- RAT 7 asks what a single overall test can and cannot tell you, and your answer there bears on
  this question.

## The plan for Monday

The session opens with a short game that needs no preparation, and then turns to the owner.

| Time | What |
|---|---|
| 0:15–0:25 | A game with the room, played in Sli.do |
| 0:25–0:30 | Silent and individual. You take a position and write it down |
| 0:30–0:47 | Your team argues, converges on one option, and submits |
| 0:47–1:12 | Every team reveals at once, and several are asked to defend |

Only the justification is graded, not the choice itself. No code is required this time, though
the notebook has a test your team may run if it wants to cite one.

## The other half, and where to find it

**The notebook** goes up before class. Please run `uv run update.py` from inside the course
folder when you arrive, which pulls the notebook and the data into your course folder.

**The Canvas assignment**, *AE 8: Which country grows the best cocoa?*, opens when class does.
One person submits for the whole team and the mark reaches everyone. Sli.do draws the histogram
the room looks at before anyone speaks and is not graded; the Canvas submission is the one that
counts.
