# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.24.0",
#     "pandas==3.0.5",
#     "matplotlib==3.11.1",
# ]
# ///
#
# Dependencies are declared here as well as in pyproject.toml, so this file also
# runs on its own, outside the course folder:
#
#     uvx marimo edit --sandbox <this file>
#
# `uv run marimo edit --no-sandbox <this file>` from inside the course folder
# remains the documented way to work. The --no-sandbox flag matters: marimo sees
# this header and, in an interactive terminal, stops to ask whether to build an
# isolated environment from it, which is not a question to put to 140 students on
# lecture-hall wifi. The flag answers it in advance. The sandbox line above is the
# fallback for a file that has been moved, renamed, or opened months later.
#
# Versions are pinned EXACTLY to uv.lock on purpose: marimo rewrites loose
# specifiers in place on the first sandbox run, and exact pins make that a no-op
# so the file does not mutate under whoever opens it first. If you change
# pyproject.toml, re-pin these to match.

import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import re
    from collections import Counter
    from pathlib import Path

    import pandas as pd
    import matplotlib.pyplot as plt

    REMOTE = ("https://raw.githubusercontent.com/"
              "cteplovs/si385-fa2026-student/main/data/")

    def course_data(name):
        """Read one of the course CSVs.

        The copy in the course folder is the one to prefer, and it is what you get
        if you are running this the documented way.  The fallback to the public
        repository is there so that the notebook also runs on molab, where there is
        no course folder for it to sit next to, provided you have a network.
        """
        try:
            local = Path(__file__).resolve().parents[2] / "data" / name
            if local.exists():
                return pd.read_csv(local)
        except (NameError, IndexError, OSError):
            pass
        return pd.read_csv(REMOTE + name)

    return Counter, course_data, mo, plt, re


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # SI 385 — Data Exploration

    ## Session 2: marimo, and the first dataset

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, September 2, 2026

    **Reading due today:** marimo *Getting Started*; *R for Data Science* 2e §10.1–10.2

    ---

    ### Today you will be able to

    - Explain what makes a marimo notebook different from a Jupyter notebook, and read
      the dependency graph off the code in front of you
    - Leave with a working environment, either a local install or molab, that you will
      use for the rest of the term
    - Defend a cleaning decision that changes the answer, which is the first real thing
      this course asks of you
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---
    ## Where this session goes

    | Time | Block |
    |---|---|
    | 0:00–0:12 | The practice quiz, and what it did and did not tell me |
    | 0:12–0:20 | Form your team |
    | 0:20–0:42 | Get marimo running, and break it on purpose |
    | 0:42–1:04 | Rebuild Monday's word cloud, and commit to an answer |
    | 1:04–1:14 | What the switches were doing, and why the chart redrew itself |
    | 1:14–1:18 | The number that would not sit still |
    | 1:18–1:20 | Before September 9 |

    Nothing today is graded.  The middle of the hour is a dry run of an application
    exercise, built to the same shape session 3 uses for real, in which you take a
    position on your own before your team has to converge on a single answer, and every
    team then reveals at the same moment.  Doing that once with nothing at stake is
    considerably better than meeting the format for the first time when it counts.

    What you are supposed to walk out with is a working environment and a slightly
    uncomfortable feeling about how much of an answer is decided before anybody looks at
    a chart.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 1. The practice quiz

    One hundred and fifteen of you took it, out of the hundred and forty of us in here.
    It was ungraded and optional and it went up at nine fifty on Monday morning, so that
    is a better turnout than I had any right to expect, and it means the results are
    worth taking seriously.  I will come back at the end of the hour to what they can and
    cannot support.

    The straightforwardly useful part comes first, which is how the five items actually
    did.
    """)
    return


@app.cell
def _(course_data):
    rat = course_data("si385_practice_rat_2026.csv")
    rat
    return (rat,)


@app.cell(hide_code=True)
def _(plt, rat):
    _order = rat.sort_values("correct_ratio")
    _colours = ["#B8860B" if _r < 0.7 else "#00274C" for _r in _order["correct_ratio"]]

    _fig, _ax = plt.subplots(figsize=(9, 3.2))
    _ax.barh(_order["item"], _order["correct_ratio"], color=_colours)
    _ax.set_xlim(0, 1)
    _ax.set_xlabel("proportion correct")
    _ax.axvline(0.7, color="grey", linestyle=":", linewidth=1)
    for _y, _v in enumerate(_order["correct_ratio"]):
        _ax.text(_v + 0.01, _y, f"{_v:.0%}", va="center", fontsize=9)
    plt.tight_layout()
    _fig
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Four of the five items came back somewhere between seventy-seven and eighty-six
    percent correct, which is roughly what a readiness check is supposed to look like,
    and I am not going to spend class time on any of them.

    The one I do want to spend time on is question 2, the item asking why marimo refuses
    to let two cells define the same variable, which came back at fifty-eight percent.
    What makes it worth the detour is not the headline number but the way it splits: all
    forty-seven people in the top third got it, eighteen of the forty-eight in the middle
    got it, and two of the twenty in the bottom third got it, which is a much sharper
    separation than any other item on the quiz managed to produce.

    An item that behaves like that is usually not testing recall.  It is testing whether
    you have a working picture of what the tool is doing, and the reason I care is that
    the rest of today depends on having one.  So rather than tell you the answer, we are
    going to spend the middle of the hour in a notebook where the restriction actually
    bites, and I will ask you again at the end.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 2. Form your team

    Teams are four people and they are fixed for the term.  You have about eight minutes.

    I said on Monday that I would post the diagnostic results so you could pick teammates
    who cover your gaps.  I am not going to do that, for two reasons.  The first is
    logistical, which is that I, in a valiant but misguided attempt to be tidy, deleted
    the wrong polls right before coming to lecture, and the diagnostic results were never
    recorded because the polls didn't exist.  The second is that having thought about it
    since, I do not think the loss is worth
    mourning.  When I asked for hands in the room on Monday, the honest picture was that
    quite a lot of the SI 345 material has faded for nearly everybody, including the
    people who took it from me.  A ranked skills map would have been a map of who
    remembered what in August, which is not a durable fact about anyone and not a good
    basis for a term-long commitment.

    So I suggest you pick on the things that are more likely to predict whether a team
    survives October:

    - **Can you be in the same room outside class when you need to be?**  The project
      lands in November and this is the constraint that bites hardest.
    - **Do you want to be in a group with someone who will tell you that you are wrong?**
      You do.  Choose accordingly.
    - **Are you all planning to sit together?**  In a sloped hall with bolted seats, a
      team that scatters cannot argue, and productive discussion and argument is the
      entire method.

    Mixing the two SI 345 sections is still a good idea and is still only a suggestion.

    **Once you have four people:** one of you registers the group in Canvas under
    *People -> Groups*, and the other three join it.  Please do that now rather than
    tonight.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 3. Get marimo running

    You were asked to do this before today.  If it worked, this block is short for you
    and I would like you to spend the spare minutes helping whoever is sitting near you
    who could use a hand.  If it did not work, this is the block where we fix it, and
    there is no penalty of any kind for being in that group.

    ### The install

    ```bash
    # from inside the course folder
    uv sync
    uv run marimo edit --no-sandbox notebooks/lectures/L02_wordcloud_reactivity.py
    ```

    A browser tab should open with this notebook in it.

    ### If it fights you

    Work down this list and stop at the first one that gets you a running notebook.

    1. `uv --version` returns nothing, so uv is not installed.  Follow the setup guide on
       Canvas, which has the one-line installer for macOS and for Windows.
    2. It runs but cannot find the data file later on.  You are almost certainly running
       from the wrong directory, so check that `ls` shows a `data` folder next to a
       `notebooks` folder.
    3. Something deeper is broken and you have burned five minutes on it.  Stop, and go
       to **<https://molab.marimo.io>**, which is marimo's free hosted sandbox.  It
       requires no install and it runs the same notebooks, and this one will pull its
       data over the network when it cannot find a course folder.  This is a
       legitimate way to take the course and not a consolation prize.

    Please seek out a GSI rather than sitting quietly with a broken laptop, since we
    would much rather find you now than in week six.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 4. Monday's word cloud

    When you walked in on Monday I asked you, in one word, what exploring a dataset means
    to you, and one hundred and eight of you answered.  Sli.do drew a picture of those
    answers and put **Understanding** at the middle of it, and we all looked at it for
    thirty seconds and moved on.

    That picture was the output of a small pile of decisions that Sli.do made silently on
    your behalf.  We are going to make them ourselves instead, one at a time, and watch
    what happens to the answer.

    Consider the raw material that picture was drawn from.
    """)
    return


