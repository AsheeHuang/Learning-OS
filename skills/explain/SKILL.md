---
name: explain
description: Teach one or more mapped Learning OS concepts by writing a short, source-grounded lesson that ends in three just-right self-check questions, then persist the lessons and learning state.
disable-model-invocation: true
argument-hint: "<concept>... (optional)"
---

# Explain

Teach one or more concepts that already exist on a Learning OS map. Teaching is artifact-based: the lesson itself teaches, and each lesson ends in three self-check questions the learner uses to verify their own understanding. There is no live one-question-at-a-time conversation.

## Source of truth

Read the bundled [Learning OS protocol](references/learning-protocol.md) before touching a workspace. Its workspace paths, lesson format, status vocabulary, link rules, history format, and invariants are authoritative. This skill defines the `/explain` sequence on top of it.

## 1. Resolve one or more concepts

The invocation takes one of two forms:

- `/explain <Concept>...` — one or more named concepts.
- `/explain` — no arguments. List the pending concepts (status `Unexplored` in `PROGRESS.md`) and ask the learner to confirm a subset or all of them. When nothing is pending, report that there is nothing to explain and stop.

Resolve every named concept against the workspace rules:

1. When the current directory is inside a topic workspace (`Learn/<topic>/`), use it.
2. Otherwise, inspect the immediate `Learn/*/PROGRESS.md` files and match each concept against topic link aliases, paths, and filename slugs, case-insensitively.
3. A concept is usable only when exactly one progress row matches it.
4. Ambiguous or unmatched names are raised as questions before any write begins; the learner confirms the final set. Never silently add an unmapped lesson.

Require `MISSION.md`, `MAP.md`, `PROGRESS.md`, `HISTORY.md`, and `RESOURCES.md`. When any file is missing, name what is missing and stop so the workspace can be recovered first.

A selected concept that is already `Learning` is a resumption, not a fresh lesson: finish its partial draft or complete its pending state update, and do not restart from scratch.

## 2. Load only teaching context

Read once, in this order:

1. `MISSION.md`
2. `PROGRESS.md`
3. `MAP.md`
4. the target lessons, when they exist
5. the `RESOURCES.md` entries relevant to the concepts
6. recent `HISTORY.md` evidence when it changes lesson difficulty

Read other artifacts only when they supply a prerequisite, learner evidence, or a relationship a lesson needs. Do not load the whole workspace.

## 3. Persist the start

Each selected concept follows the same per-concept transition:

```text
Unexplored → Learning → Needs Validation
```

Move a concept to `Learning` immediately before its lesson write begins, and set `Current Focus` to its path-qualified Wiki link. Preserve `Last Learned`, `Last Tested`, and every unrelated row exactly. A `Mastered` topic being revisited also moves to `Learning`; the completed revisit requires validation again — only `/quiz` can restore `Mastered`.

Concepts whose write has not begun stay `Unexplored`, so an interrupted run resumes cleanly.

## 4. Design one learning win per lesson

Choose one observable objective per lesson that advances the mission and fits the learner's level. A useful objective completes the sentence:

> After this lesson, the learner can …

Keep the lesson inside that objective. Prefer a mental model that transfers over a list of facts. Use the learner's work, interests, or mission as the concrete setting when it genuinely clarifies the concept. Calibrate from existing learner evidence (mission, progress, history); there is no live diagnostic step.

## 5. Ground in trusted sources

Important claims are grounded:

- inspect the source rather than citing its title from memory;
- prefer the workspace's trusted sources;
- research a high-trust source when tools are available and the workspace lacks one;
- otherwise ask the learner for a source or label the material unverified.

Never invent a citation.

## 6. Write the lesson

Write one file per concept at the target row's `Path` using the protocol headings:

```markdown
# <Concept>

## Why This Matters

## Learning Objective

## Explanation

## Example

## Practice

## Related Concepts

## Sources

## Self-Check Answers
```

