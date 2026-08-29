# `/explain` Skill Spec

Status: ready-for-human
Date: 2026-08-28
Owner: phase2 worktree, Learning OS

## Context

Learning OS runs the loop Map → Learn → Explore → Validate on a plain-Markdown
Obsidian workspace. `/learn` charts the map and initializes progress; `/explain`
turns one or more mapped concepts into short, source-grounded lessons, then
persists each lesson and its state change.

The teaching model is artifact-based: the lesson itself teaches. There is no
live one-question-at-a-time conversation; instead each lesson ends with three
self-check questions the learner uses to verify their own understanding.

The MVP protocol (`docs/learning-protocol.md`) stays authoritative and is
unchanged by this effort. Everything below is skill-local behavior on top of
it.

## Decisions recorded

- **Discard and rewrite.** The previous uncommitted `skills/explain/` draft is
  thrown away; the skill is written fresh against this spec.
- **Protocol untouched.** The teaching model, batch flow, self-check format,
  and subagent delegation live in the skill, not in
  `docs/learning-protocol.md`. The bundled reference is re-synced to the
  committed protocol.
- **Spec home.** The feature spec follows the repo's issue-tracker convention:
  `.scratch/<feature-slug>/spec.md`.
- **Static delivery.** Deliver the skill files for manual testing; no live
  run, no commit. Commit and follow-ups happen after the learner tests it.
- **No wayfinder map.** The effort is small enough for one spec + one skill.
- **Teaching model.** Single and batch runs both write lessons only; no
  interactive Q&A loop. Each lesson ends with three self-check questions.
- **Answers included.** The three questions are followed by a clearly
  separated answers section at the very end of the lesson, so the learner can
  check after attempting.
- **Batch support.** `/explain` accepts multiple concepts or a pending list;
  multiple lessons may be delegated to subagents in parallel.
- **Subagents are an optimization, not a dependency.** When the host has
  subagents, multi-lesson runs delegate one lesson per subagent; without them,
  the main agent writes the same artifacts sequentially. The file contract is
  identical either way.
- **Status timing.** A concept moves to `Needs Validation` as soon as its
  lesson is verified written; the self-check and `/quiz` come later.
- **Lesson presentation.** Lessons prefer diagrams and tables where the
  concept lends itself (Mermaid for standalone diagrams, ASCII for inline
  ones) and use Markdown comments, highlights, and quotes/callouts to express
  emphasis and annotation.

## Destination

> One or more mapped concepts, each turned into a single bounded lesson ending
> in three just-right self-check questions, with the lesson persisted, the
> topic moved `Learning → Needs Validation`, and history appended — ready for
> `/quiz` to validate later.

## Scope

In scope:

- Resolving one or more mapped concepts (named or pending list).
- Writing short lessons with protocol headings, ending in three self-check
  questions plus a separated answers section.
- Applying presentation rules inside lessons: diagrams and tables where the
  concept suits, plus Markdown comments, highlights, and quotes/callouts.
- Persisting `Learning` per concept while writing, then `Needs Validation` +
  `Last Learned` per verified lesson, plus one append-only history event per
  lesson.
- Delegating lesson authoring to subagents for multi-lesson runs, with a
  main-agent fallback that produces identical artifacts.
- Resuming interrupted lessons from durable state.
- Grounding important claims in trusted sources or labeling them unverified.

Out of scope (this phase):

- Live interactive teaching (one-question-at-a-time conversation).
- Auto-exploration of side concepts (that is `/explore`).
- Any change to `docs/learning-protocol.md`.
- Assessment or mastery status (`/quiz` owns `Mastered`).
- Flashcards, review scheduling, or other post-MVP features.

## Behavior contract

### 1. Resolve one or more concepts

Invocation takes one of two forms:

- `/explain <Concept>...` — one or more named concepts.
- `/explain` — no arguments; list the pending concepts (status `Unexplored`
  from `PROGRESS.md`) and ask the learner to confirm a subset or all of them.
  When nothing is pending, report that there is nothing to explain and stop.

Resolve every named concept against the workspace rules:

1. When the current directory is inside a topic workspace (`Learn/<topic>/`),
   use it.
2. Otherwise, inspect the immediate `Learn/*/PROGRESS.md` files and match each
   concept against topic link aliases, paths, and filename slugs,
   case-insensitively.
