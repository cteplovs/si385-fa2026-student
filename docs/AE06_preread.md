# SI 385: Data Exploration

## Application exercise 6, pre-read: the second free throw

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 8, Monday September 28, 2026*

---

This is half of an application exercise. It gives you the data and the question, and it
withholds the answer options, which you meet for the first time in the room. Nothing here is
submitted and nothing here is graded, and a student who arrives having read only the question
can still take part.

## The data

The file records NBA free throws from the 2006-07 season to 2015-16. When a player is fouled
in the act of shooting, he usually goes to the line for two shots in a row, with nobody
guarding him and the same distance to the basket each time. That is interesting from a
statistical perspective, because a trip to the line is about as controlled a repeated
measurement as professional sport offers. It's like having instant replication.

Each row of the file is one such trip, with the first shot and the second. There are 268,094
trips, taken by 1,091 players.

```python
import pandas as pd

trips = pd.read_parquet("data/nba_free_throw_pairs.parquet")
trips.head()
```

| Column | What it holds |
|---|---|
| `player` | the player's name |
| `season` | the season, such as `2012-13` |
| `playoffs` | whether the game was a playoff game |
| `first_made` | whether the first shot went in |
| `second_made` | whether the second shot went in |

The table is derived from the *NBA Free Throws* dataset published on Kaggle by Sebastian
Mantey, <https://www.kaggle.com/datasets/sebastianmantey/nba-free-throws>, which was
collected from ESPN's play-by-play records. We have processed that data to keep only the five columns above.

## Note this:

Across the whole file, the second shot goes in **79.5%** of the time when the first went in,
and **73.2%** of the time when the first missed.

Players differ a great deal at the line. Some make more than nine free throws in ten, and some
make fewer than six.

## The scenario and question

LeBron James has just missed the first of two free throws. The broadcast analyst says:

> **"The numbers say that makes no difference to the second."**

> **Is the analyst right?**

On Monday your team will choose one answer from a small fixed set, write a short
justification, and reveal at the same moment as every other team. The options differ on which
players' free throws count as evidence about LeBron.

## If you want to spend time on this

None of this is a checklist and nobody is checking.

- Please re-read the bootstrap pseudocode in Shasha and Wilson ch. 1, which is part of the
  reading for Monday. The exercise asks you to write one.
- Look at LeBron's own trips, and then at some other players'. Ask which of them tell you
  something about him.
- Ask what counts as one independent observation in this file. Ch. 2 of the reading has
  something to say about it.

## Monday asks you to write a bootstrap

Your team's justification will include a bootstrap you write yourselves, of about ten to
fifteen lines, for the evidence your answer rests on, together with the 90% interval it
produces. The notebook gives you a complete, working bootstrap for LeBron's own trips to start
from, and a check that tells you whether your version behaves correctly on two real players.

It does not matter who on the team writes the code, or whether you have help writing it, as
long as it runs against the file and produces the interval you cite.

**When you paste code into the Canvas text box**, please select those lines, open the
**Format** menu in the editor, and choose **Code**. Pasted as ordinary text, Canvas collapses
the indentation and curls the quotes, and what arrives cannot be run.

## The plan for Monday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual. You take a position and write it down |
| 0:23–0:50 | Your team argues, writes its bootstrap, converges on one option, and submits |
| 0:50–1:15 | Every team reveals at once, and several are asked to defend |

Only the justification and the code are graded, not the choice itself.

The justification asks for four things: which evidence your answer rests on and why it is
about LeBron, what your code resamples and why, when you chose the players you used, and which
result would have changed your answer.

## The other half, and where to find it

**The notebook** goes up on Monday morning. Please run `uv run update.py` from inside the
course folder when you arrive, which pulls `notebooks/lectures/L08_sampling_and_uncertainty.py`
into your course folder. It carries the worked example, the check, and the options.

**The Canvas assignment**, *AE 6: The second free throw*, opens when class does. One person
submits for the whole team and the mark reaches everyone. Sli.do draws the histogram the room
looks at before anyone speaks and is not graded; the Canvas submission is the one that counts.
