# SI 385: Data Exploration

## Application exercise 3, pre-read: what does a blank mean?

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 5, Wednesday September 16, 2026*

---

**Nothing in this document is needed to do well on Wednesday.** Everything in it is also in
the notebook you will open in class. It went up later than it should have, so it is here as
context for anyone who wants a head start, and not as preparation anyone is expected to have
done. Nothing in it is submitted and nothing in it is graded.

Like the last two pre-reads, it gives you the data and the question and withholds the answer
options, which you will see for the first time in the room.

## The data

In 2014, Open Sourcing Mental Illness (OSMI), a non-profit, ran an online survey of people
working in tech about mental health and the workplace. 1,259 people answered. The responses
are public under a Creative Commons licence (CC BY-SA 4.0), and the file is already in your
course folder, assuming you've done `uv run update.py` from your course folder.

```python
import pandas as pd

survey = pd.read_csv("data/survey.csv")
survey.shape
```

Each row is one person. Most of the 27 columns are questions about their employer. Three
matter most on Wednesday, and here they are with the survey's own wording:

| Column | The question asked |
|---|---|
| `treatment` | *Have you sought treatment for a mental health condition?* |
| `work_interfere` | *If you have a mental health condition, do you feel that it interferes with your work?* Never, Rarely, Sometimes, or Often |
| `mental_health_consequence` | *Do you think that discussing a mental health issue with your employer would have negative consequences?* |

Please read the wording of `work_interfere` twice. It opens with *if*.

## Note this:

**264 people left `work_interfere` blank.** That is 21% of the file.

```python
survey["work_interfere"].isna().sum()
```

The survey does not record why. Some of those people may have no mental health condition and
skipped a question that did not apply to them. Some may have a condition and preferred not to
say. The file holds their other answers, but not their reasons.

This is the distinction van Buuren draws in the reading, applied to 264 real people.

## The scenario and question

A 200-person software company is choosing a mental health benefit. The HR lead has no data on
the company's own staff, so the plan has to come from this survey:

> **How many of the 200 people will say a mental health condition interferes with their work
> at least sometimes? What should the HR lead plan for?**

On Wednesday your team will choose one answer from a small fixed set, write a short
justification, and reveal at the same moment as every other team. The options will differ on
what a blank is taken to mean, and I expect the room to disagree.

## If you want to spend time on this

None of this is a checklist and nobody is checking.

- Work out what share of people answered "Often" or "Sometimes". Then ask what you had to
  decide about the 264 blank rows to get that number, and whether you noticed deciding it.
- Look at who the 264 are. The rest of each row is still there.
- Look at the `state` column, which is also full of blanks, and ask whether they are the same
  kind of blank.
- Look at `Age`. Some of the values are impossible, and it is worth deciding whether an
  impossible value and a blank are the same problem.

## Wednesday asks for one line of code

This is different from the last two exercises. Your team's justification will have to cite
**one number from the file that the notebook does not show you**, along with the line of code
that produced it. One line of pandas is enough. It does not matter who on the team writes it,
or whether you have help writing it, as long as it runs against the data and produces the
number you cite.

The notebook has an empty cell ready for it, so nobody needs to arrive with anything set up.

If you are taking SI 345 at the same time as this course, the line being asked for is the
kind you have already written: a count, a filter, or a `value_counts`. If anything in this
document does not run for you, please ask on Slack, which reaches all three of us.

## What happens on Wednesday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual. You take a position and write it down |
| 0:23–0:50 | Your team argues, runs its line of code, converges on one option, and submits a justification |
| 0:50–1:15 | Every team reveals at once, and several are asked to defend |

Only the justification is graded, not the choice itself.

The justification asks for three things: what you think a blank means, the number you
computed with the code that produced it, and the one fact about the 264 people that would move
you off your answer if you could learn it.

## The other half, and where to find it

**The notebook** goes up on Wednesday morning. Please run `uv run update.py` from inside the
course folder when you arrive, which pulls `notebooks/lectures/L05_missingness.py` into your
course folder.

**The Canvas assignment**, *AE 3: What does a blank mean?*, opens when class does. One person
submits for the whole team and the mark reaches everyone. Sli.do draws the histogram the room
looks at before anyone speaks and is not graded; the Canvas submission is the one that counts.
I will try to not mix up the letter options with the histogram display this time. 😉