3. A concept is usable only when exactly one progress row matches it.
4. Ambiguous or unmatched names are raised as questions before any write
   begins; the learner confirms the final set. Never silently add an unmapped
   lesson.

Require `MISSION.md`, `MAP.md`, `PROGRESS.md`, `HISTORY.md`, and
`RESOURCES.md`. When any file is missing, name what is missing and stop so the
workspace can be recovered first.

A selected concept that is already `Learning` is a resumption, not a fresh
lesson: finish its partial draft or complete its pending state update, and do
not restart from scratch.

### 2. Load only teaching context

Read once, in order: `MISSION.md`, `PROGRESS.md`, `MAP.md`, the target lessons
when they exist, the relevant `RESOURCES.md` entries, and recent `HISTORY.md`
evidence when it changes lesson difficulty. Read other artifacts only when
they supply a prerequisite, learner evidence, or a relationship a lesson
needs. Do not load the whole workspace.

### 3. Persist the start

Each selected concept follows the same per-concept transition:

```text
Unexplored → Learning → Needs Validation
```

Move a concept to `Learning` immediately before its lesson write begins, and
set `Current Focus` to its path-qualified Wiki link. Preserve `Last Learned`,
`Last Tested`, and every unrelated row exactly. A `Mastered` topic being
revisited also moves to `Learning`; the completed revisit requires validation
again (only `/quiz` restores `Mastered`).

Concepts whose write has not begun stay `Unexplored`, so an interrupted batch
resumes cleanly.

### 4. Design one learning win per lesson

Choose one observable objective per lesson that advances the mission and fits
the learner's level. A useful objective completes: *"After this lesson, the
learner can …"* Keep the lesson inside that objective; prefer a transferring
mental model over a list of facts. Calibrate from existing learner evidence
(mission, progress, history); there is no live diagnostic step.

### 5. Ground in trusted sources

Important claims are grounded:

- inspect the source rather than citing its title from memory;
- prefer the workspace's trusted sources;
- research a high-trust source when tools are available and the workspace
  lacks one;
- otherwise ask the learner for a source or label the material unverified.

Never invent a citation.

### 6. Write the lesson

Write one file per concept at the target row's `Path` using the protocol
headings:

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
- `Practice` holds exactly three self-check questions (see the quality bar,
  §8);
- path-qualified Wiki links for related concepts;
- inline citations with a sources list;
- `Self-Check Answers` at the very end, clearly separated, with a one-line
  instruction to attempt the questions first;
- presentation follows the rules in §7 (diagrams, tables, comments,
  highlights, quotes/callouts).

When a lesson exists, preserve human-written material and make targeted
updates. Status never lives in the lesson.

### 7. Lesson presentation rules

Express content visually where the concept lends itself instead of defaulting
to prose:

- **Diagrams.** Prefer a diagram when it lowers cognitive load — mental
  models, flows, state transitions, and concept relationships. Use Mermaid
  for standalone diagrams (rendered natively by Obsidian); use ASCII for
  small or inline diagrams that must read in any plain-text view.
- **Tables.** Use tables for comparisons, steps, and state mappings instead of
  dense prose lists.
- **Comments.** Use HTML comments (`<!-- ... -->`) for non-rendered
  annotation: revision notes, per-section sources, or agent meta.
- **Highlights and quotes.** Use `==highlight==` for key terms; blockquote
  callouts (`> [!note]`, `> [!tip]`, `> [!warning]`, `> [!example]`,
  `> [!question]`) for definitions, key takeaways, warnings, misconceptions,
  and worked examples; blockquotes for quoted source passages.
- The bar is whether it lowers the learner's effort to understand; do not
  force a visual where prose is clearer.

### 8. Self-check questions — quality bar

The three questions are the lesson's formative check, not a conversation:

- **Just-right difficulty.** Each question requires transfer — applying the
  concept to a new situation, predicting an outcome, comparing with a related
  concept, or correcting a misconception — and cannot be answered by copying a
  sentence from the explanation or example. Difficulty is calibrated to the
  learner's level from mission, progress, and history evidence.
- **No hints.** Question text contains no scaffolding, no partial answers, and
  no leading clues. Prefer open-ended prompts; if options are used, keep their
  length and format comparable so they do not leak the answer.

The answers section at the end holds concise key points or model answers, kept
clearly apart from the questions.

