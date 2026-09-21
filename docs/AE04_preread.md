# SI 385: Data Exploration

## Application exercise 4, pre-read: does remote work pay?

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 6, Monday September 21, 2026*

---

This is half of an application exercise. It gives you the data and the question, and it
withholds the answer options, which you meet for the first time in the room. It is up early
on purpose, so that an hour spent on it is an hour you choose rather than one you scramble
for. A student who arrives having read only the question can still take part. Nothing here is
submitted and nothing here is graded.

## The data

The salary file from session 3, and deliberately so. 607 data science roles reported between
2020 and 2022, one row per role, already in your course folder if you have run
`uv run update.py`.

```python
import pandas as pd

salaries = pd.read_parquet("data/ds_salaries.parquet")
salaries.head()
```

In session 3 you described a single column of this file. Monday's question needs three.

| Column | What it holds |
|---|---|
| `remote_ratio` | 0 for onsite, 50 for hybrid, 100 for fully remote |
| `salary_in_usd` | the salary, converted to US dollars |
| `company_location` | the country the company is in |
| `company_size` | S, M or L |
| `experience_level` | EN entry, MI mid, SE senior, EX executive |
| `work_year` | 2020, 2021 or 2022 |

There are five more columns, and none of them are decoration.

## Note this:

Here is the summary somebody ran, and it is arithmetically correct.

| `remote_ratio` | Roles | Median USD |
|---|---|---|
| 0 — onsite | 127 | 99,000 |
| 50 — hybrid | 99 | 69,999 |
| 100 — fully remote | 381 | 115,000 |

Fully remote sits about **64% above hybrid**. The dip in the middle is the part worth staring
at: whatever story you want to tell about remote work, it has to explain why half-remote looks
worse than either end.

One more thing I am handing you outright, because you would find it in a line of pandas:
**58.5% of these roles are at companies in the United States.**

## The scenario and question

A 200-person company's People team is rewriting its job adverts. Someone wants to put this
line in them:

> **Fully remote roles in this field pay about 64% more than hybrid ones.**

The arithmetic behind the sentence is right.

> **What should the People team do with it?**

On Monday your team will choose one answer from a small fixed set, write a short
justification, and reveal at the same moment as every other team. The options differ on what
the 64% is actually measuring.

## If you want to spend time on this

None of this is a checklist and nobody is checking.

- Group the comparison by something else and see whether the ordering survives. The reading
  for Monday calls this conditioning.
- Whatever you group by, print the counts next to the medians. A median over four roles is a
  number, and it is not evidence.
- Ask who the sentence is written for. Someone reads an advert and decides whether to take a
  job; the file describes roles reported to a salary survey.

## Monday asks for three to five lines of code

Your team's justification will have to condition the comparison on a variable the notebook
does not already use, in three to five lines, and show the table it produced — counts as well
as medians. One `pivot_table` will do most of it.

It does not matter who on the team writes the lines, or whether you have help writing them,
as long as they run against the file and produce the table you cite. The notebook has an empty
cell ready, so nothing needs setting up in advance.

**One piece of housekeeping that will save you a bad five minutes.** When you paste code into
the Canvas text box, select those lines, open the **Format** menu in the editor, and choose
**Code**. The text turns monospaced and your indentation survives. Pasted as ordinary
text, Canvas collapses the leading spaces that tell Python what sits inside a block and turns
your straight quotes into curly ones, and what arrives is something nobody can run.

If anything in this document does not run for you, please ask on Slack, which reaches all
three of us. GSI office hours before we meet are Thursday 2–3 with Shan and Sunday 7–8 with
Zach.

## What happens on Monday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual. You take a position and write it down |
| 0:23–0:50 | Your team argues, runs its lines of code, converges on one option, and submits |
| 0:50–1:15 | Every team reveals at once, and several are asked to defend |

Only the justification is graded, not the choice itself.

The justification asks for three things: what you think the 64% is measuring, the table you
produced with the code that produced it, and what that table did to the claim — strengthened
it, broke it, or left it standing.

## The other half, and where to find it

**The notebook** goes up on Monday morning. Please run `uv run update.py` from inside the
course folder when you arrive, which pulls `notebooks/lectures/L06_multivariate.py` into your
course folder. It carries the table above, a grouping you can change to watch the medians
move, and the options.

**The Canvas assignment**, *AE 4: Does remote work pay?*, opens when class does. One person
submits for the whole team and the mark reaches everyone. Sli.do draws the histogram the room
looks at before anyone speaks and is not graded; the Canvas submission is the one that counts.
