# SI 385: Data Exploration

## Application exercise 12, pre-read: the interview loop

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 14, Wednesday October 21, 2026*

---

This is half of an application exercise: it tells you what Wednesday involves and withholds the
question, which you see for the first time in the room. Nothing here is submitted or graded,
and there is nothing to prepare over the break.

## What Wednesday is

Session 14 is the synthesis session for Module 2, so it has no reading and no RAT. It is
modelled on the Python rounds of real data science interviews, which are less often coding
puzzles than you might expect and more often statistical reasoning with code: rebuilding a
statistical idea as a function, reading code someone else wrote, or investigating a question
about a dataset with whatever tools you like, including an agent. The period runs as a short
sequence of those rounds, worked as a team.

## Data

The data are the data science salaries file you used in application exercises 1 and 4, which
is already in your course folder:

```python
import pandas as pd

salaries = pd.read_parquet("data/ds_salaries.parquet")
```

If you would like to do something before Wednesday, please look again at the columns in the
AE 1 pre-read. Please also run `uv run update.py` before class, as usual.