### 9. Subagent delegation for multi-lesson runs

When the run covers more than one concept and the host supports subagents,
delegate lesson authoring — one subagent per concept, run in parallel:

- each subagent reads the mission, progress, map, and relevant resources and
  writes its lesson artifact under the same contract (headings, presentation
  rules, three self-check questions, separated answers, sources,
  path-qualified links);
- subagents never edit `PROGRESS.md`, `HISTORY.md`, or any state file;
- the main agent verifies each artifact against the quality bar, then performs
  all state updates and history writes.

When the host lacks subagents, the main agent writes the same artifacts
sequentially. Delegation changes execution, never the file contract.

### 10. Complete or interrupt

A lesson is complete when its artifact is verified: protocol headings, one
bounded objective, presentation rules applied where the concept suits, three
just-right self-check questions with separated answers, source-grounded or
honestly unverified, and path-qualified links. Completing the artifact is
evidence that a lesson exists, not durable mastery.

On interruption:

- verified lessons keep `Needs Validation` and their history events;
- concepts whose write never began stay `Unexplored`;
- a concept left mid-write stays `Learning` with its partial draft, and a
  later run resumes it from durable state.

### 11. Persist completion

After a lesson artifact is verified:

1. In `PROGRESS.md`, set only that concept's row to `Needs Validation`.
2. Set `Last Learned` to today's ISO date; leave `Last Tested` unchanged.
3. Keep `Current Focus` on the concept currently being written, ending on the
   last completed concept of a batch.
4. Append one event at the end of `HISTORY.md`:

```markdown
## YYYY-MM-DD

### Learned: <Concept>

- Topic: [[lessons/<slug>.md|<Concept>]]
- Status: `Learning` → `Needs Validation`
- Artifact: [[lessons/<slug>.md|<Concept>]]
- Evidence: <self-check questions written; key points the lesson covers>
```

When today's date heading exists, append only the event beneath it. Preserve
all earlier history.

### 12. Hand back

State the tangible win(s), where each lesson was saved, and that the topics
are `Needs Validation`, not `Mastered`. Invite follow-up questions
(learner-initiated) and mention that `/quiz` is the validation step. Do not
start further lessons in the same run.

## State transitions

| Behavior | Status |
|---|---|
| `/explain` starts writing a concept | `Learning` |
| `/explain` verifies a written lesson | `Needs Validation` |
| `/explain` interrupted mid-write | stays `Learning` |
| `/explain` revisits a `Mastered` topic | `Learning`, then `Needs Validation` |
| `/quiz` (later phase) | the only path to `Mastered` |

## Evals

`skills/explain/evals/evals.json` covers six scenarios:

1. **Fresh single** — `/explain Processes` resolves the unique row, sets
   `Learning` + `Current Focus` before writing, produces one lesson ending in
   three just-right self-check questions with separated answers and using
   diagrams/tables and highlight/quote features where the concept suits, moves
   the row to `Needs Validation` with `Last Learned` updated, appends one
   history event, and never enters an interactive Q&A loop.
2. **Named batch** — `/explain Processes Threads Scheduling` writes all three
   lessons (delegated to subagents when available, sequential fallback
   otherwise), updates each row independently, appends one history event per
   lesson, and leaves `Current Focus` on the last concept.
3. **Pending list** — `/explain` with no arguments lists the `Unexplored`
   concepts, writes only the confirmed subset (or all), and reports "nothing
   to explain" when nothing is pending.
4. **Ambiguous concept** — a concept matching two workspaces raises the
   question and changes nothing before disambiguation.
5. **Mastered revisit** — revisiting a `Mastered` topic moves it through
   `Learning` to `Needs Validation` and never marks it `Mastered`.
6. **Interrupt and resume** — an interrupted batch leaves verified lessons as
   `Needs Validation`, untouched concepts as `Unexplored`, and mid-write
   concepts as `Learning`; a later run resumes from the durable state and
   finishes the remaining lessons.

## Acceptance

The user tests in a dev vault (`scripts/dev.sh --new-env`, optionally
`--agent=pi|cc|codex` to launch the agent inside it), then runs the six eval
scenarios. The skill passes when every completion condition holds and
`scripts/dev.sh --sync-resources --check` reports the explain reference
current. The remaining phases (`/quiz`, `/explore`) follow after the user
confirms.