@app.cell
def _(course_data):
    cloud = course_data("si385_wordcloud_2026.csv")
    cloud
    return (cloud,)


@app.cell(hide_code=True)
def _(cloud, mo):
    _n = len(cloud)
    _multi = (cloud["response"].str.strip().str.split().str.len() > 1).sum()
    _spaces = (cloud["response"] != cloud["response"].str.strip()).sum()
    _caps = (cloud["response"].str.strip() != cloud["response"].str.strip().str.lower()).sum()

    mo.md(f"""
    Before touching any of it, consider four facts about what is already in there:

    - **{_n}** responses.
    - **{_multi}** of them are not one word, because I asked for one word and a quarter of
      you wrote a sentence, which is what always happens and is nobody's fault.
    - **{_spaces}** of them have a leading or trailing space that you cannot see.
    - **{_caps}** of them are not all lowercase.

    None of that is dirt to be scrubbed off before the real work starts.  Every one of
    those four facts is a decision waiting for somebody to make it, and the person who
    makes it is deciding what the answer will be.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### The pipeline

    Consider the following three cells.  The first two are lists that somebody had to
    write down by hand, and the third is the thing that turns one hundred and eight
    responses into a pile of terms to count.  Please read them properly, because in a few
    minutes I am going to ask you to defend one of the choices in them.
    """)
    return


