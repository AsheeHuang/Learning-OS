# Skill Testing Practices for `/learn`

## Conclusion

**Some mature skill authors do use headless model runs plus deterministic assertions, but it is not common practice across skill repositories.** Anthropic's `skill-creator`, obra's Superpowers integration tests, Next.js documentation evals, and LangChain Deep Agents provide strong examples. Other experienced authors rely mainly on static checks, deterministic tests of bundled scripts or generated templates, and manual beta feedback. A headless behavioral harness is therefore an emerging best practice, not a baseline convention.

For Learning OS, the smallest useful design is a testing pyramid: validate cheap structural invariants first, then run a few black-box `/learn` cases in disposable vaults and grade the resulting Markdown filesystem deterministically. Do not build a runtime, service, database, or Node toolchain. Use the host agent's existing headless CLI, a Bash runner, and a small Python verifier.

## Common practice, best practice, and benchmarking

| Level | What authors actually do | What it establishes |
|---|---|---|
| **Common practice** | Validate `SKILL.md` frontmatter and directory shape; run bundled scripts; inspect a few realistic uses manually; test generated templates or artifacts where applicable. | The package is well formed and deterministic helpers work. It does **not** prove correct routing or useful agent behavior. |
| **Best practice** | Run saved prompts in fresh, isolated workspaces; separate skill loading from task success; compare with-skill against no-skill or the prior skill; inspect tool traces and files; use deterministic assertions wherever possible; repeat stochastic cases; retain failures as regression fixtures; use human or model judgment only for semantic qualities. | The skill causally improves realistic behavior and preserves its contract across changes. |
| **Research-grade benchmarking** | Use isolated/containerized environments, oracle solutions, multiple models and repeated trials, paired treatment arms, blinded/calibrated judges, held-out cases, confidence intervals, cost/latency reporting, and versioned full trajectories. | Reproducible comparative claims across skills, models, or systems. This is disproportionate for the MVP. |

