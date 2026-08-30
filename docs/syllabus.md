# SI 385 --- Data Exploration
## Fall 2026

**When:** Mondays & Wednesdays, 08:30–09:50  
**Where:** 1400 CHEM  
**Instructor:** Chris Teplovs <cteplovs@umich.edu>  Office hours Mondays & Wednesdays 10-noon, Collegian Building (333 Maynard) Room 522.  
**GSIs:** Shan Randhawa <shanmr@umich.edu> Office hours TBD  
Zach Mays <zmays@umich.edu> Office hours TBD

*Some syllabus details may be subject to change. Version 2026.08.29.1*

---

## Communication

Slack, via Canvas, is the best way to get a question answered. We aim to respond
within about 48 hours; your peers are usually faster. Weekends and holidays will be
slower.

---

## Course description

SI 385 is about deciding what data means.

SI 345 was about getting the data into a workable shape. This
course is about what happens next: describing a dataset accurately, detecting structure,
forming a testable hypothesis ,testing it correctly, building a model when appropriate, and knowing when an apparent pattern is just an artifact of what you did.

Exploratory data analysis is the sensemaking that precedes every confirmatory
analysis. It's often helpful to get a feel for what is going on before deciding what
further analysis is even appropriate. Visualization features heavily, not necessarily as a
production skill but as a form of evidence.

Where possible, we work with real data because that is where the interesting
judgement calls live.

### Where this course fits

SI 345 (Data Manipulation) is the prerequisite and covers pandas, plotting,
regular expressions, SQL, data formats, and scaling. This course assumes (well, hopes) you remember most of it.

Both feed SI 485, the capstone.

> **A note for students who took SI 345 with a different instructor.** The two
> sections covered different ground in places. Session 2 is an explicit bridge, and we
> recommend you build your team to capitalize on those differences.  At the same time,
> we recognize that most of you are seniors and some of you have formed durable 
> teams and friendships over the past few years.  We are not looking to break those up.


---

## Learning objectives

**Competency**

- Apply the tools of EDA to unfamiliar data: maximise insight, uncover structure,
  identify important variables, detect outliers and anomalies, test underlying
  assumptions, and develop parsimonious models
- Compute and interpret summary statistics
- Choose and correctly execute an appropriate statistical test, and interpret the
  result without overstating it
- Use clustering and dimension reduction to explore unlabelled data, and evaluate
  whether the result is meaningful
- Build, tune, and honestly evaluate classification and regression models
- Defend an analytical decision to peers, including the alternatives you rejected

**Literacy**

- Basic concepts and design principles of information visualization as evidence
- Analysis techniques for time-series, multidimensional, and text data
- The exploratory/confirmatory distinction and why the order of operations matters

**Awareness**

- Python modules for complex data types --- networks, embeddings, images
- Advanced visualization techniques
- What large language models can and cannot reliably do in an analytical workflow

---

## How this course runs: Team-Based Learning

This course does not work like a normal lecture course, and the difference is not
cosmetic. Please read this section carefully.

We are about 150 people in a room with fixed seats and 80 minutes twice a week. Passive
lecture is the worst possible use of that. Instead we will use **Team-Based Learning**, a
structure designed for exactly this type of situation.

### Permanent teams

You will form a team of **four** in the second session and stay in it all term. Teams are
self-selected. 

Once formed, teams stay together. It takes weeks for a group to become good at discussing and arguing
productively, and that interface is where most of the learning in this course happens.

Sit with your team. A sloped hall works best when four people are already adjacent.

### The Readiness Assurance Process

1. **Individual Readiness Assurance Test (iRAT)** --- 5 questions on the assigned
   reading, **taken on Canvas before class**:

   | For a class on | The quiz opens | and is due |
   |---|---|---|
   | Monday | Friday 09:50 | **Sunday 20:59** |
   | Wednesday | Monday 09:50 | **Tuesday 20:59** |

   Once you start it you have **five minutes**, so read first and then open it. One
   attempt. Closed book.
2. **Clarification** --- the first fifteen minutes of class. I come in already knowing
   which items the room got wrong, and we spend some time on those. Depending on the exact results, we might re-poll live on the ones that split the room: vote, argue, vote again.

There is no team version of the RAT. The reading is checked individually; the arguing
happens in the application exercise, where it is about application rather than recall.