@app.cell
def _():
    # The stopword list was written by hand and is open to argument.  Note that "data"
    # and "dataset" are in it because they are echoes of the question I asked rather than
    # anything you chose to say, which is a judgement call you are allowed to disagree with.
    STOPWORDS = {
        "the", "to", "a", "of", "and", "in", "it", "is", "for", "that", "with", "on",
        "at", "what", "you", "your", "its", "are", "or", "from", "by", "this", "be",
        "as", "an", "i", "my", "out", "all", "up", "any", "get", "different",
        "data", "dataset",
    }

    # A crude suffix stemmer.  Real ones are considerably more careful, and this one is
    # here so that you can read the rule itself rather than take it on trust.
    SUFFIXES = ("ization", "izing", "ional", "ing", "ion", "ies", "ed", "es", "s", "e")
    return STOPWORDS, SUFFIXES


@app.cell
def _(SUFFIXES):
    def stem(word):
        for suffix in SUFFIXES:
            if word.endswith(suffix) and len(word) - len(suffix) >= 4:
                return word[: -len(suffix)]
        return word

    return (stem,)


@app.cell
def _(
    Counter,
    STOPWORDS,
    cloud,
    collapse,
    drop_stop,
    lower,
    merge_analy,
    re,
    split_words,
    stem,
    trim,
):
    def to_terms(raw):
        text = raw.strip() if trim.value else raw
        text = text.lower() if lower.value else text
        pieces = re.findall(r"[A-Za-z']+", text) if split_words.value else [text]

        kept = []
        for piece in pieces:
            if drop_stop.value and piece.lower() in STOPWORDS:
                continue
            if merge_analy.value and re.match(r"analy[sz]", piece.lower()):
                piece = "analy..."
            elif collapse.value:
                piece = stem(piece)
            if piece:
                kept.append(piece)
        return kept

    counts = Counter(term for raw in cloud["response"] for term in to_terms(raw))
    return (counts,)