Static validation is intentionally narrow. The Agent Skills reference validator checks frontmatter and naming constraints but does not execute instructions or assess outputs ([specification](https://agentskills.io/specification), [validator source](https://github.com/agentskills/agentskills/blob/main/skills-ref/src/skills_ref/validator.py)). OpenAI's public skill creator similarly requires real script execution but provides a lighter generic behavioral workflow than Anthropic's ([OpenAI skill creator](https://github.com/openai/skills/blob/main/skills/.system/skill-creator/SKILL.md)).

Headless-plus-assertion examples are nevertheless concrete:

- Anthropic runs clean with-skill and baseline cases, grades explicit assertions, aggregates results, and separately repeats positive and negative trigger queries ([skill creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md), [trigger runner](https://github.com/anthropics/skills/blob/main/skills/skill-creator/scripts/run_eval.py)).
- Superpowers wraps `claude -p`, checks tool traces and generated files, and reserves expensive end-to-end tests for workflows that need them ([test helpers](https://github.com/obra/superpowers/blob/main/tests/claude-code/test-helpers.sh), [integration test](https://github.com/obra/superpowers/blob/main/tests/claude-code/test-subagent-driven-development-integration.sh)).
- Next.js runs the same project fixtures as baseline and documentation-treatment arms, then verifies resulting source and retains JSONL traces ([eval documentation](https://github.com/vercel/next.js/blob/canary/evals/README.md)).
- LangChain Deep Agents uses tiny skill fixtures and asserts tool-call order, arguments, final text, and file mutations ([skill eval source](https://github.com/langchain-ai/deepagents/blob/main/libs/evals/tests/evals/test_skills.py)).

By contrast, public repositories from Matt Pocock and Learn Anything show manual feedback or deterministic template/protocol tests without model-driven behavioral gates ([Matt Pocock beta workflow](https://github.com/mattpocock/skills/blob/main/skills/in-progress/README.md), [Learn Anything template tests](https://github.com/ChenChenyaqi/learn-anything/blob/main/packages/cli/test/skill-templates.test.ts)). This mixed evidence is why headless behavioral testing should be called best practice, not common practice.

## Smarter patterns than prose matching

1. **Grade durable effects, not eloquence.** For `/learn`, the observable vault is the primary oracle. Verify required files and directories, map/progress bijection, allowed statuses, relative paths, the 25-concept cap, no generated lessons or notes, and no writes outside `Learn/<topic>/`. First-party guidance recommends deterministic graders for objective outcomes and traces for process diagnosis ([OpenAI skill eval guide](https://developers.openai.com/blog/eval-skills), [Anthropic agent eval guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)).
2. **Test preservation with before/after fixtures.** Resume and recovery cases should compare protected human-authored text, existing statuses, dates, resources, and history prefixes byte-for-byte. This targets `/learn`'s highest-risk behavior more reliably than an LLM rubric.
3. **Separate routing, process, and outcome.** Whether the skill loaded, which tools ran, and whether the workspace is valid are different facts. Because `/learn` is explicitly invoked and disables model invocation, trigger precision/recall is not an MVP priority; one explicit-load smoke test is enough. Workspace validity remains the release gate.
4. **Use paired runs for causal claims.** The same prompt and initial vault should run with the current skill and without it—or against the previous released skill. Report both absolute pass rate and per-case lift. SkillsBench uses this treatment-variable design because skills can help some tasks and harm others ([paper](https://arxiv.org/abs/2602.12670), [repository](https://github.com/benchflow-ai/skillsbench)).
5. **Repeat only where nondeterminism matters.** One trial is adequate for quick smoke feedback; use two or three fresh trials for release candidates. Repeating trigger queries estimates routing rate, while repeating output cases estimates behavioral consistency; these should not be conflated.
6. **Promote failures, do not replay outputs.** Save the redacted initial vault, user prompt, host/model/skill versions, trace, resulting files, and verifier result. A regression test reruns from the same initial state; merely re-grading an old output cannot detect changed behavior.
7. **Constrain semantic judging.** Mission fidelity, map relevance, and source-trust explanations may need human or model review. Use one narrow rubric per dimension after deterministic preflight, retain `unknown`, and keep it nonblocking until calibrated. LLM judges have documented position, verbosity, and self-preference biases ([MT-Bench judge study](https://proceedings.neurips.cc/paper_files/paper/2023/file/91f18a1287b398d378ef22505bf41832-Paper-Datasets_and_Benchmarks.pdf)).

## Smallest effective architecture for Learning OS

```text
evals/learn/
├── README.md                 # case intent and protocol coverage
├── cases/
│   └── <case>/
│       ├── PROMPT.md         # realistic invocation and user turns
│       └── vault/            # initial Markdown workspace fixture
├── run.sh                    # copies fixture; invokes one existing host CLI
└── verify.py                 # filesystem/Markdown assertions; emits JSON
```

Keep prompts and initial learner state as Markdown. Treat traces, snapshots, and JSON reports as generated evidence, not canonical learning state. `run.sh` should create a temporary vault, copy one fixture, invoke the already-installed host in headless/machine-readable mode, capture its native trace, call `verify.py`, and preserve failed-run artifacts. The verifier should use only Python's standard library unless a real parsing need justifies an existing dependency.

Start with **six black-box cases**:

1. missing topic asks for it and writes nothing;
2. fresh setup creates the exact workspace after supplied mission answers;
3. research-unavailable setup leaves honest resource headings and invents no citations;
4. complete resume preserves the workspace and adds no meaningless history event;
5. partial recovery adds a missing file/directory/progress row while preserving existing bytes and statuses;
6. bounded mapping accepts a justified narrow map and rejects or pauses before exceeding 25 concepts.

The deterministic gate should report at least: workspace validity, preservation, map/progress bijection, boundary-write safety, pass/fail by case, host/model/skill revision, wall time, and trace path. Run verifier-only checks on every relevant change; run three to five one-trial behavioral smoke cases locally or on selected CI changes; run all six with two or three trials and a prior-skill comparison before release. Add a semantic review sample only after these gates work.

Do **not** begin with Promptfoo, DeepEval, SkillsBench containers, a SaaS observability platform, cross-model matrices, or a generic adapter framework. Those become worthwhile only when Learning OS needs provider comparison, shared dashboards, or publishable benchmark claims. The proposed Bash/Python harness supplies the missing behavioral evidence while preserving the project's Markdown-first, host-executed architecture.
