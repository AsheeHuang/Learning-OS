#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path


RESUME_ASSESSMENT = """# Assessment: Processes and Threads

- Date: 2026-08-30
- Status: in-progress
- Topics:
  - [[lessons/processes.md|Processes]]
  - [[lessons/threads.md|Threads]]

## Topic: Processes

- Path: lessons/processes.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-25
- Starting Last Tested: —

### Question 1

Prompt:
Explain a process without quoting the lesson.

Learner answer:
A process is one running program instance with private runtime state.

Feedback:
Correct independent recall.

Evidence:
The learner distinguished executing state from passive code.

Expected key points:
Running instance and private execution state.

Result: strong

### Question 2

Prompt:
Apply process isolation to a new worker-crash scenario.

Learner answer:
The failed worker cannot overwrite another process's private memory, but service-level recovery is not guaranteed.

Feedback:
Correct transfer and limitation.

Evidence:
The learner applied isolation to a new failure boundary.

Expected key points:
Memory isolation and no application-level recovery guarantee.

Result: strong

### Topic Outcome

Grounding: verified
Result: strong
Evidence summary: Independent recall and transfer.

## Topic: Threads

- Path: lessons/threads.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-27
- Starting Last Tested: —

### Question 1

Prompt:
Distinguish thread state from process state.

Learner answer:
Threads share process memory while keeping separate stacks and registers.

Feedback:
Correct distinction.

Evidence:
Independent recall.

Expected key points:
Shared address space and separate execution state.

Result: strong

### Question 2

Prompt:
Two threads update one shared queue without synchronization. Predict a failure and explain why separate stacks do not prevent it.
"""

FINALIZATION_ASSESSMENT = """# Assessment: Processes

- Date: 2026-08-30
- Status: in-progress
- Topics:
  - [[lessons/processes.md|Processes]]

## Topic: Processes

- Path: lessons/processes.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-25
- Starting Last Tested: —

### Question 1

Prompt:
Explain a process in your own words.

Learner answer:
A process is a running program instance with private execution state.

Feedback:
Correct recall.

Evidence:
Independent recall.

Expected key points:
Running instance and state.

Result: strong

### Question 2

Prompt:
Apply process isolation to a new crash scenario.

Learner answer:
Another process's private memory remains protected, while service recovery is not guaranteed.

Feedback:
Correct transfer.

Evidence:
Independent transfer.

Expected key points:
Memory boundary and limitation.

Result: strong

### Topic Outcome

Grounding: verified
Result: strong
Evidence summary: Independent recall and transfer.

## Misconceptions

None.

## Summary

Grounded recall and transfer.

## Progress Changes

- [[lessons/processes.md|Processes]]: `Needs Validation` → `Mastered`
"""


def add_caching_workspace(vault: Path) -> None:
    operating_systems = vault / "Learn" / "Operating Systems"
    progress = operating_systems / "PROGRESS.md"
    progress.write_text(
        progress.read_text()
        + "| [[lessons/caching.md|Caching]] | lessons/caching.md | Needs Validation | 2026-08-28 | — |\n"
    )
    (operating_systems / "lessons" / "caching.md").write_text(
        "# Caching\n\n## Explanation\n\nA persisted Operating Systems caching lesson.\n\n"
        "## Sources\n\n- [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/)\n"
    )

    databases = vault / "Learn" / "Databases"
    (databases / "lessons").mkdir(parents=True)
    (databases / "notes").mkdir()
    (databases / "assessments").mkdir()
    (databases / "MISSION.md").write_text("# Mission: Databases\n")
    (databases / "MAP.md").write_text("# Databases\n\n## Performance\n\n- [[lessons/caching.md|Caching]]\n")
    (databases / "PROGRESS.md").write_text(
        """# Learning Progress

## Current Focus

—

## Topics

| Topic | Path | Status | Last Learned | Last Tested |
|---|---|---|---|---|
| [[lessons/caching.md|Caching]] | lessons/caching.md | Needs Validation | 2026-08-28 | — |
"""
    )
    (databases / "HISTORY.md").write_text("# Learning History\n")
    (databases / "RESOURCES.md").write_text("# Database Resources\n\n## Knowledge\n\n## Further Reading\n")
    (databases / "lessons" / "caching.md").write_text(
        "# Caching\n\n## Explanation\n\nA persisted database caching lesson.\n"
    )


def prepare(case: str, vault: Path) -> None:
    workspace = vault / "Learn" / "Operating Systems"
    if case == "quiz-resume":
        (workspace / "assessments" / "2026-08-30-processes-and-threads.md").write_text(
            RESUME_ASSESSMENT
        )
    elif case == "quiz-finalization":
        progress = workspace / "PROGRESS.md"
        progress.write_text(
            progress.read_text().replace(
                "| [[lessons/processes.md|Processes]] | lessons/processes.md | Needs Validation | 2026-08-25 | — |",
                "| [[lessons/processes.md|Processes]] | lessons/processes.md | Mastered | 2026-08-25 | 2026-08-30 |",
            )
        )
        (workspace / "assessments" / "2026-08-30-processes.md").write_text(
            FINALIZATION_ASSESSMENT
        )
    elif case == "quiz-ambiguity":
        add_caching_workspace(vault)
    elif case == "quiz-dispute":
        (workspace / "RESOURCES.md").write_text(
            "# Operating Systems Resources\n\n## Knowledge\n\n## Further Reading\n"
        )
    elif case == "quiz-conflict":
        (workspace / "assessments" / "2026-08-30-processes.md").write_text(
            FINALIZATION_ASSESSMENT
        )
        progress = workspace / "PROGRESS.md"
        progress.write_text(
            progress.read_text().replace(
                "| [[lessons/processes.md|Processes]] | lessons/processes.md | Needs Validation | 2026-08-25 | — |",
                "| [[lessons/processes.md|Processes]] | lessons/processes.md | Needs Review | 2026-08-29 | — |",
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True)
    parser.add_argument("--vault", type=Path, required=True)
    args = parser.parse_args()
    prepare(args.case, args.vault)


if __name__ == "__main__":
    main()
