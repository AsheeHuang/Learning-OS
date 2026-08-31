#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

NOTE_LINK = "[[notes/context-switch.md|Context Switch]]"
NOTE_ROW = "| [[notes/context-switch.md|Context Switch]] | notes/context-switch.md | Needs Validation | 2026-08-27 | — |"
SOURCE_LINK = "- [[notes/context-switch.md|Context Switch]]"


def workspace(vault: Path) -> Path:
    return vault / "Learn" / "Operating Systems"


def set_current_focus(root: Path, focus: str) -> None:
    progress = root / "PROGRESS.md"
    text = progress.read_text(encoding="utf-8")
    text = re.sub(
        r"(?s)(## Current Focus\n\n).*?(\n\n## Topics)",
        rf"\g<1>{focus}\g<2>",
        text,
        count=1,
    )
    progress.write_text(text, encoding="utf-8")


def remove_note_state(root: Path) -> None:
    note = root / "notes" / "context-switch.md"
    if note.exists():
        note.unlink()
    progress = root / "PROGRESS.md"
    lines = progress.read_text(encoding="utf-8").splitlines(keepends=True)
    progress.write_text("".join(line for line in lines if NOTE_LINK not in line), encoding="utf-8")
    source = root / "lessons" / "processes.md"
    lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
    source.write_text("".join(line for line in lines if SOURCE_LINK not in line), encoding="utf-8")
    history = root / "HISTORY.md"
    text = history.read_text(encoding="utf-8")
    text = re.sub(r"\n### Explored: Context Switch\n.*?(?=\n## |\Z)", "", text, flags=re.DOTALL)
    history.write_text(text, encoding="utf-8")


def prepare(case: str, vault: Path) -> None:
    root = workspace(vault)
    set_current_focus(root, "[[lessons/processes.md|Processes]]")

    if case in {"note-create", "note-promotion", "note-unverified"}:
        remove_note_state(root)
        if case == "note-unverified":
            (root / "RESOURCES.md").write_text(
                "# Operating Systems Resources\n\n## Knowledge\n\n## Further Reading\n",
                encoding="utf-8",
            )
    elif case == "note-resume":
        (root / "notes" / "context-switch.md").write_text(
            "# Context Switch\n\n<!-- Human note: preserve this observation. -->\n\n"
            "Source: [[lessons/processes.md|Processes]]\n\n"
            "## Question\n\nWhat is a context switch?\n\n"
            "## Explanation\n\nA partial draft awaiting completion.\n",
            encoding="utf-8",
        )
        # The base row/history represent a previous exploration; remove only the
        # reciprocal link so the rerun has one missing durable effect to repair.
        source = root / "lessons" / "processes.md"
        source.write_text(
            "\n".join(
                line
                for line in source.read_text(encoding="utf-8").splitlines()
                if SOURCE_LINK not in line
            )
            + "\n",
            encoding="utf-8",
        )
    elif case == "note-ambiguity":
        second = vault / "Learn" / "Databases"
        shutil.copytree(vault / "Learn" / "Operating Systems", second)
        set_current_focus(second, "[[lessons/processes.md|Processes]]")
    else:
        raise ValueError(f"Unknown note case: {case}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--vault", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.case, args.vault)


if __name__ == "__main__":
    main()