**Why it's on Canvas.** Some of you have accommodations for extended time or for a
distraction-reduced environment, and a 140-person lecture hall at 08:30 cannot provide
the second one by any arrangement. Canvas can, natively and invisibly. It also means I
walk in already knowing what the room found hard, which is a better use of the first
fifteen minutes than finding out live.

**If you have an accommodation letter** with items relevant to this course, please reach out to me to ensure we have everything set up correctly in Canvas.

**Appeals.** If your team believes an item was ambiguous, or that the reading supports
an answer marked wrong, you may appeal in writing before you leave the room on the day
we discuss it, citing the reading. Appeals are a **team** action --- one per team, agreed
by the team ---  and a successful appeal restores credit to every member of the appealing
team. Individuals may not appeal alone.

The reading is not optional and there are no videos. In summary: you prepare
before class, and in exchange class time is spent on the interesting part instead of
on me reading slides at you.

### Application exercises

The bulk of each session (roughly 35 minutes) is one substantial problem worked in
marimo with your team, followed by a **simultaneous report**.

**The dataset and the question go up at least two days before class**, and usually a good
deal earlier than that. You are not expected to have solved anything --- but if you think better with time and quiet than under pressure in a loud
room, that time is yours and you should take it. The specific options you choose between
are not released until we are in the room.

**The first eight minutes are silent.** Read the problem, work out what *you* think, and
write it down before anyone says anything.
Why? Because a team that starts by talking converges on whatever its fastest, loudest, or most commandeering
speaker said first, which is a worse answer than the one it would have reached and a much
worse argument. Committing privately before you negotiate is the same reason all 35 teams
reveal at once.

Your team submits two things at the reveal: a **choice** --- one of a small number of
fixed options --- and a short **written justification**. All 35 teams commit before
anyone sees anyone else's answer, and then the whole distribution goes up on screen at
once. Where the room splits is the point.

My plan is to call on a few teams to defend: one from the majority, one from the largest
minority, and one from whatever wonderfully weird outliers occur on that day. The
selection is not random and I will tell you why I picked you. Over the term every team
defends two or three times (we keep the tally).

**I call on teams, not people.** Your team decides who speaks for it and can decide
differently every time. Nobody gets put on the spot alone in front of 140 people.

**How this is graded.** Six points for a committed choice with a real justification,
submitted before the reveal. Your submission also names which team members are present;
that costs nothing and is not graded, but see the peer evaluation section. That is the
whole rubric. The quality of your reasoning is
assessed in the room, out loud, by the people who chose differently --- which is a better
instrument than anything I could write in a margin, and it is the reason the exercise is worth
attending rather than worth submitting.

Problems are chosen so that reasonable teams will disagree. Is this outlier real or
an artifact? Does this violate the model's assumptions badly enough to matter? Which
of these two clusterings is more honest? When the room splits, we have found
something worth talking about.

---

## Assessment

A total of **1000 points**:

| Component | Points | Basis |
|---|---:|---|
| iRATs --- best 18 of 20 @ 15 | 270 | Individual |
| Application exercises --- best 20 of 23 @ 6 | 120 | Team |
| Demonstrations of Understanding --- 3 @ 120 | 360 | Individual |
| Team project --- final report 180 (proposal required, ungraded) | 180 | Team |
| Peer evaluation --- 2 @ 35 | 70 | Individual |
| **Total** | **1000** | |

Individual work is 63% of your grade, team work 30%, peer evaluation 7%. Your grade
is mostly yours.

**The iRAT is worth 15 points, which is more than it looks.** A small number of straight-forward questions twice a week.  That's 27% of the course riding on whether you did the
reading. It is the single highest-leverage habit in this class, and the two dropped
scores below are there precisely because the stakes per session are real.

**Best-of counts are your absence policy.** You may miss two RAT sessions and three
application exercises with no penalty and no explanation required. Oversleeping,
illness, a bad morning, an interview --- all absorbed. In exchange, RATs and
application exercises cannot be made up under any circumstances, because they only
exist in the room. Do not email us asking to make one up.  If you find yourself missing class or falling behind please reach out to the teaching team; we have access to resources that can help you.

**Team project:** proposal required but ungraded, the final report is worth 180 points.

### Demonstrations of Understanding

Three times this term you will submit a Demonstration of Understanding (DoU). If you took SI 345 with me, you have
done these before. They are an evolution of what we did. If you haven't encountered these before, here is
the general idea:

Anyone can produce code that runs. Current AI technology is particularly good at producing code.  What we want evidence of is that *you* made the
analytical decisions and can defend them.

Each DoU has two parts:

