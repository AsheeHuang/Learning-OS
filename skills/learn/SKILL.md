---
name: learn
description: Start or resume a persistent Learning OS topic workspace and create its mission, breadth-first map, progress state, history, and trusted resources without generating lessons.
disable-model-invocation: true
argument-hint: "<topic>"
---

# Learn

Create or resume the top-level workspace for one learning topic. This skill charts the subject before teaching it; `/explain` creates lesson content later.

## Source of truth

Read the bundled [Learning OS protocol](references/learning-protocol.md) before writing files. Its workspace paths, file formats, status vocabulary, link rules, and invariants are authoritative. This skill defines the `/learn` sequence only.

## 1. Resolve the topic

Take the topic from the invocation. If it is missing, ask what the learner wants to learn and stop until they answer.

Treat the current working directory as the Obsidian vault root. Resolve the topic workspace as:

```text
Learn/<topic>/
```

Preserve the learner's topic wording as the directory name. Use short kebab-case filenames for concepts inside the workspace.

## 2. Inspect before asking or writing

Check whether `Learn/<topic>/` exists and which protocol files are present.

### Complete workspace

When `MISSION.md`, `MAP.md`, `PROGRESS.md`, `HISTORY.md`, and `RESOURCES.md` exist:

1. Read `MISSION.md`, then `PROGRESS.md`, then `MAP.md`.
2. Validate that every map concept has one progress row. Preserve every existing status and human edit.
3. Summarize the mission, current focus, status counts, and available map areas.
4. Show the map and ask what the learner wants to study next.

A complete workspace is a resume, not a fresh setup. Do not repeat mission questions, regenerate the map, reset progress, or append a meaningless resume event.

### Partial workspace

Treat missing files as an interrupted setup:

1. Read every file that exists before reconstructing anything.
2. Ask only for mission information not already persisted.
3. Create only missing files, headings, directories, or progress rows.
4. Derive missing progress rows from `MAP.md` and initialize only those rows as `Unexplored`.
5. Preserve existing rows, dates, statuses, map links, resources, and history.

The recovery is complete when the workspace satisfies the same checks as a fresh setup.

## 3. Capture the mission

For a fresh workspace, ask one compact set of questions. Reuse answers already supplied in the user's prompt and ask only for missing information:

1. Why do you want to learn this topic?
2. What is your current level?
3. What target level or outcome do you want?
4. What should you be able to do when this succeeds?
5. What constraints should shape the learning plan?
6. What is out of scope?

Wait for the learner's answer before researching sources or generating the map. If they have no constraints or exclusions, record `None stated` rather than repeatedly asking.

Write `MISSION.md` using the protocol format. Keep it concise and preserve the learner's intent rather than inflating it into a course description.

## 4. Ground the map in trusted sources

Create `RESOURCES.md` with `Knowledge` and `Further Reading` headings before generating `MAP.md`.

When research or web tools are available, curate two to four high-trust sources:

- Prefer primary sources, maintained official documentation, and respected foundational material.
- Give each source a short trust/usefulness explanation and a `Use for:` scope.
- Put sources that should ground the map and later explanations under `Knowledge`; put optional depth under `Further Reading`.
- Use the selected sources to check the map's terminology, major areas, and scope.

A source counts as verified only if you fetched or read it during this run, or it was already supplied by the learner or persisted in the workspace. Parametric memory does not verify a source. When research is unavailable or fails, leave both headings empty; do not add remembered source titles or URLs. Continue to the map without letting resource gathering block setup.

## 5. Chart a bounded breadth-first map

Generate `MAP.md` from the mission and the curated resources when available.

- Use exactly two tracked levels: meaningful area headings and independently learnable concept links.
- Aim for 10–20 total concepts, with a hard maximum of 25; a legitimately narrow topic may use fewer than 10.
- If the mission needs more than 25 concepts, ask whether to split it into multiple learning topics instead of dumping a full curriculum.
- Prefer breadth over depth: show the shape of the subject without expanding every branch.
- Use topic-workspace-relative Wiki links with aliases, such as `[[lessons/processes.md|Processes]]`.
- Links may target lesson files that do not exist yet.
- Include only concepts relevant to the mission and keep declared out-of-scope material out.
- Do not add dependency edges or separately tracked subtopics in Phase 1.

Do not create lesson or note files while charting. A successful map lets the learner choose where to begin; it is not a pre-generated course.

## 6. Initialize current state

Create `PROGRESS.md` using the protocol table.

- Set `Current Focus` to `—` until the learner chooses a concept.
- Add exactly one row for every unique concept link in `MAP.md`.
- Copy the link target into the `Path` column.
- Initialize every new map concept as `Unexplored`.
- Set `Last Learned` and `Last Tested` to `—`.

Before continuing, compare `MAP.md` and `PROGRESS.md`: every map concept must have one progress row, and no row may be duplicated.

## 7. Finish the workspace

Create these directories without adding learning content:

```text
lessons/
notes/
assessments/
```

Create `HISTORY.md` if needed and append one setup event only after the fresh or recovered workspace is internally consistent. Record the date, workspace creation or recovery, and the number of map concepts initialized. History remains append-only.

## 8. Hand control to the learner

Present the high-level map in the response. Briefly state:

- where the workspace was created or resumed;
- whether trusted resources were curated or left empty;
- that map links are choices, not generated lessons.

Then list the possible next steps:

- create one or more main-path lessons from selected map concepts;
- explore an unfamiliar term or side concept without interrupting the main path;
- view current learning progress and topics waiting for validation or review.

End by asking which map concept the learner wants to study first. Do not invoke another skill or create a lesson or note in the same run.

## Completion check

Finish only when all conditions hold:

- `Learn/<topic>/` contains every required protocol file and directory.
- `MISSION.md` reflects the learner's stated purpose and constraints.
- `MAP.md` is breadth-first and contains no generated lesson content.
- Every map concept appears exactly once in `PROGRESS.md` as `Unexplored`, except statuses preserved during resume or recovery.
- `HISTORY.md` contains no rewritten prior events.
- `RESOURCES.md` contains verified sources or honest empty headings.
- `lessons/` and `notes/` contain no files created by `/learn`.
- The learner has been shown the map, given the possible next steps, and asked where to begin.
