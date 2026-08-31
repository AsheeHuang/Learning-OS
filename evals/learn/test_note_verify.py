from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

import verify_note


MAP = """# Operating Systems

## Execution

- [[lessons/processes.md|Processes]]
"""

PROGRESS = """# Learning Progress

## Current Focus

[[lessons/processes.md|Processes]]

## Topics

| Topic | Path | Status | Last Learned | Last Tested |
|---|---|---|---|---|
| [[lessons/processes.md|Processes]] | lessons/processes.md | Needs Validation | 2026-08-25 | 2026-08-28 |
"""

SOURCE = """# Processes

## Related Concepts

## Sources

- [OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/)
"""

NOTE = """# Context Switch

Source: [[lessons/processes.md|Processes]]

## Question

What is Context Switch, and why does it matter when learning Processes?

## Explanation

A context switch preserves execution state so another task can run. [OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/)

## Connection to the Source

It lets multiple process contexts share CPU time.

## Related Concepts

## Sources

- [OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/)
"""


class VerifyNoteTests(unittest.TestCase):
    def make_workspace(self, root: Path, with_note: bool = True) -> Path:
        workspace = root / "Learn" / "Operating Systems"
        (workspace / "lessons").mkdir(parents=True)
        (workspace / "notes").mkdir()
        (workspace / "assessments").mkdir()
        (workspace / "MISSION.md").write_text("# Mission: Operating Systems\n")
        (workspace / "MAP.md").write_text(MAP)
        progress = PROGRESS
        if with_note:
            progress = progress.replace(
                "| [[lessons/processes.md|Processes]] | lessons/processes.md | Needs Validation | 2026-08-25 | 2026-08-28 |",
                f"| [[lessons/processes.md|Processes]] | lessons/processes.md | Needs Validation | 2026-08-25 | 2026-08-28 |\n| [[notes/context-switch.md|Context Switch]] | notes/context-switch.md | Learning | {date.today().isoformat()} | — |",
            )
        (workspace / "PROGRESS.md").write_text(progress)
        history = "# Learning History\n"
        if with_note:
            history += "\n## 2026-08-30\n\n### Explored: Context Switch\n\n- Artifact: [[notes/context-switch.md|Context Switch]]\n"
        (workspace / "HISTORY.md").write_text(history)
        (workspace / "RESOURCES.md").write_text("# Resources\n\n## Knowledge\n\n## Further Reading\n")
        (workspace / "lessons" / "processes.md").write_text(SOURCE)
        if with_note:
            (workspace / "notes" / "context-switch.md").write_text(NOTE)
            (workspace / "lessons" / "processes.md").write_text(
                SOURCE.replace("## Related Concepts\n", "## Related Concepts\n\n- [[notes/context-switch.md|Context Switch]]\n")
            )
        return workspace

    def test_complete_note_passes_and_preserves_source_row(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initial = root / "initial"
            final = root / "final"
            self.make_workspace(initial, with_note=False)
            self.make_workspace(final, with_note=True)
            result = verify_note.verify_complete("note-create", final, initial)
            self.assertTrue(result["passed"], result)

    def test_ambiguity_requires_an_unchanged_vault(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initial = root / "initial"
            final = root / "final"
            self.make_workspace(initial, with_note=False)
            self.make_workspace(final, with_note=False)
            (final / "Learn" / "Databases").mkdir()
            (initial / "Learn" / "Databases").mkdir()
            result = verify_note.verify_ambiguity(final, initial, None)
            self.assertFalse(result["passed"])
            self.assertIn("ambiguous source asks for disambiguation", {item["name"] for item in result["expectations"] if not item["passed"]})


if __name__ == "__main__":
    unittest.main()
