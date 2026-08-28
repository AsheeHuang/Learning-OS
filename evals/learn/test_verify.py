from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import verify


MISSION = """# Mission: Operating Systems

## Why

Learn how applications interact with operating systems.

## Current Level

Application developer.

## Target Level

Reason about operating-system behavior.

## Desired Outcomes

Diagnose unfamiliar production scenarios.

## Success Criteria

Apply the concepts to new examples.

## Constraints

Short sessions.

## Out of Scope

Kernel development.
"""

MAP = """# Operating Systems

## Execution

- [[lessons/processes.md|Processes]]
- [[lessons/threads.md|Threads]]
"""

PROGRESS = """# Learning Progress

## Current Focus

—

## Topics

| Topic | Path | Status | Last Learned | Last Tested |
|---|---|---|---|---|
| [[lessons/processes.md|Processes]] | lessons/processes.md | Unexplored | — | — |
| [[lessons/threads.md|Threads]] | lessons/threads.md | Unexplored | — | — |
"""

RESOURCES = """# Operating Systems Resources

## Knowledge

## Further Reading
"""

HISTORY = """# Learning History

## 2026-08-28

### Created: Operating Systems workspace
"""


class VerifyLearnWorkspaceTests(unittest.TestCase):
    def make_workspace(self, root: Path, topic: str = "Operating Systems") -> Path:
        workspace = root / "Learn" / topic
        workspace.mkdir(parents=True)
        (workspace / "MISSION.md").write_text(MISSION)
        (workspace / "MAP.md").write_text(MAP)
        (workspace / "PROGRESS.md").write_text(PROGRESS)
        (workspace / "RESOURCES.md").write_text(RESOURCES)
        (workspace / "HISTORY.md").write_text(HISTORY)
        for directory in ("lessons", "notes", "assessments"):
            (workspace / directory).mkdir()
        return workspace

    def test_fresh_workspace_passes_when_protocol_invariants_hold(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            self.make_workspace(vault)

            result = verify.verify_case("fresh-topic", vault, None, None)

            self.assertTrue(result["passed"], result)

    def test_fresh_workspace_fails_when_map_and_progress_diverge(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            workspace = self.make_workspace(vault)
            progress = (workspace / "PROGRESS.md").read_text()
            (workspace / "PROGRESS.md").write_text(
                progress.replace(
                    "| [[lessons/threads.md|Threads]] | lessons/threads.md | Unexplored | — | — |\n",
                    "",
                )
            )

            result = verify.verify_case("fresh-topic", vault, None, None)

            failed = {item["name"] for item in result["expectations"] if not item["passed"]}
            self.assertIn("map and progress paths match", failed)

    def test_research_unavailable_rejects_resource_entries(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory)
            workspace = self.make_workspace(vault)
            (workspace / "RESOURCES.md").write_text(
                RESOURCES.replace(
                    "## Further Reading",
                    "- [Unverified Source](https://example.com)\n  Added from memory.\n\n## Further Reading",
                )
            )

            result = verify.verify_case(
                "fresh-topic",
                vault,
                None,
                None,
                research_unavailable=True,
            )

            failed = {item["name"] for item in result["expectations"] if not item["passed"]}
            self.assertIn("research-unavailable resources stay empty", failed)

    def test_partial_resume_preserves_existing_status_and_human_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            initial = root / "initial"
            final = root / "final"
            initial_workspace = self.make_workspace(initial, "Databases")
            final_workspace = self.make_workspace(final, "Databases")

            for workspace in (initial_workspace, final_workspace):
                progress = (workspace / "PROGRESS.md").read_text()
                progress = progress.replace(
                    "Unexplored | — | — |",
                    "Needs Validation | 2026-08-27 | — |",
                    1,
                )
                (workspace / "PROGRESS.md").write_text(progress)

            result = verify.verify_case("partial-resume", final, initial, None)

            self.assertTrue(result["passed"], result)

    def test_missing_mission_case_requires_questions_and_no_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            vault = root / "vault"
            vault.mkdir()
            events = root / "events.jsonl"
            events.write_text(
                json.dumps(
                    {
                        "type": "message_end",
                        "message": {
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        "Why do you want to learn this? What is your current level? "
                                        "What target outcome do you want, and what should you be able to do afterward? "
                                        "What constraints and out of scope boundaries apply?"
                                    ),
                                }
                            ],
                        },
                    }
                )
                + "\n"
            )

            untouched = verify.verify_case("missing-mission", vault, None, events)
            no_questions = verify.verify_case("missing-mission", vault, None, None)
            (vault / "Learn" / "Distributed Systems").mkdir(parents=True)
            modified = verify.verify_case("missing-mission", vault, None, events)

            self.assertTrue(untouched["passed"], untouched)
            self.assertFalse(no_questions["passed"], no_questions)
            self.assertFalse(modified["passed"], modified)


if __name__ == "__main__":
    unittest.main()
