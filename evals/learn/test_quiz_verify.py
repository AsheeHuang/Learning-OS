from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import prepare_quiz_fixture
import verify


FIXTURE = Path(__file__).parent / "fixtures" / "quiz-base" / "vault"


class VerifyLearnQuizTests(unittest.TestCase):
    def copy_fixture(self, root: Path) -> tuple[Path, Path, Path]:
        initial = root / "initial"
        final = root / "final"
        shutil.copytree(FIXTURE, initial)
        shutil.copytree(FIXTURE, final)
        workspace = final / "Learn" / "Operating Systems"
        return initial, final, workspace

    def complete_progress(self, workspace: Path, topic: str, status: str) -> None:
        path = workspace / "PROGRESS.md"
        text = path.read_text()
        if topic == "Processes":
            before = "| [[lessons/processes.md|Processes]] | lessons/processes.md | Needs Validation | 2026-08-25 | — |"
            after = f"| [[lessons/processes.md|Processes]] | lessons/processes.md | {status} | 2026-08-25 | 2026-08-30 |"
        elif topic == "Threads":
            before = "| [[lessons/threads.md|Threads]] | lessons/threads.md | Needs Validation | 2026-08-27 | — |"
            after = f"| [[lessons/threads.md|Threads]] | lessons/threads.md | {status} | 2026-08-27 | 2026-08-30 |"
        else:
            before = "| [[notes/context-switch.md|Context Switch]] | notes/context-switch.md | Needs Validation | 2026-08-27 | — |"
            after = f"| [[notes/context-switch.md|Context Switch]] | notes/context-switch.md | {status} | 2026-08-27 | 2026-08-30 |"
        path.write_text(text.replace(before, after))

    def append_history(self, workspace: Path, assessment: str, topic: str, result: str) -> None:
        transitions = {
            "Processes": "Needs Validation → Mastered",
            "Threads": "Needs Validation → Needs Review",
            "Context Switch": "Needs Validation → Needs Review",
            "Processes and Threads": "Processes: Needs Validation → Mastered; Threads: Needs Validation → Mastered",
        }
        path = workspace / "HISTORY.md"
        if topic == "Processes and Threads":
            topic_result = result.split(",")[0].strip()
            event = (
                "- Topic: [[lessons/processes.md|Processes]]\n"
                f"- Outcome: `{topic_result}`\n"
                "- Status: `Needs Validation` → `Mastered`\n"
                "- Topic: [[lessons/threads.md|Threads]]\n"
                f"- Outcome: `{topic_result}`\n"
                "- Status: `Needs Validation` → `Mastered`\n"
            )
        else:
            event = (
                f"- Topic: [[lessons/{topic.lower()}.md|{topic}]]\n"
                f"- Outcome: `{result}`\n"
                f"- Status: `{transitions[topic].replace(' → ', '` → `')}`\n"
            )
        path.write_text(
            path.read_text()
            + f"\n## 2026-08-30\n\n### Assessed: {topic}\n\n"
            + event
            + f"- Assessment: [[assessments/{assessment}.md|{topic} Assessment]]\n"
        )

    def test_grounded_strong_assessment_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, workspace = self.copy_fixture(Path(directory))
            assessment = workspace / "assessments" / "2026-08-30-processes.md"
            assessment.write_text(
                """# Assessment: Processes

- Date: 2026-08-30
- Status: complete
- Topics:
  - [[lessons/processes.md|Processes]]

## Topic: Processes

- Path: lessons/processes.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-25
- Starting Last Tested: —

### Question 1

Source section: ## Explanation
Prompt: Explain a process in your own words.
Learner answer: A running program instance with its own execution state.
Feedback: Correct core distinction.
Evidence: Independent recall.
Expected key points: Running instance and execution state.
Result: strong

### Question 2

Source section: ## Example
Prompt: Predict what isolation protects in a new crash scenario.
Learner answer: Another process's private memory remains protected.
Feedback: Correct transfer.
Evidence: Applied isolation to a new scenario.
Expected key points: Memory boundary and application-level limitation.
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
            )
            self.complete_progress(workspace, "Processes", "Mastered")
            self.append_history(workspace, "2026-08-30-processes", "Processes", "strong")

            result = verify.verify_case("quiz-strong", final, initial, None)
            history = workspace / "HISTORY.md"
            history.write_text(history.read_text().replace("- Outcome: `strong`", "- Evidence: strong", 1))
            missing_outcome = verify.verify_case("quiz-strong", final, initial, None)
            assessment.write_text(
                assessment.read_text().replace(
                    "Learner answer: A running program instance with its own execution state.",
                    "Learner answer:",
                )
            )
            empty_answer = verify.verify_case("quiz-strong", final, initial, None)

            self.assertTrue(result["passed"], result)
            self.assertFalse(missing_outcome["passed"], missing_outcome)
            self.assertFalse(empty_answer["passed"], empty_answer)

    def test_remediation_partial_assessment_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, workspace = self.copy_fixture(Path(directory))
            assessment = workspace / "assessments" / "2026-08-30-threads.md"
            assessment.write_text(
                """# Assessment: Threads

- Date: 2026-08-30
- Status: complete
- Topics:
  - [[lessons/threads.md|Threads]]

## Topic: Threads

- Path: lessons/threads.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-27
- Starting Last Tested: —

### Question 1

Prompt: Distinguish thread and process isolation.
Learner answer: Every thread has a separate address space.
Feedback: Threads in one process share the address space.
Diagnosis: concept-confusion — the answer treated thread state as process isolation.
Remediation prompt: Revise the distinction using shared and private state.
Revised answer: Threads share process memory but keep separate stacks and registers.
Follow-up feedback: The correction repairs the distinction.
Evidence: Recall succeeded only after corrective feedback.
Expected key points: Shared address space and separate execution state.
Result: partial

### Question 2

Prompt: Predict a shared-state failure in a new scenario.
Learner answer: Unsynchronized increments can lose updates.
Feedback: Correct transfer.
Evidence: Applied the model to a race.
Expected key points: Shared mutation requires coordination.
Result: strong

### Topic Outcome

Grounding: verified
Result: partial
Evidence summary: Transfer was independent; recall required remediation.

## Misconceptions

Initially confused thread execution state with process isolation.

## Summary

The learner corrected the distinction after feedback.

## Progress Changes

- [[lessons/threads.md|Threads]]: `Needs Validation` → `Needs Review`
"""
            )
            self.complete_progress(workspace, "Threads", "Needs Review")
            self.append_history(workspace, "2026-08-30-threads", "Threads", "partial")

            result = verify.verify_case("quiz-remediation", final, initial, None)

            self.assertTrue(result["passed"], result)

    def test_in_progress_assessment_requires_atomic_progress(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, workspace = self.copy_fixture(Path(directory))
            (workspace / "assessments" / "2026-08-30-processes-and-threads.md").write_text(
                """# Assessment: Processes and Threads

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

Prompt: Explain a process.
Learner answer: A running program instance.
Feedback: Correct direction.
Evidence: Recall evidence.
Expected key points: Running instance and state.
Result: strong

## Topic: Threads

- Path: lessons/threads.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-27
- Starting Last Tested: —

### Question 1

Prompt: Apply thread sharing to a new scenario.
"""
            )

            untouched = verify.verify_case("quiz-in-progress", final, initial, None)
            self.complete_progress(workspace, "Processes", "Mastered")
            modified = verify.verify_case("quiz-in-progress", final, initial, None)

            self.assertTrue(untouched["passed"], untouched)
            self.assertFalse(modified["passed"], modified)

    def test_unverified_topic_cannot_be_mastered(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, workspace = self.copy_fixture(Path(directory))
            assessment = workspace / "assessments" / "2026-08-30-context-switch.md"
            assessment.write_text(
                """# Assessment: Context Switch

- Date: 2026-08-30
- Status: complete
- Topics:
  - [[notes/context-switch.md|Context Switch]]

## Topic: Context Switch

- Path: notes/context-switch.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-27
- Starting Last Tested: —

### Question 1

Prompt: Explain a context switch.
Learner answer: Save one execution context and restore another.
Feedback: Accurate relative to the note.
Evidence: Recall evidence.
Expected key points: Save and restore execution state.
Result: strong

### Question 2

Prompt: Apply the idea to a new scheduler scenario.
Learner answer: The scheduler must preserve resumable state.
Feedback: Accurate relative to the note.
Evidence: Transfer evidence.
Expected key points: Resumable execution state.
Result: strong

### Topic Outcome

Grounding: unverified
Result: partial
Evidence summary: Strong answers capped because the note is unverified.

## Misconceptions

None observed.

## Summary

Understanding is demonstrated but the content needs grounding.

## Progress Changes

- [[notes/context-switch.md|Context Switch]]: `Needs Validation` → `Needs Review`
"""
            )
            self.complete_progress(workspace, "Context Switch", "Needs Review")
            self.append_history(workspace, "2026-08-30-context-switch", "Context Switch", "partial")

            valid = verify.verify_case("quiz-unverified", final, initial, None)
            assessment.write_text(assessment.read_text().replace("Result: partial", "Result: strong", 1))
            self.complete_progress(workspace, "Context Switch", "Mastered")
            invalid = verify.verify_case("quiz-unverified", final, initial, None)

            self.assertTrue(valid["passed"], valid)
            self.assertFalse(invalid["passed"], invalid)

    def test_candidate_selection_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, _ = self.copy_fixture(Path(directory))
            events = Path(directory) / "events.jsonl"
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
                                        "Choose and confirm one to three topics: Processes, Threads, "
                                        "or Context Switch. You may exclude any candidate."
                                    ),
                                }
                            ],
                        },
                    }
                )
                + "\n"
            )

            result = verify.verify_case("quiz-candidates", final, initial, events)
            lesson = final / "Learn" / "Operating Systems" / "lessons" / "processes.md"
            lesson.write_text(lesson.read_text() + "\nUnexpected mutation.\n")
            mutated = verify.verify_case("quiz-candidates", final, initial, events)

            self.assertTrue(result["passed"], result)
            self.assertFalse(mutated["passed"], mutated)

    def test_abandoned_attempt_preserves_state_and_uses_suffix(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, workspace = self.copy_fixture(Path(directory))
            assessments = workspace / "assessments"
            (assessments / "2026-08-30-processes-and-threads.md").write_text(
                """# Assessment: Processes and Threads

- Date: 2026-08-30
- Status: abandoned
- Topics:
  - [[lessons/processes.md|Processes]]
  - [[lessons/threads.md|Threads]]

## Topic: Processes

- Path: lessons/processes.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-25
- Starting Last Tested: —

### Question 1

Prompt: Explain a process.
Learner answer: A running program instance.
"""
            )
            (assessments / "2026-08-30-processes-and-threads-2.md").write_text(
                """# Assessment: Processes and Threads

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
"""
            )

            result = verify.verify_case("quiz-abandon", final, initial, None)

            self.assertTrue(result["passed"], result)

    def test_resume_completes_existing_multi_topic_assessment(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, workspace = self.copy_fixture(Path(directory))
            prepare_quiz_fixture.prepare("quiz-resume", initial)
            prepare_quiz_fixture.prepare("quiz-resume", final)
            assessment = workspace / "assessments" / "2026-08-30-processes-and-threads.md"
            assessment.write_text(
                assessment.read_text().replace("- Status: in-progress", "- Status: complete")
                + """

Learner answer:
Unsynchronized updates can lose queue entries because the shared address space exposes the same queue to both threads.

Feedback:
Correct transfer.

Evidence:
Applied shared state to a new scenario.

Expected key points:
Shared mutation and synchronization.

Result: strong

### Topic Outcome

Grounding: verified
Result: strong
Evidence summary: Independent recall and transfer.

## Misconceptions

None.

## Summary

Both topics have grounded recall and transfer.

## Progress Changes

- [[lessons/processes.md|Processes]]: `Needs Validation` → `Mastered`
- [[lessons/threads.md|Threads]]: `Needs Validation` → `Mastered`
"""
            )
            self.complete_progress(workspace, "Processes", "Mastered")
            self.complete_progress(workspace, "Threads", "Mastered")
            self.append_history(
                workspace,
                "2026-08-30-processes-and-threads",
                "Processes and Threads",
                "strong, strong",
            )

            result = verify.verify_case("quiz-resume", final, initial, None)

            self.assertTrue(result["passed"], result)

    def test_cross_workspace_ambiguity_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, _ = self.copy_fixture(Path(directory))
            prepare_quiz_fixture.prepare("quiz-ambiguity", initial)
            prepare_quiz_fixture.prepare("quiz-ambiguity", final)

            result = verify.verify_case("quiz-ambiguity", final, initial, None)

            self.assertTrue(result["passed"], result)

    def test_interrupted_finalization_adds_only_missing_history(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, workspace = self.copy_fixture(Path(directory))
            prepare_quiz_fixture.prepare("quiz-finalization", initial)
            prepare_quiz_fixture.prepare("quiz-finalization", final)
            assessment = workspace / "assessments" / "2026-08-30-processes.md"
            assessment.write_text(assessment.read_text().replace("- Status: in-progress", "- Status: complete"))
            self.append_history(workspace, "2026-08-30-processes", "Processes", "strong")

            result = verify.verify_case("quiz-finalization", final, initial, None)
            progress = workspace / "PROGRESS.md"
            progress.write_text(progress.read_text().replace("2026-08-30 |", "2026-08-31 |", 1))
            rewritten_date = verify.verify_case("quiz-finalization", final, initial, None)

            self.assertTrue(result["passed"], result)
            self.assertFalse(rewritten_date["passed"], rewritten_date)

    def test_knowledge_gap_weak_assessment_passes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, workspace = self.copy_fixture(Path(directory))
            assessment = workspace / "assessments" / "2026-08-30-threads.md"
            assessment.write_text(
                """# Assessment: Threads

- Date: 2026-08-30
- Status: complete
- Topics:
  - [[lessons/threads.md|Threads]]

## Topic: Threads

- Path: lessons/threads.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-27
- Starting Last Tested: —

### Question 1

Prompt: Explain the core thread model.
Learner answer: I don't know.
Feedback: This is a genuine knowledge gap; threads share process memory while retaining execution state.
Diagnosis: knowledge-gap — the learner did not attempt a guess.
Remediation prompt: Try the distinction after feedback.
Revised answer: I still cannot explain it.
Follow-up feedback: The core gap remains.
Evidence: Recall remains absent after bounded remediation.
Expected key points: Shared address space and separate execution state.
Result: weak

### Topic Outcome

Grounding: verified
Result: weak
Evidence summary: Core recall remains absent after feedback.

## Misconceptions

No misconception; a knowledge gap remains.

## Summary

Threads needs review.

## Progress Changes

- [[lessons/threads.md|Threads]]: `Needs Validation` → `Needs Review`
"""
            )
            self.complete_progress(workspace, "Threads", "Needs Review")
            self.append_history(workspace, "2026-08-30-threads", "Threads", "weak")

            result = verify.verify_case("quiz-unknown", final, initial, None)

            self.assertTrue(result["passed"], result)

    def test_real_interruption_shape_preserves_atomic_progress(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, workspace = self.copy_fixture(Path(directory))
            (workspace / "assessments" / "2026-08-30-processes-and-threads.md").write_text(
                """# Assessment: Processes and Threads

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

Prompt: Explain a process.
Learner answer: A running program instance.
Feedback: Correct recall.
Evidence: Independent recall.
Expected key points: Running instance and state.
Result: strong

### Question 2

Prompt: Apply isolation to a new crash.
Learner answer: Other private memory remains protected.
Feedback: Correct transfer.
Evidence: Applied to a new scenario.
Expected key points: Memory boundary and limitation.
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

Prompt: Explain the thread sharing model.
"""
            )

            result = verify.verify_case("quiz-interruption", final, initial, None)

            self.assertTrue(result["passed"], result)

    def test_unresolved_grading_dispute_stays_in_progress(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, workspace = self.copy_fixture(Path(directory))
            prepare_quiz_fixture.prepare("quiz-dispute", initial)
            prepare_quiz_fixture.prepare("quiz-dispute", final)
            (workspace / "assessments" / "2026-08-30-context-switch.md").write_text(
                """# Assessment: Context Switch

- Date: 2026-08-30
- Status: in-progress
- Topics:
  - [[notes/context-switch.md|Context Switch]]

## Topic: Context Switch

- Path: notes/context-switch.md
- Starting status: Needs Validation
- Starting Last Learned: 2026-08-27
- Starting Last Tested: —

### Question 1

Prompt: Compare a context switch and a privilege-mode switch.
Learner answer: They are always the same operation.
Feedback: The note does not establish that equivalence.
Diagnosis: concept-confusion — two adjacent operations were treated as identical.
Dispute: The learner disputes the correction and requests persisted-source evidence.
Resolution: Unresolved; persisted workspace sources do not settle the claim.
"""
            )

            result = verify.verify_case("quiz-dispute", final, initial, None)

            self.assertTrue(result["passed"], result)

    def test_concurrent_progress_edit_blocks_finalization_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            initial, final, _ = self.copy_fixture(Path(directory))
            prepare_quiz_fixture.prepare("quiz-conflict", initial)
            prepare_quiz_fixture.prepare("quiz-conflict", final)
            events = Path(directory) / "events.jsonl"
            events.write_text(
                json.dumps(
                    {
                        "type": "message_end",
                        "message": {
                            "role": "assistant",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Concurrent edit conflicts with the recorded baseline; reconcile it before resuming.",
                                }
                            ],
                        },
                    }
                )
                + "\n"
            )

            result = verify.verify_case("quiz-conflict", final, initial, events)

            self.assertTrue(result["passed"], result)


if __name__ == "__main__":
    unittest.main()
