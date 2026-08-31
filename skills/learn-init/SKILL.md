---
name: learn-init
description: Start or resume a persistent Learning OS topic workspace and create its mission, breadth-first map, progress state, history, and trusted resources without generating lessons.
disable-model-invocation: true
argument-hint: "<topic>"
---

# Learn Init

Create or resume the top-level workspace for one learning topic. This skill charts the subject before teaching it; `/learn-lesson` creates lesson content later.

## Source of truth

Read [Learning OS protocol](references/learning-protocol.md) before writing. It owns workspace paths, formats, statuses, links, and invariants; this skill adds the `/learn-init` sequence.

## 1. Resolve the topic

Take the topic from the invocation. If missing, ask what the learner wants to learn and stop. Treat the current working directory as the Obsidian vault root and use:

```text
Learn/<topic>/
```

Preserve the learner's topic wording as the directory name. Use the human-facing concept title as the filename for lessons and notes, preserving spaces and meaningful punctuation such as `&` (for example, `User Kernel Mode & System Call.md`).

## 2. Inspect before asking or writing

Check whether `Learn/<topic>/` exists and which protocol files are present.

### Complete workspace

When all five protocol files exist:

1. Read `MISSION.md`, `PROGRESS.md`, and `MAP.md`.
2. Verify one progress row per map concept, preserving statuses and human edits.
3. Summarize the mission, current focus, status counts, and map areas.
4. Show the map and ask what the learner wants to study next.

A complete workspace is a resume: do not repeat mission questions, regenerate the map, reset progress, or append a resume event.

### Partial workspace

Treat missing files as an interrupted setup:

1. Read every existing file before reconstructing anything.
2. Ask only for missing mission information.
3. Create only missing files, headings, directories, or progress rows.
4. Derive missing rows from `MAP.md` and initialize only those rows as `Unexplored`.
5. Preserve existing rows, dates, statuses, links, resources, and history.

The recovery is complete when the workspace satisfies the same checks as a fresh setup.

## 3. Capture the mission

For a fresh workspace, ask one compact set of questions. Reuse answers already supplied and ask only for missing information:

1. Why do you want to learn this topic?
2. What is your current level?
3. What target level or outcome do you want?
4. What should you be able to do when this succeeds?
5. What constraints should shape the learning plan?
6. What is out of scope?

Wait for the learner's answer before researching or generating the map. If there are no constraints or exclusions, record `None stated`.

Write `MISSION.md` using the protocol format. Keep it concise and preserve the learner's intent rather than inflating it into a course description.

## 4. Ground the map in trusted sources

Create `RESOURCES.md` with `Knowledge` and `Further Reading` headings before `MAP.md`.

When research tools are available, curate two to four high-trust sources:

- Prefer primary sources and maintained official documentation.
- Give each source a short trust explanation and `Use for:` scope.
- Put grounding sources under `Knowledge` and optional depth under `Further Reading`.
- Use them to check the map's terminology, areas, and scope.

A source is verified only if fetched or read during this run, supplied by the learner, or already persisted. Memory does not verify a source. If research is unavailable or fails, leave both headings empty and continue without adding remembered titles or URLs.

## 5. Chart a bounded breadth-first map

Generate `MAP.md` from the mission and curated resources when available.

- Follow the protocol's two-level, breadth-first map format and 10–20 concept target (25 maximum).
- If more than 25 concepts are needed, ask whether to split the topic.
- Use topic-workspace-relative Wiki links with aliases and human-facing title filenames; links may target lessons that do not exist.
- Include only mission-relevant concepts and no declared out-of-scope material.
- Do not add dependency edges or separately tracked subtopics in Phase 1.

Do not create lesson or note files. The map lets the learner choose where to begin; it is not a pre-generated course.

## 6. Initialize current state

Create `PROGRESS.md` using the protocol table. Set `Current Focus` to `—`, add exactly one row per unique map link, copy each target into `Path`, initialize new concepts as `Unexplored`, and set both dates to `—`. Verify that map concepts and progress rows match without duplicates.

## 7. Finish the workspace

Create these directories without learning content:

```text
lessons/
notes/
assessments/
```

Create `HISTORY.md` if needed and append one setup event after the workspace is consistent. Record the date, creation or recovery, and initialized concept count. Keep history append-only.

## 8. Hand control to the learner

Present the map, workspace path, resource status, and the available next steps: create lessons, explore a side concept, or view progress. Ask which map concept to study first. Do not invoke another skill or create a lesson or note in the same run.

## Completion check

Finish only when the workspace is complete and internally consistent, the mission and map reflect the learner's scope, resources are verified or honestly empty, no lesson or note was created, history was preserved, and the learner saw the map and was asked where to begin.
