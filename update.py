#!/usr/bin/env python3
"""Bring your copy of the course files up to date.

    uv run update.py

Run it from inside the course folder before each class. It works whether you
downloaded the ZIP or cloned with git, and it needs nothing installed.

It only ever touches files that came from the course. Notebooks you made
yourself are left alone, and if you have edited a course file your version is
saved next to it rather than thrown away.
"""

import hashlib
import io
import json
import shutil
import sys
import urllib.error
import urllib.request
import zipfile
from datetime import date
from pathlib import Path

ARCHIVE = ("https://github.com/cteplovs/si385-fa2026-student"
           "/archive/refs/heads/main.zip")

# What the course delivers. Anything outside these is yours and is never touched.
COURSE_DIRS = ("notebooks/", "data/", "docs/")
COURSE_FILES = ("README.md", "pyproject.toml", "uv.lock", "update.py")

MANIFEST = Path(".si385-delivered.json")
HERE = Path.cwd()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def is_course_file(name: str) -> bool:
    return name.startswith(COURSE_DIRS) or name in COURSE_FILES


def fetch() -> dict[str, bytes]:
    """Download the current course files. Returns {relative path: contents}."""
    try:
        with urllib.request.urlopen(ARCHIVE, timeout=60) as r:
            blob = r.read()
    except urllib.error.URLError as e:
        sys.exit(f"Could not reach GitHub: {e.reason}\n"
                 f"Check your connection and try again. Nothing was changed.")

    files = {}
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            # Strip the "si385-fa2026-student-main/" prefix GitHub adds.
            name = info.filename.split("/", 1)[1]
            if is_course_file(name):
                files[name] = z.read(info)
    return files


def main() -> int:
    if not (HERE / "pyproject.toml").exists() or not (HERE / "notebooks").is_dir():
        sys.exit("This does not look like the course folder.\n"
                 "Move into the folder that contains 'notebooks' and try again.")

    delivered = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    incoming = fetch()

    added, updated, kept, unchanged = [], [], [], 0
    stamp = date.today().isoformat()

    for name, content in sorted(incoming.items()):
        local = HERE / name
        if not local.exists():
            local.parent.mkdir(parents=True, exist_ok=True)
            local.write_bytes(content)
            added.append(name)
            continue

        current = local.read_bytes()
        if current == content:
            unchanged += 1
        else:
            # Did you change this file, or is your copy simply old? The manifest
            # records what was last delivered, so the two can be told apart.
            yours = digest(current) != delivered.get(name, digest(current))
            if yours:
                backup = local.with_name(f"{local.stem}.yours-{stamp}{local.suffix}")
                shutil.copy2(local, backup)
                kept.append(f"{name}  (your version saved as {backup.name})")
            local.write_bytes(content)
            updated.append(name)

    MANIFEST.write_text(json.dumps({n: digest(c) for n, c in incoming.items()},
                                   indent=1, sort_keys=True))

    def show(title, items):
        if items:
            print(f"\n{title}")
            for i in items:
                print(f"  {i}")

    show("New:", added)
    show("Updated:", [u for u in updated if not any(u in k for k in kept)])
    show("Updated, and your edits were saved:", kept)
    print(f"\n{unchanged} file(s) already current. Nothing of yours was deleted.")
    if not added and not updated:
        print("You are up to date.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
