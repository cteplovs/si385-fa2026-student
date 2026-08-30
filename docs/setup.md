# Setting up your laptop

**Time: about ten minutes, most of it waiting.** Do this before session 2 (Wed Sep 2).
If it goes wrong, do not spend your evening fighting it — read the last section and come
to class with the error message.

## You do not need to install Python

This is the part people get wrong, so it is worth saying plainly: **do not go to
python.org.** You are installing one thing, called `uv`, and `uv` installs the correct
version of Python for you, in a place that cannot break anything else on your machine.

If you already have Python installed from some previous course, that is fine. Leave it
alone. It will not be used and it will not conflict with the tools we're using in this course.

---

## Step 1 — Install uv

Open a terminal.

- **macOS:** Terminal (⌘-space, type "terminal")
- **Windows:** PowerShell (Start menu, type "powershell"). Not Command Prompt.

Paste **one** line — the one for your machine — and press Enter.

**macOS / Linux**

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows**

```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Then close the terminal window and open a new one.** The installer adds `uv` to your
PATH, and a terminal that was already open has not heard about it. Skipping this is the
single most common reason step 2 "fails".

## Step 2 — Check that it worked

```
uv --version
```

You should get a version number, something like `uv 0.9.x`. Any version number is fine.

If instead you get `command not found` or `not recognized`, see troubleshooting below.

## Step 3 — Get the course files

Download the course repository as a ZIP:

**<https://github.com/cteplovs/si385-fa2026-student/archive/refs/heads/main.zip>**

That link starts the download immediately. Unzip it somewhere you will find again —
your Desktop is a perfectly good answer. Avoid anything inside a synced folder that is
aggressively cleaning up after you.

The unzipped folder is called `si385-fa2026-student-main`. GitHub adds the `-main`; it
is not a mistake and you do not need to rename it. Move your terminal into it:

```
cd Desktop/si385-fa2026-student-main
```

On Windows the same line works in PowerShell. If you unzipped somewhere other than the
Desktop, the reliable trick is to type `cd ` (with the space) and then drag the folder
from Finder or File Explorer onto the terminal window — it fills in the path for you.

If you are comfortable with git, clone it instead — you will get updates with
`git pull` rather than re-downloading:

```
git clone https://github.com/cteplovs/si385-fa2026-student.git
```

If you do not know what that means, the ZIP is not a lesser option — it is the same
files. Materials will be added during term; re-download the ZIP when that happens.

## Step 4 — Open a notebook

```
uv run marimo edit notebooks/lectures/L02_marimo_tooling.py
```

**The first time you run this it will take a few minutes.** It is downloading Python
and the packages the course uses. It is not stuck. Every run after this one is instant.

A browser tab will open with the notebook in it. That is marimo. That tab is where you
work — there is nothing else to install, and no extension to add to anything.

To stop it, go back to the terminal and press `Ctrl-C`.  Remember to save your work before quitting.

---

## If your laptop is fighting you

You are not going to be locked out of an application exercise because of a laptop. Use
**[molab](https://molab.marimo.io)** — marimo's free cloud sandbox. It runs the same
notebooks in a browser tab with nothing installed, and it is a completely legitimate way
to take this course. Several people will end up working this way all term.

Bring the failure to session 2 anyway.  We can probably fix the problem or decide that it's not worth fixing in a few minutes instead of you banging your head against the machine for an hour.

## Troubleshooting

| What you see | What to do |
|---|---|
| `uv: command not found` / `'uv' is not recognized` | Close the terminal completely and open a new one. If it still fails, restart the laptop — this genuinely fixes it. |
| Windows: `running scripts is disabled on this system` | You changed the install command. Use the `-ExecutionPolicy ByPass` version exactly as written above. |
| The install command hangs or times out | You are probably on a VPN or a restricted network. Try again on a normal connection. |
| Your laptop is managed by an employer and blocks installs | Do not fight it. Use molab. |
| `No such file or directory` naming the notebook | Your terminal is not in the course folder. Run `ls` (macOS) or `dir` (Windows): you should see `notebooks`, `data`, and `docs`. If you do not, `cd` into the unzipped folder — see step 3. |
| The notebook opens, but cells show `ModuleNotFoundError: No module named 'numpy'` (or `pandas`, `seaborn`) | Same cause: your terminal was outside the course folder, so `uv` had nothing telling it what to install and gave you marimo on its own. `Ctrl-C`, `cd` into the folder, and run the command again. |
| `uv run` fails with a long red wall of text | Copy the **last five lines** and bring them to class or post them on Canvas. The first forty lines are never the useful part. |
| The browser tab never opens | Look in the terminal for a `http://localhost:...` address and paste it into a browser yourself. |
| Something else | Post it on Canvas with the exact error text and your operating system. Someone else has it too. |

## What "done" looks like

You ran `uv run marimo edit notebooks/lectures/L02_marimo_tooling.py`, a browser tab
opened, and you can see the notebook. That is the whole bar. Nothing to submit.
