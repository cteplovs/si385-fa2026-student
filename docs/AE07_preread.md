# SI 385: Data Exploration

## Application exercise 7, pre-read: the streaky few

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 9, Wednesday September 30, 2026*

---

This is half of an application exercise: it gives you the question and withholds the answer
options, which you meet for the first time in the room. Nothing here is submitted or graded.

It also went up a day late, which makes it **context only**: nothing in it is needed to do well
on Wednesday, and everything in it is also in the notebook you will open in class. If you have
time tonight and are curious, it is here, and if you do not, you are not behind.

## The data

The file is the one from Monday: NBA free throws from 2006-07 to 2015-16, one row per trip to
the line with at least two shots.

```python
import pandas as pd

trips = pd.read_parquet("data/nba_free_throw_pairs.parquet")
```

On Wednesday we work with the same 180 regular shooters that ended Monday's session, meaning the
players with at least 500 trips and at least 50 missed first shots.

## Note this:

Monday's question was about one player, and Wednesday's is about all 180, one at a time. For
each player, the analyst runs the shuffle test from Chapter 1 of Shasha and Wilson on his own trips:
shuffle his first-shot results, recompute the gap between his second shot after a make and
after a miss, and see how often the shuffled gap is at least as large as the real one.

## The scenario and question

The broadcast analyst from Monday is back:

> **"We ran the shuffle test on all 180 regular shooters. Only 30 make their second shot
> significantly more often after a make. For the other 150 the first shot makes no difference,
> and the league-wide effect comes from a few streaky shooters."**

> **Is the analyst right?**

On Wednesday your team will choose one answer from a small fixed set, write a short
justification, and reveal at the same moment as every other team.

## If you want to spend time on this

None of this is a checklist and nobody is checking.

- Please re-read the coin example and the shuffle test in Shasha and Wilson ch. 1, which are
  part of the reading for Wednesday.
- The analyst's sentence makes more than one claim. Ask what each part claims, and what
  evidence would test it.
- RAT 6 asks what a test that does not pass tells you, and your answer there bears on this
  question.

## Wednesday asks you to write a test

Your team's justification will include a test of the analyst's claim that you write yourselves,
together with what it found, and your team chooses which part of the claim to test. The notebook
gives you a working shuffle test to start from, and the table of all 180 players with each one's
result.

It does not matter who on the team writes the code, or whether you have help writing it, as
long as it runs against the file and produces the result you cite.

**When you paste code into the Canvas text box**, please select those lines, open the
**Format** menu in the editor, and choose **Code**. Pasted as ordinary text, Canvas collapses
the indentation and curls the quotes, and what arrives cannot be run.

## The plan for Wednesday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual. You take a position and write it down |
| 0:23–0:50 | Your team argues, writes its test, converges on one option, and submits |
| 0:50–1:15 | Every team reveals at once, and several are asked to defend |

Only the justification and the code are graded, not the choice itself. The justification asks
for three things: which part of the analyst's claim your test
addresses, what your test would have shown if the analyst were right, and which part of the
claim your test leaves unanswered.

## The other half, and where to find it

**The notebook** goes up before class. Please run `uv run update.py` from inside the course
folder when you arrive, which pulls `notebooks/lectures/L09_hypothesis_testing_i.py` into your
course folder. It carries the worked shuffle test, the table of 180 players, and the options.

**The Canvas assignment**, *AE 7: The streaky few*, opens when class does. One person submits
for the whole team and the mark reaches everyone. Sli.do draws the histogram the room looks at
before anyone speaks and is not graded; the Canvas submission is the one that counts.
