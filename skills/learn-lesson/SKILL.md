---
name: learn-lesson
description: Teach one or more mapped Learning OS concepts by writing a short, source-grounded lesson that ends in three just-right self-check questions, then persist the lessons and learning state.
disable-model-invocation: true
argument-hint: "<concept>... (optional)"
---

# Learn Lesson

Teach one or more mapped concepts by writing lessons with three formative self-check questions. The lesson is an artifact, not a live one-question-at-a-time conversation.

## Source of truth

Read [Learning OS protocol](references/learning-protocol.md) before touching a workspace. It owns paths, formats, statuses, links, history, and invariants; this skill adds the `/learn-lesson` sequence.

## 1. Resolve one or more concepts

Invocation:

- `/learn-lesson <Concept>...` — one or more mapped concepts.
- `/learn-lesson` — list `Unexplored` concepts and ask the learner to confirm a subset. If none are pending, report and stop.

Resolve every named concept:

1. Use the current `Learn/<topic>/` workspace, or inspect immediate `Learn/*/PROGRESS.md` files otherwise.
2. Match names case-insensitively against aliases and exact paths; each must match exactly one progress row.
3. Ask about ambiguous or unmatched names before writing. Never add an unmapped lesson.

Require `MISSION.md`, `MAP.md`, `PROGRESS.md`, `HISTORY.md`, and `RESOURCES.md`; report missing files and stop.

A selected concept already `Learning` is a resumption: finish its partial draft or pending state update without restarting.

## 2. Load teaching context

Use the protocol's progressive context order, reading the mission, progress, map, target lessons, relevant resources, and history only when it affects difficulty. Read other artifacts only for needed prerequisites, learner evidence, or relationships.

## 3. Persist the start

Each selected concept follows:

```text
Unexplored → Learning → Needs Validation
```

Move it to `Learning` immediately before writing and set `Current Focus` to its path-qualified link. Preserve `Last Learned`, `Last Tested`, and unrelated rows. Revisiting `Mastered` also moves to `Learning`; only `/learn-quiz` can restore `Mastered`.

Concepts whose write has not begun stay `Unexplored`.

## 4. Design one learning win per lesson

Choose one observable objective per lesson that advances the mission and fits the learner's level:

> After this lesson, the learner can …

Keep the lesson inside that objective. Prefer a transferable mental model over a fact list, use the learner's context when it clarifies the concept, and calibrate from mission, progress, and history without a live diagnostic.

## 5. Ground in trusted sources

Ground important claims:

- inspect sources rather than citing titles from memory;
- prefer trusted workspace sources;
- research a high-trust source when tools are available and sources are insufficient;
- otherwise ask the learner for a source or mark the material unverified.

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

The lesson must be mission-grounded, bounded to one objective, source-grounded or honestly unverified, and contain exactly three transfer-oriented questions with separate answers at the end. Tell the learner to attempt the questions before reading the answers. Include path-qualified links and citations. Use visual Markdown features when they reduce effort. Preserve human-written material and update only the lesson; `PROGRESS.md` owns status.

Two constraints on how the explanation reads:

- Explain in plain language people actually speak. Avoid abstract jargon when a concrete word says the same thing. Keep a technical term only when it is the concept being taught, and define it plainly on first use.
- Use analogies. Anchor each new idea to something the learner already knows, then say where the analogy breaks down.

## 7. Present with diagrams, tables, and markdown features

Use visual Markdown features when they reduce effort:

- Use Mermaid for standalone diagrams and ASCII for small inline diagrams.
- Use tables for comparisons, steps, or state mappings.
- Use HTML comments for non-rendered notes and callouts/highlights for key ideas.
- Do not force a visual where prose is clearer.

## 8. Self-check questions — quality bar

The three questions in `Practice` are formative checks:

- Require transfer: apply the concept, predict an outcome, compare a related concept, or correct a misconception rather than copy the explanation. Calibrate to mission, progress, and history.
- Give no hints or partial answers. Prefer open-ended prompts; comparable options must not leak the answer.

Keep concise key points or model answers in a separate `Self-Check Answers` section.

## 9. Multi-lesson runs and subagents

For multiple concepts, delegate one lesson per concept in parallel when subagents are available. They may write only lesson artifacts; the main agent verifies them and performs all progress and history updates. Without subagents, write the same artifacts sequentially.

## 10. Finalize or resume

After verifying each lesson, set its row to `Needs Validation`, update only `Last Learned`, preserve `Last Tested`, and keep `Current Focus` on the current or last completed concept. Append one event per lesson:

```markdown
## YYYY-MM-DD

### Learned: <Concept>

- Topic: [[lessons/<Concept Title>.md|<Concept>]]
- Status: `Learning` → `Needs Validation`
- Artifact: [[lessons/<Concept Title>.md|<Concept>]]
- Evidence: <self-check questions written; key points the lesson covers>
```

Append beneath today's heading when present and preserve earlier history. A verified lesson is evidence of a lesson, not mastery.

On interruption, leave untouched concepts `Unexplored`, mid-write concepts `Learning` with their partial drafts, and verified lessons `Needs Validation`; resume from durable state.

## 11. Hand back

State the learning win, saved lesson paths, and `Needs Validation` status. Mention `/learn-quiz` as the validation step. Do not start further lessons.

## Completion check

Finish only when every selected concept has a verified, bounded, source-grounded or honestly unverified lesson written in plain language with at least one analogy and exactly three separated-answer self-checks; state and history match; untouched and mid-write concepts retain their proper states; `Current Focus` is correct; and no topic is `Mastered`.
