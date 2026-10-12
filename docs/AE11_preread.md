# SI 385: Data Exploration

## Application exercise 11, pre-read: is Yandex crawling less?

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 13, Wednesday October 14, 2026*

---

This is half of an application exercise: it gives you the question and withholds the answer
options, which you see for the first time in the room, and nothing here is submitted or graded.

## Data

The file holds twelve weeks of daily web traffic from the network that Yandex, Russia's largest
internet company, uses for its own services, including the crawler that indexes the web for
Yandex search. It comes from Cloudflare Radar, which sees the requests that pass through
Cloudflare's network and classifies each one as likely automated or likely human. There are 84
rows, one per day (in UTC) from July 20 to October 11, 2026. The data are published under
CC BY-NC 4.0, so please credit Cloudflare Radar if you use them elsewhere.

```python
import pandas as pd

yandex = pd.read_csv("data/yandex_bot_traffic.csv", parse_dates=["date"])
```

| Column | What it holds |
|---|---|
| `date` | The day, in UTC |
| `day_of_week` | `Mon` to `Sun` |
| `bot_index` | Requests classified as automated, as a fraction of the busiest day in the file |
| `human_index` | Requests classified as human, on the same scale |

## What the numbers mean

Cloudflare does not publish request counts, so both columns are indexes rather than counts. The
busiest day for automated traffic is set to 1, and every other value in both columns is a
fraction of that day, so a `bot_index` of 0.5 means half as many automated requests as the
busiest day. Because the two columns share a scale, you can compare them directly: human traffic
from this network is about 1% of its automated traffic.

Cloudflare Radar's annotation for this period notes that Yandex shut down its data centre in Sasovo,
Ryazan, after a drone strike started a fire there, beginning late on October 7 (UTC).

## Scenario and question

You work on capacity planning at a company that hosts websites, and Yandex's crawler is one of
the heaviest automated visitors to your customers' sites. Your manager is setting next quarter's
budget and has asked your team the following question.

> **Is Yandex's crawling declining, or not?**

On Wednesday your team will choose one answer from a small fixed set, write a short
justification, and reveal at the same moment as every other team.

## Optional preparation

If you have time before Wednesday, the following will help.

- Please read Bruce et al. ch. 4, §*Regression Diagnostics*, which is Wednesday's reading. The
  notebook's worked example fits a regression of the kind Monday's reading describes, and the
  diagnostics section is about how far to trust it.
- Plot `bot_index` against `date` and look at the whole series before fitting anything.
- Consider what a trend fitted to twelve weeks of this series can tell your manager about next
  quarter, and what it cannot.

## Schedule for Wednesday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual. You take a position and write it down |
| 0:23–0:50 | Your team argues, converges on one option, and submits |
| 0:50–1:15 | Every team reveals at once, and several are asked to defend |

Your team submits a piece of code with its justification, and the two are graded together. The
code fits a regression and reports a confidence interval, and the notebook gives you a worked
example to start from.

## Notebook and submission

**The notebook** goes up before class, so run `uv run update.py` from inside the course
folder when you arrive; it pulls the notebook and the data into your course folder.

**The Canvas assignment**, *AE 11: Is Yandex crawling less?*, opens when class does, and one
person submits for the whole team and the mark reaches everyone. Only the Canvas submission is
graded; Sli.do draws the histogram the room looks at before anyone speaks.
