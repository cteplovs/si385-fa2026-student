# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo==0.24.0",
#     "numpy==2.4.6",
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

__generated_with = "0.23.16"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # SI 385 — Data Exploration

    ## Session 2: marimo and your working environment

    ### Dr. Chris Teplovs, School of Information, University of Michigan

    Wednesday, September 2, 2026

    **Reading due today:** marimo *Getting Started*; *R for Data Science* 2e §10.1–10.2

    ---

    ### Today you will be able to

    - Explain what makes a marimo notebook different from a Jupyter notebook
    - Run a notebook in marimo and read a dependency graph off the code
    - Leave with a working environment — local install or molab — that you will use all term
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    ## Where this session goes

    | Time | Block |
    |---|---|
    | 0:00–0:15 | Clarification — the practice RAT you took last night |
    | 0:15–0:20 | Form teams |
    | 0:20–0:55 | Hands-on: install, launch, and the reactive model |
    | 0:55–1:05 | Whole-room status check |
    | 1:05–1:15 | molab, and what to do if it is still broken |
    | 1:15–1:20 | Before September 9 |

    This session has no application exercise. The deliverable is a working environment,
    not a shared analytical commitment, so the simultaneous report is replaced by a
    status check at 0:55.

    **You took the practice RAT on Canvas last night**, and it was ungraded — it does not
    count toward your RAT total. From here on the pattern is the same every session: the
    quiz opens two days before class and closes at 20:59 the night before, and class opens
    with the fifteen minutes of clarification you are about to see. There is no team
    version of the RAT.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    # 0:00 — Clarification

    Your answers are in, so we already know which items split the room. We spend this
    block on those and not on the ones everybody got.

    **Appeals are a team action.** If your team believes an item was ambiguous, or that
    the reading supports an answer marked wrong, put it in writing citing the reading,
    before you leave the room on the day we discuss it. One per team. A successful appeal
    restores credit to everyone on the team.

    Nothing today is graded, so this round is purely about learning what the format feels
    like.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    # 0:15 — Form your team

    **Five minutes.** Teams of four, and they stay together all term.

    If you do not have three other people yet, turn to the people around you now. The
    diagnostic aggregate from Monday is on Canvas — mixing SI 345 sections gives your team
    a wider toolkit, and that pays off from session 3 onwards. You do not need to be best
    friends; you need to be able to argue about data for 80 minutes twice a week. That is
    a lower bar than it sounds.

    Once you have four people, submit your roster via the Canvas Group activity. That is
    the official record.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    # 0:20 — Hands-on: install, launch, and the reactive model

    Two stages. If you get stuck, ask your team before you raise your hand — your
    teammates are the first line of support all term, and this is a good moment to start
    that habit.

    **Stage 1 — Install and launch (0:20–0:35)**
    **Stage 2 — The reactive model (0:35–0:55)**
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    ## Stage 1 — Install and launch

    The full instructions are in the setup guide on Canvas, which you should already
    have worked through. The short version:

    ```bash
    uv run marimo edit --no-sandbox notebooks/lectures/L02_marimo_tooling.py
    ```

    `uv` installs the right Python and the packages this course needs. You do not install
    Python yourself. If you have not installed `uv` yet, step 1 of the setup guide is
    a single line for your platform.

    You should see this notebook open in a browser tab. If you are reading this in marimo,
    stage 1 is done.

    ### If it fights you

    Stop after five minutes and go to **[molab.marimo.io](https://molab.marimo.io)**:
    free, no install, runs in a browser tab. You are not behind. molab is a first-class
    option and not a consolation prize — several people will work this way all term.

    Download this notebook from Canvas and upload it through the molab interface, or just
    work in a blank notebook for today.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    ## Stage 2 — The reactive model

    Run the cells below in order, then change the slider and watch what happens.

    The point is not the content — it is the experience of reactivity. **Change a value
    and watch everything downstream update without you pressing anything.**
    """
    )
    return


@app.cell
def _(mo):
    n_points = mo.ui.slider(10, 500, value=100, label="Number of points")
    n_points
    return (n_points,)


@app.cell
def _(n_points):
    import numpy as np
    rng = np.random.default_rng(42)
    demo_x = rng.normal(0, 1, n_points.value)
    demo_y = 0.7 * demo_x + rng.normal(0, 0.5, n_points.value)
    return demo_x, demo_y, np, rng


@app.cell
def _(demo_x, demo_y, mo, np):
    import matplotlib.pyplot as plt
    _fig, _ax = plt.subplots(figsize=(6, 4))
    _ax.scatter(demo_x, demo_y, alpha=0.4, s=18, color="#00274C")
    _ax.set_xlabel("x")
    _ax.set_ylabel("y")
    _corr = float(np.corrcoef(demo_x, demo_y)[0, 1])
    _ax.set_title(f"n = {len(demo_x)}, r = {_corr:.3f}")
    plt.tight_layout()
    mo.mpl.interactive(_fig)
    return (plt,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    **What just happened.** Drag the slider. The scatterplot and the correlation update
    live — no re-run, no kernel restart. That is marimo's reactive graph: every cell
    declares its inputs through the variables it uses, and marimo re-executes any cell
    whose inputs changed. Position in the file has nothing to do with it.

    **The one-variable rule in action.** Notice that `demo_x` is defined in exactly one
    cell. If you redefined it in a second cell, marimo would refuse to run — it could not
    tell which cell produced the `demo_x` that the plot reads. This is not a quirk; it is
    the mechanism that makes reactivity possible.

    ### Try breaking it, on purpose

    Add a new cell below containing:

    ```python
    demo_x = [1, 2, 3]
    ```

    marimo flags the conflict immediately. Read what it says, then delete the cell.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    ## Stage 2b — Delete a definition

    One more, because it is the thing marimo exists for.

    1. Look at the cell that defines `demo_x` and `demo_y`.
    2. Imagine deleting it. In Jupyter, the plot below would keep working — the values
       would still be alive in the kernel, and the notebook on screen would no longer
       match the code that produced it.
    3. In marimo, the plot errors immediately, because the dependency is live.

    Try it if you have time, then undo. No hidden state, by construction. That property
    is why this course uses marimo, and it is worth more than the slider.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    # 0:55 — Whole-room status check

    Sli.do — everyone answers at once:

    > **Where are you right now?**
    >
    > A. marimo running locally — this notebook is open and the slider works
    > B. Working in molab — the slider works
    > C. Installed, but something is not working
    > D. Nothing is working yet
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    # 1:05 — molab, and what to do if it is still broken

    **[molab.marimo.io](https://molab.marimo.io)** is the answer for anyone whose local
    environment is still broken after today. It is not a downgrade.

    What molab gives you:

    - Full marimo in a browser tab — no install, no Python version conflict
    - Shareable notebooks via URL
    - Enough compute for everything in this course

    What it does not give you:

    - Access to files on your own machine — you upload datasets instead
    - Persistent local state between sessions unless you save

    For application exercises, molab is fine. For the project you may eventually want a
    local environment, but that is a problem for October.

    **Do not spend the next week fighting your laptop.** Come to office hours, or work in
    molab. The nine-day gap before session 3 is not a grace period, and a setup that is
    broken today will still be broken on September 9 unless someone looks at it with you.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ---
    # 1:15 — Consolidation

    **The one thing that must survive this session:**

    A marimo notebook is a dependency graph, not a script. The single-variable rule and
    reactive re-execution are the same mechanism — cells declare their dependencies
    through the variables they use, and marimo infers what to re-run. Understand that and
    everything else follows.

    A marimo notebook is also a plain `.py` file. You can read it top to bottom, diff it,
    and put it under version control like any other code. That is not a side benefit; it
    is why the format was chosen.

    ---

    ### Before Wednesday, September 9

    1. **Read:** Bruce et al. ch. 1, through *Exploring the Data Distribution* (§§1–6).
       That part is all you are expected to have read — the chapter is split across four
       sessions.
    2. **Take the RAT.** It opens on Canvas Monday Sep 7 at 09:50 and closes Tuesday Sep 8
       at 20:59. This one counts.
    3. **Confirm your environment works** — local marimo or molab. If it is still broken,
       come to office hours before Sep 9.
    4. **Note:** no class Monday Sep 7 (Labour Day).
    """
    )
    return


if __name__ == "__main__":
    app.run()
