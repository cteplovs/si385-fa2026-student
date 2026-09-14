# SI 385: Data Exploration

## Application exercise 2, pre-read: a sentence that is true

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 4, Monday September 14, 2026*

---

This is half of an application exercise.  It gives you the data and the question, and it
deliberately withholds the answer options, which you will see for the first time in the
room.  An hour spent here will make Monday considerably better for you, and a student who
arrives having read nothing but the question can still take part.  Nothing in this document
is submitted and nothing in it is graded.

## The data

Every entry in a Summer Olympic Games between 1896 and 2016: 222,552 rows, one per athlete
per event.  Real people, and the same person appears once for each event they entered.

```python
import pandas as pd

olympics = pd.read_parquet("data/olympic_heights.parquet")
olympics.head()
```

| Column | What it holds |
|---|---|
| `year` | 1896 to 2016, Summer Games only |
| `sex` | M or F, as recorded by the Games |
| `sport` | 52 sports |
| `event` | the specific event within the sport |
| `height_cm` | height in centimetres, **where anyone recorded one** |
| `weight_kg` | weight in kilograms, same caveat |
| `age` | age in years, same caveat |
| `noc` | three-letter national committee code |

The rows with no height have been left in rather than dropped.  That was a deliberate
choice on my part and you may want to think about why.

## Working in a notebook of your own

Same as last time: make your own scratch notebook rather than working in mine.

```bash
uv run marimo edit --no-sandbox notebooks/ae02_scratch.py
```

marimo creates the file and opens it empty.  The two things that caught people out in
session 3 are still true.  A variable can be defined in exactly one cell, and your imports
belong in the first cell rather than wherever marimo decides to put them.

## What is already known about it

You do not have to take any of this on trust, and re-deriving it is twenty minutes well
spent.

Comparing the 1920s with the 2010s, across everyone who has a height recorded:

| | 1920s | 2010s |
|---|---|---|
| Mean height, everyone | 175.4 cm | 176.1 cm |
| Mean height, men | 175.9 cm | 181.6 cm |
| Mean height, women | 165.7 cm | 169.6 cm |
| Women as a share of the measured field | 4.9% | 45.4% |

## One thing I am telling you outright

**The average is flat and both groups rose.**  Pooled, a century of Olympic sport moves the
mean height by seven millimetres.  Split by sex, men gain 5.7 cm and women 3.9 cm.  Neither
number is wrong and neither is a trick.  The pooled average is dragged by the fact that the
Games admitted almost no women in 1924 and admits nearly half now.

I am handing you that because finding it is an afternoon and it is not what Monday is
about.

There is a second thing in the file, and I am handing you this one too:

| Decade | Entries | With a height recorded |
|---|---|---|
| 1920s | 14,517 | 17.3% |
| 2010s | 26,608 | 98.7% |

Whoever was measured in 1924 was not a random fifth of the field.  Nothing in the file says
who they were or why they and not the rest.

## The question

A wire service has this file and is about to run this sentence:

> **Olympic athletes are no taller today than they were a century ago.**

The number behind it is correct.

**Should the sentence run?**

That is the entire question and it is not rhetorical.  On Monday your team will choose one
answer from a small fixed set, write a short justification, and reveal at the same moment as
every other team.  I expect the room to disagree, and the disagreement is the lesson rather
than a failure of the exercise.

## If you want to spend real time on this

None of this is a checklist and nobody is checking.

- Draw the pooled line and the two sex lines on the same axes and look at them together.
- The composition of the *Games* changed as well as the composition of the field.  Ask
  whether the sports that were added between 1924 and 2016 were tall sports, and whether
  that is enough on its own to explain anything.
- Pick a sport that ran in both decades and compare it with itself.  This is probably the
  most useful twenty minutes available to you here, and what it turns up is worth arriving
  with.
- Ask what a reader who sees only the sentence would go away believing, and whether the
  file supports it.

## If you are taking SI 345 at the same time as this course

The point from last time stands: this exercise does not reward coding ability.  The
arithmetic is above, already done.  What is being asked for is a ruling on a sentence, and
a teammate who writes the pandas faster does not thereby get closer to it.

Working code for everything the previous section suggests, run against the file you are
being given:

```python
import pandas as pd

olympics = pd.read_parquet("data/olympic_heights.parquet")
measured = olympics.dropna(subset=["height_cm"]).copy()
measured["decade"] = (measured["year"] // 10) * 10

# the pooled line, and the two lines underneath it
measured.groupby("decade")["height_cm"].mean()
measured.groupby(["decade", "sex"])["height_cm"].mean().unstack()

# who is in the field
measured.assign(is_f=measured["sex"].eq("F")).groupby("decade")["is_f"].mean()

# how much of each decade carries a height at all
olympics.assign(decade=(olympics["year"] // 10) * 10) \
        .groupby("decade")["height_cm"].agg(["size", "count"])

# which sports ran in both decades
early = set(measured.loc[measured["decade"] == 1920, "sport"])
late = set(measured.loc[measured["decade"] == 2010, "sport"])
sorted(early & late)

# one sport, compared with itself
one = measured[measured["sport"] == "Athletics"]
one.groupby(["decade", "sex"])["height_cm"].mean().unstack()
```

If any of that does not run for you, please ask on Slack rather than losing an evening to
it.  Slack reaches all three of us.  GSI office hours before we next meet are Shan on
Thursday from 2 to 3 and Zach on Sunday from 7 to 8.

## What happens on Monday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual.  You take a position and write it down |
| 0:23–0:50 | Your team argues, converges on one option, and submits a justification |
| 0:50–1:15 | Every team reveals at once, and several are asked to defend |

Only the justification is graded, not the choice itself.

The justification asks for two things.  Name the reader you have in mind and what they
would take away from those nine words.  Then name the one fact that, if this file carried
it, would move you off your answer.

## The other half, and where to find it

The answer options are the part this document withholds, and they arrive in the room.

**The notebook** goes up on Monday morning.  Please run `uv run update.py` from inside the
course folder when you arrive, which pulls
`notebooks/lectures/L04_visual_reasoning.py` into your course folder.  Alongside the options
it carries the figures you have seen here, and a grouping you can change to watch the
pooled line come apart.

**The Canvas assignment**, *AE 2: Have Olympic athletes gotten taller?*, opens when class
does.  One person submits for the whole team and the mark reaches everyone, so please check
you are in a team on Canvas before Monday, under People, on the **Teams** tab.  Sli.do
draws the histogram the room looks at before anyone speaks and is not graded; the Canvas
submission is the one that counts, and it closes at 0:50.
