# Learning OS

## Problem and vision

Learning OS addresses the weaknesses of chat-based AI learning: conversations are temporary, useful side explorations disappear, learning state is difficult to resume across agents, and reading an explanation is often mistaken for mastery.

The project defines an agent-powered, Obsidian-native learning protocol that runs on existing coding agents such as Claude Code and Codex. The coding agent is the execution engine; Learning OS supplies reusable skills, learning workflows, file conventions, and durable Markdown state. It does not build a custom LLM backend or agent runtime.

The core learning loop is:

```text
Map
  ↓
Learn
  ↓
Explore
  ↓
Validate
```

The learner starts with a broad knowledge map, chooses what to study, expands only the concepts they need, persists side explorations as linked notes, and earns mastery through assessment evidence. The long-term vision is a portable, human-editable learning workspace that any compatible agent can resume and that works naturally as an Obsidian vault.

Live learning data belongs in the user's vault, not this source repository:

```text
Obsidian vault/
└── Learn/
    └── <topic>/
```

Before changing learning behavior or workspace formats, read `docs/learning-protocol.md`. It is the authoritative MVP contract.

## RULES

- Keep agent responses concise. Use ASCII diagrams when they make architecture, workflow, state transitions, or trade-offs easier to understand.
- Think before doing. Inspect the relevant files, distinguish settled decisions from open questions, and understand the intended outcome before editing or implementing.
- Ask the user before acting when a material requirement, product decision, or destructive change is uncertain. Do not block progress with low-impact questions; choose the simplest option consistent with the existing protocol.
- Protect user-owned artifacts and dev vaults: never run destructive cleanup during testing or routine work. First list what it would remove, verify nothing pre-existing is at risk, and get the user's confirmation before anything is deleted.
- Treat Markdown files as durable source of truth. Conversation history and hidden agent state are not authoritative.
- Preserve human edits and existing learning state. Prefer targeted, incremental changes over regeneration.
- Keep the MVP small. Use existing coding-agent capabilities and current project dependencies before introducing scripts, services, schemas, adapters, or abstractions.
- Do not add a custom LLM API, agent runtime, backend service, vector database, graph database, or Web UI unless the project scope explicitly changes.
- Separate the Learning OS source repository from learner workspaces under `Learn/<topic>/`.

## Agent skills

### Issue tracker

Issues live as markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Use the canonical labels `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, and `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository using root-level `CONTEXT.md` and `docs/adr/`. See `docs/agents/domain.md`.