1. **The analysis** (40 pts) --- a marimo notebook answering a substantive question
   about data you haven't seen before, drawing on the previous few weeks.
2. **A decision memo, target length 400 words** (80 pts) --- and _not_ a walkthrough of your
   code. It should consist of three blocks:

   | Block | Roughly | Points |
   |---|---:|---:|
   | The single analytical decision you would defend | 150 words | 30 |
   | The alternative you rejected, and why you rejected it | 150 words | 30 |
   | What you are still unsure about in your own analysis | 100 words | 20 |

   **Every claim must be anchored** --- cite the cell where you made the choice and quote
   the actual numbers your notebook produced. An assertion with nothing behind it earns
   nothing, however well written.

   Memos over 450 words will be returned ungraded.

   The last block is the one people get wrong by trying to look competent. Write it
   honestly, not defensively: it is the one place in this course where admitting you do
   not know something earns points rather than costing them.  It also helps you track where you struggle, when breakthroughs happen, and data on which to reflect.

The word cap is deliberate and it is the part people underestimate. Picking which
decision matters most, and cutting everything else, is itself the skill being assessed.
Four hundred words is not many. You will want a fifth block and you cannot have one.

The anchoring requirement is the other half of that. A memo that names a cell and quotes
a number is making a claim about *your* notebook that can be checked in seconds. A memo
that could have been written about anybody's analysis is, as far as this course is
concerned, about nobody's.

### Team project

The team project is the main integrative work of the course. Your team will choose a
dataset, frame a substantial analytical question, and carry it from raw data through EDA,
inference or modelling, and a written conclusion --- all in a single marimo notebook.

**What to build.** A marimo notebook that runs top to bottom, plus a written report
integrated into it as markdown cells (~1500 words across the report sections). The
notebook is the submission. There is no separate document.

**Dataset.** Any dataset not used in course materials. A curated list of starting
points will be provided on Canvas; you are not limited to it. Data about people is encouraged: it's
where the interesting judgement calls live.

**Required sections:**

1. **Question and context** --- what you are trying to find out, and why it matters
2. **EDA** --- describe the data honestly before you model it; show the distributions,
   the missing values, the things that surprised you
3. **Analysis** --- at least one inferential or model-based analysis; the method must
   match what the data and question can support
4. **Limitations** --- what you cannot conclude, and why; what you would do with more
   time or better data
5. **One decision defended** --- the single analytical choice your team would stand
   behind in front of the room, and the alternative you rejected; written in the same
   voice as a DoU

**Proposal** (required, ungraded, due Oct 14): one page in a marimo notebook --- your
question, your dataset, why it's interesting, and a plan for the division of labour specification that describes what each team member will contribute. A
proposal that gets feedback is more useful than one that gets a grade, so it doesn't
get a grade. It does get read, and it is not optional.

**Final report** (180 pts, due Dec 11): the completed notebook, submitted on Canvas.
It must run top to bottom from a clean kernel. Rubric: question clarity and scope
(20), EDA quality and honesty (45), analytical depth and correctness (55), limitations
(30), decision defended (30).

### Peer evaluation

Twice a term you will assess your teammates' contributions --- once at midterm, once
at the end. You get the 35 points for completing the evaluation thoughtfully, not for
the ratings you receive.

**How you rate.** You have **30 points to distribute among your three teammates**. You
do not rate yourself. The average is therefore 10, and here is the part that matters:
**you may not give all three the same number.** At least one teammate must get more than
10 and at least one must get less than 10. An evaluation that splits 10/10/10 is not a
valid submission and earns none of the 35 points.

This is deliberate and it is uncomfortable on purpose. Rating everyone identically is
the path of least resistance, and a peer evaluation where everyone does it carries no
information at all --- which means it cannot protect the people it exists to protect. You
are not being asked to punish anyone. You are being asked to say who did the most.

**What the ratings do.** The average rating you *receive* adjusts your share of the
180 project points:

| Mean rating received | Multiplier | Effect on 180 pts |
|---:|---:|---:|
| 12.0 and above | 1.10 | +18 |
| 10.5 – 11.9 | 1.05 | +9 |
| 8.5 – 10.4 | 1.00 | --- |
| 7.0 – 8.4 | 0.90 | −18 |
| below 7.0 | 0.80 | −36 |

Note how wide that middle band is. Ordinary differences --- someone did a bit more, someone
a bit less --- land everybody at 1.00, which is the intended result. To fall below it, all
three of your teammates have to say the same thing about you independently. One
teammate's low opinion cannot move your grade but a consensus can.

