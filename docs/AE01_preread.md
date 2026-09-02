# SI 385: Data Exploration

## Application exercise 1, pre-read: reading a skewed distribution

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 3, Wednesday September 9, 2026*

---

This is half of an application exercise.  It gives you the data and the question, and it
deliberately withholds the answer options, which you will see for the first time in the
room.  An hour spent here will make Wednesday considerably better for you, and a student
who arrives having read nothing but the question can still take part.  Nothing in this
document is submitted and nothing in it is graded.

## The data

Six hundred and seven self-reported data science salaries, collected between 2020 and
2022.  These are real people reporting their own pay to a public salary survey.

The file is Parquet rather than CSV.  Some of you used Parquet in SI 345 and some of you
did not, so here is the whole of what you need, and it behaves like any other DataFrame
once it has loaded:

```python
import pandas as pd

salaries = pd.read_parquet("data/ds_salaries.parquet")
salaries.head()
```

| Column | What it holds |
|---|---|
| `work_year` | 2020, 2021 or 2022 |
| `experience_level` | EN entry, MI mid, SE senior, EX executive |
| `employment_type` | FT full time, PT part time, CT contract, FL freelance |
| `job_title` | 50 distinct titles |
| `salary` | the number the person reported, in their own currency |
| `salary_currency` | the currency they reported it in |
| `salary_in_usd` | that figure converted to US dollars |
| `employee_residence` | where the person lives, 57 countries |
| `remote_ratio` | 0, 50 or 100 percent remote |
| `company_location` | where the employer is |
| `company_size` | S, M or L |

## Working in a notebook of your own

Every notebook you have opened so far was one I wrote.  For this one please make your own,
which takes a single command.  Choose a name, keep it inside the course folder, and run:

```bash
uv run marimo edit --no-sandbox notebooks/ae01_scratch.py
```

marimo sees that the file does not exist, creates it, and opens an empty notebook in your
browser.  Write your first cell and the file on disk fills itself in when you save.  It is
an ordinary Python file, so you can open it in any editor afterwards and read it top to
bottom.

Two things catch people out on a first notebook of their own:

- **A variable can be defined in exactly one cell.**  When you want a second version of
  something, give it a second name.
- **Put your imports in the first cell.**  marimo appends new cells at the bottom, so if
  you leave it to add an import for you it will land at the end, and a notebook that has
  to be read bottom to top is a poor thing to hand a teammate.

Nothing in this notebook is submitted.  It is scratch space for Wednesday.

## What is already known about it

You do not have to take any of this on trust, and re-deriving it is a reasonable way to
spend twenty minutes.

- `salary_in_usd` is right-skewed, with a mean of $112,298 against a median of $101,570.
- Two hundred and nine of the six hundred and seven salaries were reported in a currency
  other than US dollars and were converted.
- People living in the United States have a median of $138,475.  Everyone else has a
  median of $62,649.

## One thing I am telling you outright

Eighteen records sit at or above $250,000, and they run up to $600,000.

**Every one of those eighteen was reported in US dollars.**  The highest salary anywhere
in the file that was reported in any other currency is $196,979.

I am handing you that because finding it is most of an afternoon and it is not what
Wednesday is about.  The experience levels attached to those eighteen records are also
worth a look, and I will leave you to make of them what you will.

## The question

**What is the upper tail of this distribution?**

That is the entire question and it is not rhetorical.  On Wednesday your team will choose
one answer from a small fixed set, write a short justification, and reveal at the same
moment as every other team, and I expect the room to disagree.

## If you want to spend real time on this

None of this is a checklist and nobody is checking.

- Plot `salary_in_usd` and look at the shape rather than the summary of it.
- Work out what the mean, the median and a trimmed mean each tell you here, and what each
  of them would let you say out loud to somebody who had not seen the data.
- Split the file by residence, by currency, and by year, and see which splits change the
  picture and which leave it alone.
- Ask what this file does not record.  That question turns out to matter more than any of
  the ones it does answer, and it is the one I would spend the last ten minutes on.

## If you are taking SI 345 at the same time as this course

About ten of you are, for reasons ranging from study abroad to timetable collisions, and
that is a harder position than this course's syllabus assumes.  SI 385 is written on the
assumption that you finished 345 last term, which means you are being asked to use tools
you are still being taught.

Two things are worth saying plainly.

The first is that this exercise does not reward coding ability.  The question is what the
upper tail of the distribution actually is, and the four answers you will choose between
on Wednesday differ by interpretation rather than by computation.  A teammate who writes
the pandas faster does not thereby get closer to the answer, and the exercise is built
that way deliberately.

The second is that you should not spend an evening fighting syntax.  Below is working code
for everything the previous section suggests you look at, and please use it rather than
reconstructing it.  Every line has been run against the file you are being given.

```python
import pandas as pd

salaries = pd.read_parquet("data/ds_salaries.parquet")

# the shape itself, rather than a summary of it
salaries["salary_in_usd"].plot(kind="hist", bins=40)

# centre, three ways
salaries["salary_in_usd"].mean()
salaries["salary_in_usd"].median()

lo, hi = salaries["salary_in_usd"].quantile([0.1, 0.9])
salaries.loc[salaries["salary_in_usd"].between(lo, hi), "salary_in_usd"].mean()

# split it, and see which splits change the picture
salaries.groupby("employee_residence")["salary_in_usd"].median()
salaries.groupby("salary_currency")["salary_in_usd"].agg(["count", "median", "max"])
salaries.groupby("work_year")["salary_in_usd"].median()

# the eighteen records at the top
salaries[salaries["salary_in_usd"] >= 250_000].sort_values("salary_in_usd")
```

If any of that does not run for you, please ask on Slack rather than losing an evening to
it.  Slack reaches all three of us and it is usually the fastest route.  There are also
GSI office hours before we next meet, with Shan on Thursdays from 2 to 3 and Zach on
Sundays from 7 to 8.

## What happens on Wednesday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual.  You take a position and write it down |
| 0:23–0:50 | Your team argues, converges on one option, and submits a justification |
| 0:50–1:15 | Every team reveals at once, and several are asked to defend |

Only the justification is graded, not the choice itself.
