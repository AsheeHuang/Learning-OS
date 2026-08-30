# Learning OS MVP Protocol

Status: Phase 0

Learning OS is a file protocol executed by an existing coding agent. Markdown files are the source of truth; conversation, model memory, and host-specific state are not.

## 1. Workspace boundary

Treat the agent's current working directory as the Obsidian vault root. Learning OS owns one mother folder:

```text
Learn/
└── <topic>/
```

`/learn-init OS` resolves to `Learn/OS/`. `/learn-init Operating Systems` resolves to `Learn/Operating Systems/`.

The Learning OS source repository contains the protocol and skills. It does not contain a learner's live workspace.

## 2. Topic workspace

Each topic is self-contained:

```text
Learn/<topic>/
├── MISSION.md
├── MAP.md
├── PROGRESS.md
├── HISTORY.md
├── RESOURCES.md
├── lessons/
├── notes/
└── assessments/
```

Post-MVP features may add `flashcards/`, `references/`, and `assets/` without changing the core protocol.

### Roles

- `MISSION.md` grounds teaching decisions in the learner's purpose.
- `MAP.md` is a breadth-first map of topics, including links whose target files do not exist yet.
- `PROGRESS.md` is the only source of current learning status.
- `HISTORY.md` is an append-only event log.
- `RESOURCES.md` is the curated source set used to ground lessons and notes.
- `lessons/` contains learner-selected main-path material.
- `notes/` contains side explorations.
- `assessments/` contains questions, learner answers, feedback, evidence, and outcomes.

## 3. Naming and links

Use short kebab-case Markdown filenames. Keep human-facing titles in title case.

All generated Obsidian links identify the content role with a topic-workspace-relative path and use an alias for the human-facing title:

```markdown
[[lessons/processes.md|Processes]]
[[notes/context-switch.md|Context Switch]]
```

`lessons/processes.md` and `notes/processes.md` may both exist when they are genuinely different artifacts. Use their paths to disambiguate them. Do not duplicate identical content merely because both directories exist.

The `Path` column in `PROGRESS.md` stores the same topic-workspace-relative path without Wiki-link syntax.

## 4. File formats

### `MISSION.md`

Keep the mission short:

```markdown
# Mission: <Topic>

## Why

## Current Level

## Target Level

## Desired Outcomes

## Success Criteria

## Constraints

## Out of Scope
```

A resumed learning session reads the mission before teaching. Mission changes require learner confirmation.

### `MAP.md`

Organize the map into a few high-level areas and list concepts using Wiki links:

```markdown
# <Topic>

## <Area>

- [[lessons/concept.md|Concept]]
```

Track exactly two map levels: area headings and independently learnable concept links. Aim for 10–20 concepts; 25 is the hard maximum. A legitimately narrow topic may use fewer than 10. If the mission needs more than 25 concepts, ask whether to split it into multiple learning topics instead of generating a full curriculum.

A map link does not require its lesson to exist. `/learn-init` creates breadth, not a generated course. Detailed content is created only after the learner selects it. Phase 1 does not persist subtopic status or dependency edges.

Exploration notes stay out of the map unless the concept becomes a useful visible choice on the main learning path.

### `PROGRESS.md`

The `Topics` table is the only source of topic status:

```markdown
# Learning Progress

## Current Focus

[[lessons/concept.md|Concept]]

## Topics

| Topic | Path | Status | Last Learned | Last Tested |
|---|---|---|---|---|
| [[lessons/concept.md|Concept]] | lessons/concept.md | Unexplored | — | — |
```

Use ISO dates (`YYYY-MM-DD`) and exactly these statuses:

- `Unexplored`
- `Learning`
- `Needs Validation`
- `Mastered`
- `Needs Review`

Do not duplicate status into separate `Needs Validation` or `Needs Review` lists.

#### State transitions

```text
/learn-init adds a map topic                  → Unexplored
/learn-lesson starts                          → Learning
/learn-lesson completes                       → Needs Validation
/learn-note creates an exploration note     → Learning
learner explicitly requests validation   → Needs Validation
/learn-quiz result: strong                     → Mastered
/learn-quiz result: partial or weak            → Needs Review
/learn-lesson revisits a topic                 → Learning → Needs Validation
```

Only `/learn-quiz` can produce `Mastered`. Topics not tested by a quiz keep their existing status.

### `HISTORY.md`

History answers "what happened?" It does not represent current state.

Append events at the end of the file. If the latest date heading is today, append another event beneath it; otherwise append a new date heading.

```markdown
## YYYY-MM-DD

### Learned: <Topic>

- Topic: [[lessons/concept.md|Concept]]
- Status: `Learning` → `Needs Validation`
- Artifact: [[lessons/concept.md|Concept]]
- Evidence: <concise learner-specific observation>
```

Record outcomes, artifact links, state changes, and useful learner evidence. Do not copy the conversation transcript.

### `RESOURCES.md`

Follow the core shape of Matt Pocock's Teach `RESOURCES-FORMAT.md`:

```markdown
# <Topic> Resources

## Knowledge

- [<source title>](<url>)
  <Why this is trusted or useful>. Use for: <topics>.

## Further Reading

- [<source title>](<url>)
  <Why this is useful>. Use for: <topics>.
```

`Knowledge` contains sources that should ground explanations. `Further Reading` contains optional depth. Important claims in lessons and notes should use inline citations.

After `MISSION.md` is written and before `MAP.md` is generated, `/learn-init` creates `RESOURCES.md`. When research tools are available, it curates two to four trusted sources and uses them to ground the map's terminology and coverage. A source counts as verified only when the agent fetched or read it during the current run, or when it was already supplied by the learner or persisted in the workspace. Parametric model knowledge does not verify a source. Without research tools, or when research fails, `/learn-init` leaves both resource sections empty before continuing to the map; it must not populate remembered titles or URLs. Empty resources do not block map creation. Before producing an explanation from unverified model knowledge, the agent asks for a source, researches one, or labels the content as unverified.

