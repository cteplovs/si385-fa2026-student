# SI 385: Data Exploration

## Application exercise 11, pre-read: how much did the strikes take offline?

*Dr. Chris Teplovs, School of Information, University of Michigan*

*For session 13, Wednesday October 14, 2026*

---

This is half of an application exercise: it gives you the question and withholds the answer
options, which you see for the first time in the room, and nothing here is submitted or graded.

*Revised Tuesday October 13. The data are unchanged; the scenario and the question are new.*

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
from this network is about 1% of its automated traffic, so `bot_index` is in effect a measure of
the network's traffic as a whole.

Cloudflare Radar's annotation for this period notes that Yandex shut down its data centre in Sasovo,
Ryazan, after a drone strike started a fire there, beginning late on October 7 (UTC). News reports
describe further strikes on Yandex data centres in the Kaluga and Vladimir regions over the
following days.

## Scenario and question

News reports this week said that traffic from Yandex's network fell to less than one percent of
its peak after the strikes. A journalist writing a follow-up wants a figure that a reader can
trust, and has asked your team the following question.

> **Over October 8 to 11, what share of Yandex's normal traffic did the strikes take offline?**

On Wednesday your team will choose one answer from a small fixed set, write a short
justification, and reveal at the same moment as every other team.

## Optional preparation

If you have time before Wednesday, the following will help.

- Please read Bruce et al. ch. 4, §*Regression Diagnostics*, which is Wednesday's reading. The
  notebook's worked example fits a regression of the kind Monday's reading describes, and the
  diagnostics section is about how far to trust it.
- Plot `bot_index` against `date` and look at the whole series before fitting anything.
- Consider what "normal" traffic would have been on those four days, and how you would estimate
  it from the rest of the file.

## Schedule for Wednesday

| Time | What |
|---|---|
| 0:15–0:23 | Silent and individual. You take a position and write it down |
| 0:23–0:50 | Your team argues, converges on one option, and submits |
| 0:50–1:15 | Every team reveals at once, and several are asked to defend |

Your team submits a piece of code with its justification, and the two are graded together. The
code fits a regression and reports the baseline it predicts, with a prediction interval, and the
notebook gives you a worked example to start from.

## Notebook and submission

**The notebook** goes up before class, so run `uv run update.py` from inside the course
folder when you arrive; it pulls the notebook and the data into your course folder.

**The Canvas assignment**, *AE 11: How much did the strikes take offline?*, opens when class does, and one
person submits for the whole team and the mark reaches everyone. Only the Canvas submission is
graded; Sli.do draws the histogram the room looks at before anyone speaks.