The multiplier applies to the project only, not to application exercise points. An AE is
80 minutes in a room, and either you were there or the best-of-20-of-23 count already
handled it. The project runs six weeks and is where a teammate can genuinely leave the
work to everyone else.

Midterm evaluations are formative and shared back to you; only the final round affects
the multiplier, so there is time to change how you show up.

### Grade mapping

| Points | Grade | | Points | Grade |
|---:|---|---|---:|---|
| 970 | A+ | | 730 | C |
| 930 | A | | 700 | C− |
| 900 | A− | | 665 | D+ |
| 865 | B+ | | 630 | D |
| 830 | B | | 600 | D− |
| 800 | B− | | <600 | E |
| 765 | C+ | | | |

---

## Software

We use **marimo** notebooks, not Jupyter.

Marimo is reactive: change a cell and everything depending on it re-runs. There is no
hidden state and no "did I run that cell?" A marimo notebook is a plain `.py` file,
so it diffs, versions, and reviews like real code.

This matters more than it sounds. A large share of the debugging pain in a notebook
course is stale state: output on screen that no longer matches the code that
produced it. Marimo makes that category of bug impossible.

One rule will bite you early: **a variable can be defined in only one cell.** You
cannot redefine `df` eight times down the notebook. Prefix a name with `_` to make it
cell-local, or give it a real name. This is annoying for about a week and then it
quietly makes you a better programmer.