### Lesson

```markdown
# <Concept>

## Why This Matters

## Learning Objective

## Explanation

## Example

## Practice

## Related Concepts

- [[notes/related-concept.md|Related Concept]]

## Sources
```

A lesson is short, mission-grounded, and aimed at one tangible learning win. It includes retrieval or application practice. Status remains exclusively in `PROGRESS.md`.

### Exploration note

```markdown
# <Concept>

Source: [[lessons/source-concept.md|Source Concept]]

## Question

## Explanation

## Connection to the Source

## Related Concepts

## Sources
```

A note records a side exploration without replacing or interrupting the source lesson. The source lesson and note link to each other.

### Assessment

Use `assessments/YYYY-MM-DD-<topic-slug>.md` for a completed or in-progress quiz session:

```markdown
# Assessment: <Topics>

- Date: YYYY-MM-DD
- Topics:
  - [[lessons/concept.md|Concept]]

## Questions

### 1. <Question>

Prompt:

Learner answer:

Feedback:

Evidence:

Result: strong | partial | weak

## Misconceptions

## Summary

## Progress Changes
```

Create the artifact before asking the first question. Ask one question at a time, then persist the learner's answer, feedback, evidence, and result before continuing. Do not prefill answers or results.

Judge each topic independently:

- `strong`: accurate explanation plus successful comparison, example, prediction, or application; no critical misconception.
- `partial`: core direction is understood, but the explanation, transfer, or distinctions are incomplete.
- `weak`: the core concept cannot yet be explained or is confused with another concept.

Prefer open-ended explanation, comparison, prediction, application, and misconception-correction questions. If multiple-choice questions are used, keep option lengths and formatting comparable so they do not leak the answer.

Update `PROGRESS.md` only after the assessment has enough evidence for that topic. Preserve the status of untested topics.

## 5. Skill contracts

### `/learn-init <topic>`

1. Resolve the workspace as `Learn/<topic>/` and classify it as new or existing.
2. Ask for the mission: why, current level, target level, desired outcomes, success criteria, constraints, and out of scope.
3. Write `MISSION.md`.
4. Create `RESOURCES.md`; curate sources when research is available, otherwise leave honest empty headings.
5. Create a source-grounded, breadth-first `MAP.md` without generating lessons.
6. Initialize every map concept in `PROGRESS.md` as `Unexplored`.
7. Initialize `HISTORY.md` and record workspace creation.
8. Create `lessons/`, `notes/`, and `assessments/`.
9. Verify file and map/progress consistency, then present the map and ask what the learner wants to study first.

Completion criterion: the workspace is internally consistent, no lesson has been generated, and the learner can choose a map concept.

### `/learn-lesson <concept>...`

1. Read `MISSION.md`, `PROGRESS.md`, `MAP.md`, relevant resources, and the target artifact if it exists.
2. Set the target to `Learning` in `PROGRESS.md`.
3. Create or update one short lesson.
4. Teach through an interactive practice prompt and immediate feedback.
5. Persist useful learner evidence in the history event or lesson.
6. Set the topic to `Needs Validation`, update `Last Learned`, and append history.

Completion criterion: one lesson and its practice are complete, persisted state matches the session, and the topic is not marked `Mastered`.

### `/learn-note <note-name>`

The argument names the note to create. The command identifies or asks for the source lesson or concept before writing it.

1. Identify or ask for the source lesson or concept.
2. Read the source artifact, mission, progress, map, and relevant resources.
3. Delegate research when the host supports subagents; otherwise perform the same work in the current agent.
4. Create or update one note using the standard format.
5. Add reciprocal path-qualified links between the source and note.
6. Add or update the progress row as `Learning` and update `Last Learned`.
7. Add the concept to `MAP.md` only when it becomes a useful main-path choice.
8. Append history.

Completion criterion: the exploration is persisted and connected without changing the source lesson's learning status. Subagent and fallback execution produce the same file contract.

### `/learn-quiz [topics...]`

1. Read `PROGRESS.md` first.
2. With explicit topics, select those topics. Without arguments, list all `Needs Validation` topics and let the learner confirm or exclude candidates.
3. Read the selected lessons, notes, mission, and relevant recent history.
4. Create the assessment artifact.
5. Ask one question at a time and persist each answer and feedback turn.
6. Record evidence and a per-topic `strong`, `partial`, or `weak` result.
7. Update tested topics in `PROGRESS.md` and set `Last Tested`.
8. Append a concise history event linking the assessment.

Completion criterion: every selected topic has sufficient recorded evidence, the assessment is complete, and progress/history match its results.

## 6. Progressive context loading

Load only what the current command needs:

1. `MISSION.md`
2. `PROGRESS.md`
3. `MAP.md`
4. the relevant lesson, note, or assessment
5. `RESOURCES.md`
6. recent `HISTORY.md` entries when prior evidence matters

Read deeper references only when the selected topic requires them. Do not load the entire topic workspace by default.

## 7. Protocol invariants

Every host and skill must preserve these rules:

1. Files, not conversation, hold durable learning state.
2. `PROGRESS.md` is the only source of current status.
3. `HISTORY.md` is append-only.
4. Only assessment evidence can produce `Mastered`.
5. Map links may point to lessons that do not exist yet.
6. Exploration creates notes and links without interrupting the main lesson.
7. All generated concept links are path-qualified.
8. Human edits are preserved; agents make targeted updates.
9. Host-specific adapters may change invocation and delegation mechanics, not workspace semantics.
10. No backend, custom model runtime, database, or hidden state is required.
