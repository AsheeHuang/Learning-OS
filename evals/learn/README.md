# `/learn-init` behavioral evals

These evals execute the real Skill through Pi in disposable vaults, then grade durable filesystem effects with deterministic assertions.

```text
fixture → headless Pi → generated vault → verify.py → result JSON
```

## Requirements

- Bash
- Python 3 standard library
- An authenticated `pi` CLI
- A configured Pi model, or `--model <provider/model>`

No Node runtime or custom agent runtime is used. The runner disables extensions and web tooling so the default cases are reproducible; `RESOURCES.md` must therefore keep empty `Knowledge` and `Further Reading` sections rather than populate remembered citations.

## Run

Run every case once:

```bash
evals/learn/run.sh
```

Run one case:

```bash
evals/learn/run.sh --case fresh-topic
```

Repeat release-candidate cases:

```bash
evals/learn/run.sh --runs 3 --model <provider/model>
```

Results are written under `.eval-results/learn/<timestamp>/` and ignored by Git. Every run retains its initial vault, resulting vault, Pi JSONL event trace, stderr, and verification report.

## Cases

- `fresh-topic`: creates a complete workspace from supplied mission information.
- `partial-resume`: repairs an interrupted workspace while preserving human-authored state.
- `missing-mission`: asks for missing mission information and writes nothing.

Prompts and high-level expectations live in `skills/learn-init/evals/evals.json`. Resume input state lives under `fixtures/partial-resume/vault/`.

## Verification

`verify.py` checks observable protocol behavior:

- required state files and artifact directories;
- writes remain under `Learn/`;
- bounded two-level map;
- path-qualified lesson links;
- MAP/PROGRESS bijection and valid statuses;
- fresh topics begin `Unexplored` with blank dates;
- `/learn-init` creates no lesson or note files;
- required resource headings and initialized history;
- resume preserves mission, map, existing statuses, and dates.

Run verifier unit tests without a model:

```bash
cd evals/learn
python3 -m unittest -v test_verify.py
```

## Evaluation layers

The deterministic verifier is the release gate. Mission fidelity, map relevance, concept granularity, and source quality remain semantic review dimensions. Add a model or human grader only after deterministic checks pass.