Session 2 covers setup. If your machine fights you, use **molab**
(<https://molab.marimo.io>) --- marimo's free cloud sandbox. It requires no installation and runs in a
browser tab. You will not be locked out of an application exercise over an
environment problem.

**One optional extension, for the curious.** If you already pay for an AI coding agent,
there is a tool called [marimo-pair](https://github.com/marimo-team/marimo-pair) that
connects it to a *running* notebook instead of a static copy of the file, so it can
inspect your actual dataframe and run a cell rather than guessing from the source. It is
a genuinely different way to work with an agent and some of you will find it interesting.

It is not part of this course. We will not teach it, nothing is graded on it, and it
requires a subscription this course is not going to ask you to buy. We will encourage you to experiment with using it if you have the capacity to do so.

## Readings

Through the U-M O'Reilly portal:
<https://www.lib.umich.edu/announcements/oreilly-safari-books-online>

- Bruce, Bruce & Gedeck, *AI-Assisted Statistics for Data Scientists*, 3rd ed.
- Géron, *Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow*
- Grus, *Data Science from Scratch*, 2nd ed.
- VanderPlas, *Python Data Science Handbook*
- Shasha & Wilson, *Statistics is Easy*
- McKinney, *Python for Data Analysis* --- reference only
- Wickham, Çetinkaya-Rundel & Grolemund, *R for Data Science*, 2nd ed. --- one short
  excerpt in session 2; also free at <https://r4ds.hadley.nz>

See the Schedule of Topics and Readings. Readings are due **before** the session
listed, and the iRAT is based on them.

---

## Attendance

Attendance is effectively mandatory, and mostly not because of points.

The part that actually matters is your team. Four people carrying a problem is a
discussion, three is a strain, two is a slog --- and **every AE submission names who was
there**. That list is not graded; it is simply visible to the three people who will
distribute peer-evaluation points at the end of term, and who will have done your share
of the work in the meantime.

The best-of counts exist so that missing occasionally costs you nothing. Repeatedly missing class will cost you, and your teammates will be the ones who say so.

## Late policy

Three (3) free late days for DoUs, in whole 24-hour blocks, no explanation needed. We
track them. After they are used: 25% deduction per 24-hour period.

Late days may not be applied to the final report.
They cannot be applied to RATs or application exercises, which do not have deadlines
in the usual sense.

---

## Getting and giving help

Learning technical material is hard and we move quickly. Get help from anyone you
like. You are still responsible for learning the material, and if you take on so much
help that you never build the skill, it will find you out in the end.

Your DoU submission must be your own work in your own voice. If you received
substantial assistance, say so in a comment. Excerpts from others must be quoted and
cited.

If you are further along and willing to help classmates, please do but with the goal of
teaching, not of transferring an answer. Short code fragments on Slack are fine;
complete solutions are not. Solutions from previous semesters are never allowed.

Search the web. Read Stack Overflow. Tell us where you found something; even a
partial solution that shows the right instincts earns credit.

### Generative AI

You may use generative AI in this course, and you should learn to use it well. We spend a
session on where LLMs help and where they fabricate, and **agents are permitted during
in-class application exercises.** Let me explain the reasoning rather than just the
rule.

An agent can compute a silhouette score (you'll know what that is by the time you complete the course), fit a model, and produce a chart faster than
you can. Tha's fine and that is not what you are being graded on. Application exercises are
written so that the computation is the easy part and the *judgement* is the problem:
whether this outlier is real, whether this assumption is violated badly enough to
matter, which of two defensible answers you will commit to in front of the room. An
agent will give you an answer to any of those with total confidence and no basis. You
still have to decide, and then defend it out loud to people who chose differently.

If you find an agent is doing an application exercise for you, tell me. It means I
wrote a bad exercise and I would like to know.

Two limits hold everywhere. The DoU memo has to be anchored in your own notebook --
specific cells, actual numbers --- and a model that did not do your analysis cannot supply
those, so prose that floats free of your own output will look remarkably out of place. And the
final block must be yours: it is a record of your own uncertainty, and outsourcing it
defeats the only purpose it has. I will say plainly that neither of these is airtight; nor are they meant to be. The reason to write your own memo is that the alternative is
arriving in November unable to do the thing this degree says you can do.

RATs are done on your own. I suggest that you try them closed-book and without AI help.  I also recognize that that is neither realistic nor enforceable, but we're going to run with it nonetheless.  Think of this as a request rather than a directive.

Here is why I think you should honour it anyway. The five-minute limit is doing most of
the work: at sixty seconds an item, looking something up in a reading you haven't done is
slow, because you don't know where to look. It rescues someone who read the chapter and
forgot a detail but it does almost nothing for someone who didn't read it.

What it does reliably is tell me the room understood something it didn't. I build the
next morning's clarification out of your answers. If they are not yours, I spend fifteen
minutes on the wrong thing and you spend thirty-five on an application exercise you
aren't equipped for. The iRAT is diagnostic before it is a grade, and it is the only
instrument in this course that tells me what to teach. Lying to it mostly wastes your own
eighty minutes.

---

## Academic integrity

### Collaboration

UMSI strongly encourages collaboration. Active learning works. Collaboration is
especially valuable in summarising readings and identifying key concepts. You must,
however, write your own submissions in your own words, and list your collaborators.
If you are in doubt, please ask.

### Plagiarism

All written submissions must be your own original work, not paraphrases of someone
else's answer. You may incorporate excerpts from other authors if clearly marked as
quotations and attributed. If you build on others' ideas or code, cite them. You may
get copy-editing help and discuss ideas, but the substantive writing, code, and ideas
must be yours or explicitly attributed.

See the BSI student handbook on the UMSI Current Students page for the definition of
plagiarism and the consequences.

---

## Accommodations for students with disabilities

The University of Michigan recognises disability as an integral part of diversity and
is committed to an inclusive and equitable educational environment. Students
experiencing a disability-related barrier should contact Services for Students with
Disabilities (<https://ssd.umich.edu/>; 734-763-3000; ssdoffice@umich.edu). Students
connected with SSD can make accommodation requests in Accommodate.

**Please come talk to me in the first two weeks if any part of how this course runs
interacts with an accommodation.**  The application exercise in particular is 35 minutes of thirty-five teams
talking at once in a hard-surfaced hall, and I am aware that for some of you that is a
barrier the room itself creates and that no general policy of mine fixes. What works
differs enough person to person that the honest approach is to build something with you
rather than to announce something at you --- so bring me the problem, even if you do not
have a solution in mind, and even if you are not sure it counts.

There _are_ some things we can adjust: where your team sits, how your team deliberates, what you can
do with the material in advance, and who speaks for your team when it is called on.

## Student mental health and wellbeing

The University offers services through Counseling and Psychological Services (CAPS,
<https://caps.umich.edu/>, 734-764-8312) and University Health Service
(<https://uhs.umich.edu/mentalhealthsvcs>, 734-764-8320). An 8:30am course in your
final years is a lot; if things are going badly, tell someone early.

## Class recordings

Lecture sessions may be audio and video recorded so that students who cannot attend
can access the content. Recordings are posted on Canvas for registered students only
and are not public. As part of your participation you may be recorded; if you do not
wish to be, contact me in the first week. Students may not share or re-upload these
recordings (a FERPA violation). Personal recordings are prohibited without written
permission except as part of an approved accommodation.
