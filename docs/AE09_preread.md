# SI 385: Data Exploration

## Application exercise 9, pre-read: which squirrel fact goes on the tour?

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 11, Wednesday October 7, 2026*

---

This is half of an application exercise: it gives you the question and withholds the answer
options, which you see for the first time in the room, and nothing here is submitted or graded.

## The data

The file holds the 2018 Central Park Squirrel Census, in which volunteers walked every part of
the park between 6 and 20 October 2018 and recorded each squirrel they saw. It has 3,023 rows,
and each row is one sighting, not one squirrel, since nobody can tell whether the squirrel by the
pond at 9:00 is the one seen there at 4:00.

```python
import pandas as pd

squirrels = pd.read_csv("data/nyc_squirrels.csv")
```

Each row records where and when the squirrel was seen (`hectare` of the park grid, `shift` AM or
PM, `date`), its `age`, its `primary_fur_color`, and a set of true-or-false columns for what it
was doing:

| Kind | Columns |
|---|---|
| Moving and feeding | `running`, `chasing`, `climbing`, `eating`, `foraging` |
| Calls | `kuks`, `quaas`, `moans` |
| Tail | `tail_flags`, `tail_twitches` |
| Towards people | `approaches`, `indifferent`, `runs_from` |

## Note this:

`primary_fur_color` is gray, cinnamon or black, and it is missing for some sightings. The three
colours are far from equal in number, so please look at how many of each there are before you
compare them.

The census describes the calls as follows: a kuk is a chirpy call used for a variety of reasons,
a quaa is an elongated call that can signal a predator on the ground, and a moan is a
high-pitched call that can signal a predator in the air.

Every true or false is one volunteer's judgement after a few seconds of watching, so "approaches"
means that the volunteer thought the squirrel came towards them, not that anyone measured it.

## The scenario and question

A company that runs walking tours of Central Park wants one fact about squirrel colours for its
script. A blogger has gone through the census, comparing the three colours on the behaviour
columns, and offers the company two facts. Each says that squirrels of one colour do something
more often than gray squirrels do, and each comes with rates and a chi-square p-value below 0.05.

> **Which fact belongs in the script?**

On Wednesday your team will choose one answer from a small fixed set, write a short
justification, and reveal at the same moment as every other team.

## If you want to spend time on this

If you have time before Wednesday, the following will help.

- Please read the *Chi-Square Test* section of Bruce et al. ch. 3, which is Wednesday's reading.
  Its resampling version of the test is the code you will adapt in the room.
- Ask what it means that the blogger went through every behaviour column looking for a
  difference, and what you would want to know about the count behind each rate.
- RAT 8 asks about both of those, and your answers there bear on this question.

## The plan for Wednesday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual. You take a position and write it down |
| 0:23–0:50 | Your team argues, converges on one option, and submits |
| 0:50–1:15 | Every team reveals at once, and several are asked to defend |

This time your team submits a piece of code with its justification, and the two are graded
together. The code adapts the reading's resampling test, and the notebook gives you a worked
example to start from.

## The other half, and where to find it

**The notebook** goes up before class, so please run `uv run update.py` from inside the course
folder when you arrive; it pulls the notebook and the data into your course folder.

**The Canvas assignment**, *AE 9: Which squirrel fact goes on the tour?*, opens when class does,
and one person submits for the whole team and the mark reaches everyone. Sli.do draws the histogram
the room looks at before anyone speaks and is not graded; the Canvas submission is the one that
counts.
