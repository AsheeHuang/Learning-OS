# Phase 1 `/learn-init`: Primary-Source Reference Analysis

## Scope and conclusion

This note compares two reference implementations with the current Learning OS contract: [the Learning OS MVP protocol](../learning-protocol.md), especially its `/learn-init` skill contract, and [the Phase 1 section of the direction review](../learning-os-direction-review.md#phase-1實作-learn-init).

The references solve different parts of the problem:

- **Teach** is strongest at learner intent, trusted-source curation, durable continuity, and selective learning evidence.
- **Learn Anything** is strongest at bounded map generation, canonical-state discipline, deterministic projections, and choice-oriented first-run UX.
- **Learning OS should not combine their storage models wholesale.** Its defining constraint is already settled: editable Markdown is the durable source of truth. Phase 1 should borrow workflow rules, not introduce Learn Anything's JSON runtime or Teach's HTML artifact model.

The recommended MVP remains small: initialize or safely resume one mission-grounded Markdown workspace, create a bounded breadth-first map and matching `Unexplored` progress rows, curate a few trusted resources when possible, then return control to the learner without generating a lesson.

### Research basis

This is a static source analysis. Upstream links are pinned to the repository revisions inspected so that the cited behavior does not move with `main`:

- Teach: `mattpocock/skills` at [`6654f6b`](https://github.com/mattpocock/skills/tree/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76)
- Learn Anything: `ChenChenyaqi/learn-anything` at [`83b33cb`](https://github.com/ChenChenyaqi/learn-anything/tree/83b33cb6f897c3ee26b341abee800976dfa34b66)

The analysis concerns source contracts and prompts, not measured learner outcomes. Both products rely substantially on host-agent compliance.

## 1. What Teach does

Teach treats a directory of durable files as the teaching workspace. A fresh agent can continue by reading those files; the conversation is not the durable state. Its declared workspace includes a mission, trusted resources, learning records, lessons, references, and assets. The skill itself uses relative paths and assumes the current directory is the intended workspace, which makes the state model portable but leaves destination selection underspecified. See [`skills/productivity/teach/SKILL.md`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/productivity/teach/SKILL.md) and the repository's setup/usage account in [`docs/productivity/teach.md`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/docs/productivity/teach.md).

### Initialization behavior

1. **Mission before teaching.** If the mission is absent or unclear, Teach interviews the learner before creating a lesson. Later teaching should trace back to the mission. The format is intentionally short: `Why`, `Success looks like`, `Constraints`, and `Out of scope`; one workspace has one mission, vague outcomes should be challenged, and later changes require confirmation. See [`skills/productivity/teach/MISSION-FORMAT.md`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/productivity/teach/MISSION-FORMAT.md).
2. **Trusted resources before unsupported content.** Teach treats model memory as untrusted. `RESOURCES.md` is curated rather than accumulated: entries have a URL, an annotation, and an explicit `Use for`; weak or irrelevant entries are pruned and missing coverage is recorded as a gap. Its two principal buckets are `Knowledge` and `Wisdom (Communities)`. See [`skills/productivity/teach/RESOURCES-FORMAT.md`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/productivity/teach/RESOURCES-FORMAT.md).
3. **Evidence is selective.** Small numbered learning records capture demonstrated non-trivial understanding, disclosed prior knowledge, corrected misconceptions, and mission changes. Merely covering material is not evidence. Contradicted records are superseded instead of erased. See [`skills/productivity/teach/LEARNING-RECORD-FORMAT.md`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/productivity/teach/LEARNING-RECORD-FORMAT.md).
4. **Vocabulary is earned rather than pre-generated.** A glossary term is added only after the learner can use it correctly; definitions stay concise and canonical. See [`skills/productivity/teach/GLOSSARY-FORMAT.md`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/productivity/teach/GLOSSARY-FORMAT.md).
5. **Invocation is explicitly human-controlled.** The skill disables implicit model invocation in both its skill frontmatter and Codex-facing metadata. See [`skills/productivity/teach/agents/openai.yaml`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/skills/productivity/teach/agents/openai.yaml) and [`.agents/invocation.md`](https://github.com/mattpocock/skills/blob/6654f6b60cd9d5be8b54c6fafe44346dabeb3b76/.agents/invocation.md).

### Limits relevant to Phase 1

Teach does **not** define a systematic first-session baseline assessment, a bounded bootstrap source count, deterministic topic-folder identity, collision handling, a breadth-first map, a progress state machine, an append-only history, a formal assessment artifact, or an assessment-only mastery gate. Its HTML-first lesson/reference presentation and asset system are also not a fit for an Obsidian-first MVP. These absences matter because Learning OS must specify them itself rather than describe them as Teach behavior.

## 2. What Learn Anything does

Learn Anything is an installer plus a set of agent workflow prompts. Its TypeScript CLI installs skills and host command shims; when invoked, the host agent creates and updates project-local artifacts under `.learn/topics/<topic>/`. See [`README.md`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/README.md) and [`packages/cli/src/core/init.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/init.ts).

### Topic and state behavior

1. **A versioned JSON record is canonical.** `state.json` models topic → domains → concepts; concepts carry status, confidence, counts, and recent dates. `knowledge-map.md` and status output are derived views and are not read back as canonical input. The state types and validation live in [`packages/cli/src/core/learn-protocol/types.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/learn-protocol/types.ts) and [`schema.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/learn-protocol/schema.ts); rendering and status validation live in [`scripts/render.mts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/scripts/render.mts) and [`scripts/status.mts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/scripts/status.mts).
2. **The initial map is bounded.** The topic workflow asks for 2–3 levels, breadth before depth, independently learnable concept names, and roughly 10–15 concepts for narrow topics or 15–25 for broad topics. Domains group trackable concepts; optional details are descriptive rather than independently tracked. See [`templates/workflows/learn-topic.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/templates/workflows/learn-topic.ts).
3. **First-run UX returns agency quickly.** A new topic is shown as a compact landscape and followed by concrete actions; a resumed topic gets status counts and prioritized next choices rather than a repeated setup flow. The effective pattern is orient → summarize → offer a few actions → let the learner choose. See the new and existing topic workflows in [`learn-topic.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/templates/workflows/learn-topic.ts).
4. **Generated learning artifacts precede chat presentation.** Explain and practice workflows save the self-contained session artifact before echoing it conversationally, reducing drift between chat and persisted state. See [`learn-explain.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/templates/workflows/learn-explain.ts) and [`learn-practice.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/templates/workflows/learn-practice.ts).
5. **Generative and deterministic work are separated.** The agent proposes maps, explanations, exercises, and grading judgments; copied scripts validate state, initialize folders, render maps/status, and validate quiz structure. The standalone helpers use Node built-ins for portability. See [`packages/cli/src/scripts/utils.mts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/scripts/utils.mts) and [`init-sessions.mts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/scripts/init-sessions.mts).
6. **Protocol evolution removes old canonical paths.** Its v0-to-v1 migration validates the replacement state, makes backups, removes obsolete canonical inputs, and regenerates views. See [`packages/cli/src/core/learn-protocol/migrate.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/learn-protocol/migrate.ts).

### Limits relevant to Phase 1

Learn Anything has no persisted learner mission, baseline, constraints, success criteria, time budget, milestones, or plan history. Relationships and prerequisites are requested by prompts but absent from canonical state, so they can be re-invented on each run. Confidence changes are model-assigned heuristics without evidence IDs. Agents edit `state.json` directly before post-write validation; there is no transactional mutation API. Review priority is a prompt formula rather than a deterministic scheduler.

Its delivery surface also has implementation defects that Learning OS should not inherit: command names differ among README, generated skills, and installer output; only four host command adapters exist despite broader tool claims; generated files overwrite unconditionally; and target-path/tool detection can inspect the wrong directory. The relevant primary paths are [`templates/workflows/_shared.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/templates/workflows/_shared.ts), [`command-generation/registry.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/command-generation/registry.ts), [`config.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/core/config.ts), and [`utils/file-system.ts`](https://github.com/ChenChenyaqi/learn-anything/blob/83b33cb6f897c3ee26b341abee800976dfa34b66/packages/cli/src/utils/file-system.ts).

## 3. What Learning OS should adopt in Phase 1

The current protocol and direction review already settle most of the product boundary correctly. The table distinguishes settled contracts from the small adaptations still needed.

| Adopt now | Source pattern | Fit with the Learning OS protocol | Phase 1 form |
|---|---|---|---|
| Mission as the initialization gate | Teach | Extends the existing `MISSION.md` and `/learn-init` steps | Ask only for missing intent and baseline information; persist it before map generation; create no lesson. |
| One topic per durable workspace | Teach | Matches `Learn/<topic>/` and file-based continuity | Resolve the vault-root-relative destination before writing; distinguish fresh, resumed, and conflicting workspaces. |
| Concise outcome and scope language | Teach | Matches `Why`, outcomes, success criteria, constraints, and out of scope | Keep answers learner-authored and operational; reject vague goals such as “understand everything.” |
| Claimed knowledge is not mastery | Teach | Matches the assessment-only `Mastered` invariant | Store initial capability claims in the mission, but initialize every map concept as `Unexplored`; only later assessment evidence can establish mastery. |
| Curated, annotated source set | Teach | Already adopted by `RESOURCES.md` | Keep the protocol's two-to-four-source budget, primary/official-source preference, annotation, and `Use for` scope; record empty headings honestly if research is unavailable. |
| Bounded breadth-first decomposition | Learn Anything | Matches `MAP.md` as choices rather than generated course content | Use area → independently learnable concept as the MVP shape, with a soft size bound selected in Decision 3 below. Details remain prose, not progress rows. |
| Choice-oriented completion | Learn Anything | Matches the Phase 1 final step | After files are consistent, show the map, summarize whether the workspace is new/resumed and whether sources were curated, then ask for one first concept. |
| Canonical current state and consistency checks | Learn Anything | Matches `PROGRESS.md` as the sole current-status source | Keep Markdown canonical. Before completion, verify one progress row per unique map concept, valid paths/statuses, and preserved existing states. Do not add JSON. |
| Artifact-first visible output | Learn Anything | Matches file-based continuity | Persist and verify `MISSION.md`, `MAP.md`, `PROGRESS.md`, `HISTORY.md`, and `RESOURCES.md` before presenting their result in chat. |
| Idempotent resume | Both | Required by the direction review's Phase 1 acceptance criteria | Read existing mission/progress/map first; ask only for missing fields; never regenerate a valid map, reset progress, or rewrite history merely because `/learn-init` was invoked again. |
| Explicit human invocation | Teach | Appropriate for a state-creating command | Keep `/learn-init` user-invoked and expose one canonical command spelling. |

### Recommended Phase 1 sequence

Subject to the decisions below, the smallest coherent sequence is:

1. Resolve and display `Learn/<topic>/`; classify the run as **new**, **resume**, or **conflict** before writing.
2. On resume, read existing durable state and repair only objectively missing initialization artifacts. On a new workspace, collect the compact mission and baseline first.
3. Curate a bounded source set when research is available. Failure to retrieve sources remains explicit and non-blocking.
4. Generate one bounded breadth-first map grounded in the mission and, when available, the curated sources. Generate no lesson or note.
5. Initialize exactly one `Unexplored` progress row per unique map concept; initialize append-only history and required directories.
6. Run consistency checks, then present the map and offer the learner the next choice.

This changes neither the Markdown source-of-truth decision nor the Phase 1 artifact set.

## 4. What Learning OS should reject or defer

### Reject for the MVP

- **Current-directory-as-topic routing.** Teach's ambiguous relative workspace must not replace Learning OS's explicit vault-root `Learn/<topic>/` boundary.
- **JSON as canonical state.** Learn Anything's `state.json` plus generated Markdown projection conflicts with the project's defining human-editable Markdown contract. `PROGRESS.md` remains canonical.
- **Raw model-assigned confidence as mastery.** Numeric confidence and practice-count thresholds are not adequate assessment evidence and conflict with the protocol's `/learn-quiz`-only mastery gate.
- **Model edits to hidden state followed only by post-write validation.** Phase 1 has no need for a hidden record that can diverge from human-readable state.
- **Implicit prerequisites or personalized recommendations presented as persisted facts.** If relationships are not represented and reviewed, the agent should not pretend they are deterministic.
- **HTML-first lessons, shared stylesheets, and reusable asset bootstrapping.** They add a second presentation system to an Obsidian-first product.
- **Multiple spellings for the same command or unsupported host-capability claims.** Phase 1 should advertise one `/learn-init` entry point and only behavior shared by supported hosts.
- **Pre-generating lessons, notes, glossary entries, or reference documents.** Both the current protocol and evidence-gated learning principles favor lazy creation after learner choice.

### Defer until the core learning loop is proven

- **Stable concept IDs and typed prerequisite/relationship edges.** These may eventually improve reproducible recommendations, but the direction review explicitly keeps automatic dependency-graph work out of the MVP. Path-qualified lesson links are sufficient in Phase 1.
- **Deterministic renderer/validator scripts and transactional mutation commands.** Learn Anything demonstrates their value, but adding a TypeScript runtime now would widen a skill-and-Markdown MVP. Start with explicit completion checks and fixtures; add code only after repeated failures justify it.
- **Glossary lifecycle and Teach-style learning-record files.** Their evidence discipline is useful, but Learning OS already has mission, history, and assessments. A new artifact type needs a named owner and retrieval contract before it is added.
- **Review scheduling, spaced repetition, flashcards, scoring models, and confidence decay.** Neither reference supplies a trustworthy complete scheduler, and the direction review places these after the four-command core loop.
- **Installer migration machinery, multi-host adapter registries, dashboards, and web UI.** These solve distribution or later product concerns, not Phase 1 `/learn-init` correctness.
- **Concurrency controls.** Atomic writes and locking become important with multiple writers, but Phase 1 can explicitly assume one active writer per topic workspace.

## 5. High-impact Phase 1 decisions still requiring user input

Most architectural questions in the direction review are now answered by `docs/learning-protocol.md`: workspace boundary, path-qualified links, progress statuses, assessment-only mastery, Markdown canonical state, and the artifact set should not be reopened. Four decisions still materially affect `/learn-init` acceptance behavior.

### Decision 1 — What baseline must the mission capture?

**Unresolved:** `MISSION.md` has `Current Level`, but neither the protocol nor Phase 1 acceptance criteria define whether `/learn-init` must elicit concrete prior capabilities, known gaps/misconceptions, and desired challenge level. Teach demonstrates why prior-knowledge claims matter but does not systematically collect them; Learn Anything omits learner intent almost entirely.

**Recommended MVP choice:** keep the existing headings and require `Current Level` to contain two concise parts: claimed prior exposure/capabilities and known gaps. Treat both as learner claims, never as mastery. Do not add a placement quiz or a new baseline artifact in Phase 1.

**Acceptance consequence:** a fresh `/learn-init` cannot generate the map until outcome, constraints, concrete current capability, and known gaps are either supplied or explicitly recorded as unknown/none stated.

### Decision 2 — Should resource curation precede map generation?

**Unresolved:** Teach's philosophy is resource-first. The current `/learn-init` sequence creates the map before resources, while the resource contract says research failure must not block map creation.

**Recommended MVP choice:** when research is available, curate the existing two-to-four-source budget **before** generating the map and use it to check terminology and coverage. When research is unavailable or fails, create honest empty headings and continue. This preserves non-blocking completion without grounding the map in known-unverified model memory when sources are readily available.

**Acceptance consequence:** tests must distinguish “research available and used before map generation” from “research unavailable, recorded honestly, map still completed.”

### Decision 3 — What is the measurable map bound?

**Unresolved:** Learning OS says “a few high-level areas” and breadth-first; Learn Anything supplies concrete but broad-topic-dependent limits. Without a bound, `/learn-init` can produce either an unusably shallow list or a full curriculum dump.

**Recommended MVP choice:** exactly two tracked levels—area headings and concept links—with **10–20 total concepts as a soft target and 25 as a hard maximum**. A concept must be independently selectable for a future lesson. Do not persist dependency edges in Phase 1.

**Acceptance consequence:** maps over the hard cap or with nested tracked sub-concepts fail completion; legitimately narrow topics may contain fewer than ten concepts.

### Decision 4 — How should topic collisions and inconsistent resumes behave?

**Unresolved:** preserving the learner's topic wording means `OS`, `os`, and `Operating Systems` may become distinct folders. The protocol also requires preserving human edits but does not say what `/learn-init` should do when an existing mission conflicts with the requested topic, a map row is malformed, or progress contains an orphaned human-added concept.

**Recommended MVP choice:** trim surrounding whitespace but otherwise preserve the requested display name and directory spelling. Before creating a new folder, inspect `Learn/` for case-insensitive exact-name collisions only; show the resolved path and ask before using or creating a conflicting destination. On resume, auto-repair only objectively derivable omissions (missing required directories/files or a missing progress row for an existing map link). Preserve and report malformed or orphaned human state rather than deleting or silently rewriting it.

**Acceptance consequence:** Phase 1 needs explicit fresh, exact-resume, interrupted-setup, case-collision, and inconsistent-human-edit scenarios.

## Bottom line

Teach supplies the best **initialization ethics**: mission first, sources are curated, evidence is earned, and files provide continuity. Learn Anything supplies the best **workflow mechanics**: bound the map, make current state canonical, validate before presenting, and return a small set of choices. Learning OS should combine those behaviors inside its already-chosen Markdown protocol—not combine the references' artifact trees or runtimes.

Once the four decisions above are recorded in the protocol, Phase 1 `/learn-init` is sufficiently specified for implementation and acceptance testing without adding a backend, schema runtime, dependency graph, scheduler, or lesson generation.
