# 
Learning OS

> **Top-down and graph-based learning with Claude Code, Codex, or any skill-capable AI agent — turning what you learn into an Obsidian-native knowledge system.**

Learning OS is an open-source learning protocol built on top of existing AI agents.

It uses agents like **Claude Code** and **Codex** to organize learning files, explain concepts, test understanding, and grow a connected knowledge base over time.

Everything is stored as plain Markdown and designed to work naturally with **Obsidian**.

---

## What is Learning OS?

Learning OS helps you learn through a simple loop:

```text
See the map
→ Pick what matters
→ Learn
→ Branch into questions
→ Expand the knowledge graph
→ Test yourself
→ Update progress
```

You choose what to explore. The agent expands only the parts you need instead of generating an entire course up front.

When you encounter something you don't understand, you don't have to leave your current learning flow.

You can send that question to a separate subagent:

```text
process.md
    │
    ├── continue reading
    │
    └── "What is a context switch?"
              │
              ▼
           subagent
              │
              ▼
      context-switch.md
              │
              └── linked back to process.md
```

The result becomes part of your knowledge graph instead of disappearing into another chat.

---

## Core Ideas

- 🗺️ **Top-down learning** — start with a high-level knowledge map
    
- 🌱 **Progressive expansion** — generate deeper material when needed
    
- 🌿 **Parallel exploration** — send unfamiliar concepts or deep dives to subagents without interrupting your main learning flow
    
- 🔗 **Graph learning** — connect concepts, dependencies, and relationships
    
- 📝 **Persistent knowledge** — turn explanations and explorations into linked Markdown notes
    
- 🧠 **Active recall** — use quizzes and flashcards to verify understanding
    
- 📈 **Track understanding** — measure knowledge, not just completion
    
- 🧹 **Continuous organization** — find duplicates, missing links, and structural issues
    
- 🪨 **Obsidian-native** — support Markdown, wiki links, Graph View, and spaced repetition
    
- 🤖 **Bring your own agent** — use Claude Code, Codex, or another capable agent
    

---

## How It Works

```text
Claude Code / Codex
        │
        ▼
   Learning Skills
        │
        ├── Main learning flow
        │
        └── Subagent explorations
        │
        ▼
   Learning Workspace
        │
   ┌────┴────┐
   ▼         ▼
Obsidian    Web UI
```

The agent handles reasoning, research, subagents, and file operations.

Learning OS defines how learning content, progress, relationships, questions, and assessments are organized in a portable, human-readable workspace.

---

## Planned Skills

| Skill               | Description                                                                 |
| ------------------- | --------------------------------------------------------------------------- |
| `/learn-init`       | Create or continue a topic and generate its knowledge map                   |
| `/learn-lesson`     | Deep-dive into the concept you are currently learning                       |
| `/learn-note`   | Send a question or sub-topic to a subagent, create a note, and link it back |
| `/learn-quiz`       | Test understanding and update learning progress                             |
| `/learn-flashcards` | Generate Obsidian Spaced Repetition-compatible flashcards                   |
| `/learn-review`     | Find weak or stale knowledge to revisit                                     |
| `/learn-organize`   | Review notes for duplicates, missing links, and structural issues           |

---

## Status

Learning OS is currently in the **early design and prototyping stage**.

The first goal is to build learning skills that work well inside Claude Code and Codex, using a shared Obsidian-compatible workspace.

---

## Inspiration

- [Learn Anything](https://github.com/ChenChenyaqi/learn-anything)
    
- [Teach Skill by Matt Pocock](https://github.com/mattpocock/skills)
    
- [Bloom](https://github.com/Li-Evan/Bloom)
    
- [DeepTutor](https://github.com/HKUDS/DeepTutor)
    

---

## License

MIT