@app.cell
def _(mo):
    # Defined here, but drawn in the cell below so that they sit directly above the
    # chart they control.  A marimo UI element can be created in one cell and rendered
    # in another, and it stays the same element either way.
    trim = mo.ui.switch(value=False, label="Trim invisible leading and trailing spaces")
    lower = mo.ui.switch(value=False, label="Lowercase everything")
    split_words = mo.ui.switch(value=False, label="Split the sentences into separate words")
    drop_stop = mo.ui.switch(value=False, label="Drop common English words")
    collapse = mo.ui.switch(value=False, label="Collapse word forms with a suffix rule")
    merge_analy = mo.ui.switch(value=False, label="Merge the analy... family by hand")
    top_n = mo.ui.slider(3, 15, value=8, label="Terms to show")
    return collapse, drop_stop, lower, merge_analy, split_words, top_n, trim


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Stage 1, on your own, eight minutes

    This part is silent and it is yours alone.  Your team is about to have to agree on
    something, and that argument is worthless if you arrive at it without a view.

    Each switch is one decision.  Please turn them on roughly in order, from the top of
    the left column to the bottom of the right, and watch which term is on top of the
    chart as you go.  Then read the two sections underneath the chart, and write down,
    on paper, which version of this chart you would be willing to stand behind.  You do
    not have to be able to justify it yet.
    """)
    return


@app.cell(hide_code=True)
def _(
    collapse,
    counts,
    drop_stop,
    lower,
    merge_analy,
    mo,
    plt,
    split_words,
    top_n,
    trim,
):
    _top = counts.most_common(top_n.value)[::-1]
    _values = [_c for _t, _c in _top]

    _fig, _ax = plt.subplots(figsize=(9, 0.4 * len(_top) + 1.0))
    _ax.barh([_t for _t, _c in _top], _values, color="#00274C")
    _ax.set_xlabel("times said")
    _ax.set_title(f"{len(counts)} distinct terms from 108 responses")
    for _y, _v in enumerate(_values):
        _ax.text(_v + 0.12, _y, str(_v), va="center", fontsize=9)
    plt.tight_layout()

    _ranked = counts.most_common(3)
    _verdict = (
        "a tie at the top, which is its own kind of answer"
        if _ranked[0][1] == _ranked[1][1]
        else f"**{_ranked[0][0]}**, ahead of {_ranked[1][0]} "
             f"by {_ranked[0][1] - _ranked[1][1]}"
    )

    mo.vstack(
        [
            mo.hstack(
                [
                    mo.vstack([trim, lower, split_words], gap=0.3),
                    mo.vstack([drop_stop, collapse, merge_analy], gap=0.3),
                ],
                widths="equal",
                gap=1.5,
            ),
            top_n,
            mo.callout(mo.md(f"Top of the chart right now: {_verdict}."), kind="info"),
            mo.as_html(_fig),
        ],
        gap=0.5,
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### What the switches did

    Turning them on in order gives you this sequence, and it is worth writing the winners
    down because the point is the sequence rather than any one of them.

    | Switches on | Distinct terms | Top of the chart |
    |---|---|---|
    | none, which is roughly what Sli.do did | 89 | Understanding, 5 |
    | trim | 84 | Understanding, 6 |
    | trim, lowercase | 75 | analyzing, 9 |
    | trim, lowercase, split | 143 | **the**, 16 |
    | trim, lowercase, split, stopwords | 120 | analyzing and understanding tie at 10 |
    | all five | 113 | understand, 11 |
    | all six | 111 | analy..., 18 |

    Four different words have been at the top of that chart, and I would defend every one
    of the seven rows to a colleague.  Nothing in the sequence is a mistake being
    corrected.  Row four is the closest thing to a bad answer and even it is only bad
    because I know what the question was for; a stopword list is a judgement about
    relevance and not a fact about English.

    The row I want to draw your attention to is the fifth, where two terms tie at ten.
    Sli.do's version of this chart had **Understanding** at five, and it looked like a
    finding.  What it actually was, was one of several possible findings, chosen for you
    by a tool that never mentioned it had chosen.

    ### Where the suffix rule gives up

    Look at what the suffix rule does in row six.  It merges *analyzing* into *analyz*
    and it merges *analysis* into *analysi*, and those two are still sitting in the chart
    as separate terms, ten and seven, when everybody in this room can see they are the
    same idea.  No automatic rule fixes that, because the difference is a spelling
    difference rather than a suffix difference, and the only way to merge them is for a
    person to decide that they mean the same thing here.  Some of you may recall a
    technique called *lemmatization*, which instead of chopping letters off the end of a
    word looks the word up in a vocabulary and hands back the dictionary headword, so
    that *analyzing* comes back as *analyze* rather than as *analyz*.  Rather than bring
    in the more advanced natural language processing tools that do this, I have provided
    a crude yet functional implementation of its blunter relative, stemming, which
    applies a suffix rule and consults nothing.

    The substitution costs less than you would think, because a real lemmatizer does not
    solve this problem either.  It returns *analyze* for *analyzing* and *analysis* for
    *analysis*, one being a verb and the other a noun, and in English they really are
    two different words.  It would also have to be told which of those two *understanding*
    is before it could do anything with it, and ten of you wrote that word without
    telling anybody which one you meant.

    That decision is the last switch, and it is the one that changes the answer most.
    Turning it on takes the top term from eleven to eighteen and settles the argument
    that row five could not settle.  It is also the only switch on the list that a tool
    could not have offered you, which is a reasonable summary of what this course is
    going to keep asking you to do.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ### Stage 2, with your team, eight minutes

    On Monday I asked what exploring a dataset means to you, and one hundred and eight
    people answered.  Your team has to say what the room actually said.

    > **Which of these is the most honest answer to the question I asked?**
    >
    > **A.** *Understanding*, at five.  Every response counted exactly as it was typed,
    > which is the chart Sli.do put on the screen on Monday.
    >
    > **B.** *analyzing*, at nine.  Invisible spaces trimmed and everything lowercased,
    > with each response still counted as the single thing its author wrote.
    >
    > **C.** A tie between *analyzing* and *understanding*, at ten each.  Sentences
    > broken into their words, and the words nobody chose dropped.
    >
    > **D.** *analy...*, at eighteen.  All of the above, plus word forms collapsed and
    > the analy family merged by a person who decided they meant the same thing.

    Every team answers this same question and every team has to land on one letter.  You
    are not being asked which chart is prettiest or which pipeline is most sophisticated,
    and D is not the right answer because it has the most switches on.

    **Two things to produce, and please have both ready at 0:58.**

    - **The choice.** One letter, agreed by all four of you.  Nobody abstains, and a team
      that cannot agree still has to pick, which is a normal thing to have to do.
    - **The justification.** Three or four sentences on paper, naming the one decision
      that mattered most to your answer and the option you rejected because of it.  Write
      the number your chart actually showed rather than a general remark about cleaning.

    In session 3 the choice goes into Sli.do so the room sees the distribution before
    anyone speaks, and the justification is the only part that gets marked.  Today it is
    hands and paper, and neither is going anywhere near the gradebook.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Stage 3, all at once, six minutes

    Hands up on a count of three, every team at the same moment, one hand per team with
    the letter on your fingers.  The simultaneity is not theatre.  If teams reveal one
    after another the later ones drift towards whatever is winning, and the disagreement
    that makes this worth doing quietly disappears.

    Then I will ask two teams to defend, chosen so that they disagree, and I will
    probably pick a team whose letter is unpopular.  Being asked to defend an unpopular
    answer is not a sign that you got it wrong.

    For what it is worth, I would argue for B or C and I would take some convincing on A,
    though A has the one property none of the others have, which is that it is the only
    chart on the list that nobody in this room touched.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Why the chart redrew itself

    You just changed one switch and the chart redrew itself, and nobody pressed anything.
    That is what question 1 on the practice quiz was asking about, and it is where marimo
    and Jupyter part company.

    marimo read the code and worked out that `counts` uses `trim`, and that the chart
    uses `counts`, so touching `trim` obliges it to redo both.  It is not running the
    cells top to bottom.  It is running the ones that are downstream of what you touched,
    which is why the order of cells in the file does not have to match the order things
    happen in.

    Which brings us back to question 2, the one that split the room.

    Suppose two different cells in this notebook both defined `counts`.  You turn the
    trim switch.  marimo now has to redraw the chart, and the chart needs `counts`, and
    there are two of them.  There is no correct thing for it to do at that point.  It
    cannot pick the one that ran most recently, because in a notebook where you jump
    around there is no such thing as most recently in any sense you could rely on, and
    that ambiguity is precisely the bug you have all had in Jupyter where a notebook
    works on your machine and produces nothing on anybody else's.

    So the restriction is not marimo being fussy about style.  It is the price of the
    guarantee, and the guarantee is that what you see on screen is what the code says,
    every time, for everyone.  A notebook that cannot be in two states at once has to
    forbid the thing that would put it in two states at once.

    **Please try it.**  Add a cell containing `counts = 1` and see what marimo says, and
    then delete it again.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Question 3, which was about deleting a cell

    Rather than take this notebook apart, please build a small piece of it that you can
    afford to lose.  Add a cell containing `demo_value = 10`, and then a second cell
    containing `demo_value * 2`, which should show you 20.

    Now delete the first of those two cells.  The 20 goes the moment you do, because the
    value it was made from no longer exists anywhere in the notebook.  In Jupyter,
    `demo_value` would still be sitting in memory and that second cell would keep
    printing 20 until you restarted, at which point everything would break at once and
    you would have no idea why.

    Then delete the second cell as well, which puts the notebook back exactly as it
    started.  Deleting the cell that reads the CSV would teach the same lesson and take
    every chart in section 4 with it, which is why I would rather you practised on
    something you built yourself.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 5. The number that would not sit still

    Back to the quiz, and to the question I parked at the start of the hour.

    Here is something I did not plan.  I exported the results three times yesterday,
    because I was building this session around them and kept wanting a fresher copy.

    | when I exported | answers in | question 1 | question 2 |
    |---|---|---|---|
    | morning | 37 | 84% | 65% |
    | late afternoon | 58 | 79% | 53% |
    | after it closed | 115 | 81% | 58% |

    Had I built the session on the morning export, I would have opened today by telling
    you that eighty-four percent of you understand reactivity and that question 2 was
    sitting at sixty-five.  Both were wrong, by three points and by seven, and question 2
    did not drift gently towards its final value either, because it fell to fifty-three
    before it came back up.

    Nobody was careless at any point in that table.  Every one of those three numbers was
    computed correctly from every answer that existed when I asked for it, so the only
    thing separating the rows is the moment I chose to look.

    That is the same shape as the argument your team just had.  The word cloud gave you
    four different top terms depending on which decisions you made, and this table gives
    you three different readings of the same class depending on when the snapshot was
    taken.  In both cases the number is real and the answer is still a choice.

    One more thing worth noticing, because it is the part people walk past.  The *top
    third* and *bottom third* columns in the table at the top of this notebook are
    computed within the people who answered.  They are thirds of the hundred and fifteen
    rather than thirds of this class, and there are still about twenty-five of you who
    did not take the quiz at all.

    I am not asking you to vote on this one.  I am asking you to leave with two worked
    examples of a number that moves when somebody decides something, and with the
    knowledge that in neither case had anyone made a mistake.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## 6. Before September 9

    1. **The reading quiz for session 3 opens Monday September 7 at 09:50 and closes
       Tuesday September 8 at 20:59.**  This one counts.  Five questions, five minutes,
       one attempt, on the assigned reading.  Monday is Labour Day and we do not meet,
       so the quiz opens on a day you are not in a classroom and there are nine days
       between now and the next time we are in a room together.
    2. **Watch for the pre-read for application exercise 1**, which goes up on Canvas by
       Friday.  It gives you the dataset and the question and deliberately does not give
       you the options.
    3. **If your environment is still broken, deal with it this week rather than next.**
       Ask on Slack, or commit to molab and stop fighting the install.  Slack reaches
       all three of us, and there are GSI office hours before we meet again, with Shan on
       Thursdays from 2 to 3 and Zach on Sundays from 7 to 8.  Session 3 has an
       application exercise and your team will submit an answer from a notebook.
    4. **Please sit with your team on Wednesday September 9.**

    One last thing about today:  You spent twenty minutes on a chart of
    your own words, the answer changed four times depending on decisions any of you could
    defend, and your team still had to pick one of them.  That is not a quirk of text
    data.  It is what the next thirteen weeks are about, and the reason your team submits
    a justification rather than just a number is that the justification is the only part
    of the work that could not have been produced without you.
    """)
    return


if __name__ == "__main__":
    app.run()
