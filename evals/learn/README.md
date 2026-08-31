# Learning OS behavioral evals

These evals execute real Learning OS skills through Pi in disposable Obsidian vaults, then grade durable filesystem and transcript effects with deterministic assertions.

```text
fixture → headless Pi session → generated vault → verify.py → result JSON
```

## Requirements

- Bash
- Python 3 standard library
- An authenticated `pi` CLI
- A configured Pi model, or `--model <provider/model>`

No Node runtime or custom agent runtime is used. Initialization cases disable extensions and web tooling, so `RESOURCES.md` must keep honest empty sections rather than populate remembered citations. Quiz cases use a retained Pi session to deliver scripted learner turns one at a time.

## Run

Run initialization cases:

```bash
evals/learn/run.sh
```

Run all quiz cases:

```bash
evals/learn/run.sh --suite quiz
```

Run all note cases:

```bash
evals/learn/run.sh --suite note
```

Run one case or repeat release-candidate cases:

```bash
evals/learn/run.sh --suite quiz --case quiz-strong
evals/learn/run.sh --suite quiz --runs 3 --model <provider/model>
```

Use `--suite all` to run both suites. Results are written under `.eval-results/learn/<timestamp>/` and ignored by Git. Every run retains its initial vault, resulting vault, Pi JSONL event trace, stderr, session files, and verification report.

## Initialization cases

- `fresh-topic`: creates a complete workspace from supplied mission information.
- `partial-resume`: repairs an interrupted workspace while preserving human-authored state.
- `missing-mission`: asks for missing mission information and writes nothing.

## Quiz cases

- `quiz-candidates`: lists only eligible topics and writes nothing before confirmation.
- `quiz-strong`: records grounded recall and transfer, then produces `Mastered`.
- `quiz-remediation`: preserves correction turns and caps the outcome at `partial`.
- `quiz-unknown`: distinguishes a knowledge gap from an incorrect guess.
- `quiz-resume`: resumes an exact unanswered prompt and finalizes a multi-topic assessment atomically.
- `quiz-abandon`: preserves an abandoned attempt and creates a suffixed fresh attempt.
- `quiz-unverified`: caps unsupported content at `partial`.
- `quiz-ambiguity`: blocks cross-workspace ambiguity before any write.
- `quiz-interruption`: stops between topics and verifies prompt-before-answer snapshots plus atomic progress.
- `quiz-dispute`: persists an unresolved grading dispute without finalizing or researching.
- `quiz-conflict`: detects a concurrent progress edit against the durable baseline and writes nothing.
- `quiz-finalization`: repairs an interrupted finalization without duplicate effects.

## Note cases

- `note-create`: creates a side note from Current Focus and preserves the main path.
- `note-resume`: completes a partial note without overwriting human content or duplicating history.
- `note-promotion`: verifies that MAP.md changes only after explicit promotion.
- `note-unverified`: verifies honest source handling when research is unavailable.
- `note-ambiguity`: blocks writes until the workspace/source is unambiguous.

Prompts and expectations live in each skill's eval metadata. Scripted quiz turns live in `quiz-cases.json`. Resume input state is created from the bounded fixtures under `fixtures/`.

## Verification

`verify.py` checks observable protocol behavior:

- workspace and path boundaries;
- assessment lifecycle and topic grouping;
- durable prompt, raw answer, feedback, diagnosis, remediation, and evidence fields;
- grounded qualitative outcomes;
- atomic and idempotent progress transitions;
- preserved `Last Learned`, `Current Focus`, unrelated rows, and append-only history;
- no state writes before candidate confirmation or after abandonment;
- per-turn vault snapshots proving prompt-before-answer durability and intermediate atomicity;
- concurrent-edit conflict detection from persisted row baselines;
- transcript checks proving feedback and the correct answer are visible in chat, not only stored in Markdown.

Run verifier unit tests without a model:

```bash
cd evals/learn
python3 -m unittest -v test_verify.py test_quiz_verify.py
```

The deterministic verifier is the release gate. Question quality, source relevance, and feedback usefulness remain semantic review dimensions until a calibrated grader exists.
