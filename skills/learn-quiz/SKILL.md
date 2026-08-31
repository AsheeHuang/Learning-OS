---
name: learn-quiz
description: Validate one or more Learning OS topics through a durable, interactive assessment and update progress from recorded evidence.
disable-model-invocation: true
argument-hint: "[topics...]"
---

# Learn Quiz

Run the formal Learning OS mastery gate. A lesson self-check is formative; only a completed, grounded assessment can produce `Mastered`.

## Protocol

Read the **Assessment**, **`/learn-quiz`**, **Progressive context loading**, and **Protocol invariants** sections of [the Learning OS protocol](references/learning-protocol.md). It owns paths, schemas, statuses, outcomes, transitions, and recovery; this skill adds quiz-specific execution gates.

## Workflow

### 1. Resolve or recover

Read `PROGRESS.md` and assessment metadata first; resolve exactly one `Learn/<topic>/` workspace.

Interrupted finalization has priority over a new attempt. Once an artifact contains `Progress Changes` or any intended effect was applied, finish it idempotently or stop on a concurrent-edit conflict; it can no longer be abandoned.

Otherwise resume an exact matching `in-progress` assessment or confirm one fixed, non-empty set of eligible `Needs Validation` or `Needs Review` rows. With no arguments, offer in-progress work before `Needs Validation` candidates. Recommend one to three topics and write nothing before selection is unambiguous.

### 2. Preflight and plan coverage

Verify the workspace files and selected lesson or note paths. Read the selected artifacts and relevant persisted sources; load mission, map, or recent history only when they affect scope, difficulty, or prior misconceptions. Record each topic's grounding as `verified` or `unverified`; assessment never researches or teaches missing material.

For each topic, derive a coverage plan from its instructional sections:

- Select three to five independent learning targets that together represent the learning objective, explanation, and application or practice. Merge repeated expressions of the same idea, not distinct ideas.
- Use two targets only when the artifact is genuinely atomic. If more than five are necessary, show the plan and ask the learner to confirm the longer assessment.
- Mark targets required by the learning objective as `core`; mark additional breadth as `supporting`.
- Assign one concise open-ended question to each target and record its exact source heading. The set must contain independent **recall** and **transfer** evidence.

Show the targets and planned question count before creating a new assessment.

### 3. Create or resume the artifact

Use the protocol filename and lifecycle rules. Before the first prompt, persist the fixed topic set, each progress-row baseline, grounding state, and numbered coverage plan. Keep one canonical `Coverage status`, written with the topic outcome.

On resume, continue from the first incomplete field. Re-display an unanswered persisted prompt exactly; never regenerate completed work.

### 4. Collect independent evidence

Finish one topic before the next and ask one question at a time.

Before displaying a question, persist its `Coverage target`, `Dimension`, exact `Source section`, and complete `Prompt`. Persist the raw learner answer immediately. Ask at most one neutral clarification when the answer is ambiguous.

Collect every first-pass answer for the topic before revealing verdicts or correct models; otherwise early feedback can teach answers needed by later questions. After the first pass:

1. Grade each answer against its source section.
2. Persist and show concise feedback, expected key points, and evidence for every question.
3. Add a diagnosis only when a gap exists, explaining the mistaken assumption and missing premise.
4. Offer at most one remediation question for the highest-priority unresolved core target. Preserve both answers. Successful remediation caps the topic at `partial`.

An explicit `I don't know` is a `knowledge-gap`. Do not convert the assessment into a lesson, add research, or use hidden/subagent grading.

### 5. Decide the topic outcome

`Coverage status: complete` means every planned target received durable first-pass evidence; it does not mean every answer was correct.

- `strong`: every target succeeded independently, including recall and transfer, with verified grounding and no remediation dependency.
- `partial`: core direction is understood, but a supporting target is incomplete, remediation was needed, or grounding is unverified.
- `weak`: a core target remains absent or a critical misconception remains.

Resolve grading disputes only from persisted workspace sources. If those sources cannot settle the dispute, keep the assessment `in-progress`.

### 6. Finalize crash-safely

After every topic has a supported outcome:

1. Persist the intended `Progress Changes`.
2. In one targeted edit, update only selected progress rows and `Last Tested`; preserve `Last Learned`, `Current Focus`, and unrelated rows.
3. Append exactly one assessment-linked history event with each topic's outcome and actual transition.
4. Mark the assessment `complete`.

On recovery, compare every current row with the recorded baseline and intended result. Apply only missing effects, preserve already-applied effects, and stop without mutation on any other value.

### 7. Hand back

Report demonstrated strengths, unresolved gaps, the assessment path, and resulting statuses. Suggest `/learn-lesson` for `partial` or `weak` gaps, but do not start it automatically.

## Completion gate

Finish only when the artifact is `complete`, every coverage target has durable evidence, progress and history match the recorded outcomes, and no unselected or protected state changed.