The artifact stands on its own after the run ends:

- `Why This Matters` ties to the mission;
- one observable objective;
- the smallest sufficient model;
- one worked example;
- `Practice` holds exactly three self-check questions (see the quality bar);
- path-qualified Wiki links for related concepts;
- inline citations with a sources list;
- `Self-Check Answers` at the very end, clearly separated, with a one-line instruction to attempt the questions first.

When a lesson exists, preserve human-written material and make targeted updates. Status never lives in the lesson; `PROGRESS.md` owns it.

## 7. Self-check questions — quality bar

The three questions in `Practice` are the lesson's formative check:

- **Just-right difficulty.** Each question requires transfer — applying the concept to a new situation, predicting an outcome, comparing with a related concept, or correcting a misconception — and cannot be answered by copying a sentence from the explanation or example. Calibrate difficulty to the learner's level from mission, progress, and history evidence.
- **No hints.** Question text contains no scaffolding, no partial answers, and no leading clues. Prefer open-ended prompts; if options are used, keep their length and format comparable so they do not leak the answer.

The `Self-Check Answers` section holds concise key points or model answers, kept clearly apart from the questions.

## 8. Multi-lesson runs and subagents

When the run covers more than one concept:

- **With subagents:** delegate lesson authoring — one subagent per concept, run in parallel. Each subagent reads the mission, progress, map, and relevant resources and writes its lesson artifact under the same contract (headings, three self-check questions, separated answers, sources, path-qualified links). Subagents never edit `PROGRESS.md`, `HISTORY.md`, or any state file. The main agent verifies each artifact against the quality bar, then performs all state updates and history writes.
- **Without subagents:** the main agent writes the same artifacts sequentially.

Delegation changes execution, never the file contract.

## 9. Complete or interrupt

A lesson is complete when its artifact is verified: protocol headings, one bounded objective, three just-right self-check questions with separated answers, source-grounded or honestly unverified, and path-qualified links. Completing an artifact is evidence that a lesson exists, not durable mastery.

On interruption:

- verified lessons keep `Needs Validation` and their history events;
- concepts whose write never began stay `Unexplored`;
- a concept left mid-write stays `Learning` with its partial draft, and a later run resumes it from durable state.

## 10. Persist completion

After a lesson artifact is verified:

1. In `PROGRESS.md`, set only that concept's row to `Needs Validation`.
2. Set `Last Learned` to today's ISO date; leave `Last Tested` unchanged.
3. Keep `Current Focus` on the concept currently being written, ending on the last completed concept of a run.
4. Append one event at the end of `HISTORY.md`:

```markdown
## YYYY-MM-DD

### Learned: <Concept>

- Topic: [[lessons/<slug>.md|<Concept>]]
- Status: `Learning` → `Needs Validation`
- Artifact: [[lessons/<slug>.md|<Concept>]]
- Evidence: <self-check questions written; key points the lesson covers>
```

When today's date heading exists, append only the event beneath it. Preserve all earlier history.

## 11. Hand back to the learner

State the tangible win(s), where each lesson was saved, and that the topics are `Needs Validation`, not `Mastered`. Invite follow-up questions (learner-initiated) and mention that `/quiz` is the validation step. Do not start further lessons in the same run.

## Completion check

Finish only when:

- every selected concept is either a verified lesson or an explicit stop decision;
- each lesson uses the protocol headings and ends in exactly three just-right self-check questions with a separated `Self-Check Answers` section;
- lessons are mission-grounded, bounded, source-grounded or honestly marked unverified, and use path-qualified links;
- per-concept state is consistent: verified lessons are `Needs Validation` with `Last Learned` updated and `Last Tested` preserved; untouched concepts remain `Unexplored`; mid-write concepts remain `Learning`;
- one append-only history event exists per verified lesson;
- `Current Focus` points at the last completed concept;
- no topic was marked `Mastered`;
- no interactive Q&A loop was entered.
