#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
evals_file="$repo_root/skills/learn-init/evals/evals.json"
skill_file="$repo_root/skills/learn-init/SKILL.md"
verifier="$repo_root/evals/learn/verify.py"
fixtures_root="$repo_root/evals/learn/fixtures"
pi_bin="${PI_BIN:-pi}"
runs=1
selected_case="all"
model="${PI_MODEL:-}"
results_root=""
timeout_seconds="${PI_EVAL_TIMEOUT:-600}"

usage() {
  cat <<'EOF'
Usage: evals/learn/run.sh [options]

Options:
  --case <name>     fresh-topic, partial-resume, missing-mission, or all
  --runs <count>    Number of fresh trials per case (default: 1)
  --model <id>      Pi model override (or set PI_MODEL)
  --results <path>  Result directory (default: .eval-results/learn/<timestamp>)
  -h, --help        Show this help

Environment:
  PI_BIN             Pi executable (default: pi)
  PI_MODEL           Model ID when --model is omitted
  PI_EVAL_TIMEOUT    Seconds allowed per agent run (default: 600)
EOF
}

while (( $# > 0 )); do
  case "$1" in
    --case)
      selected_case="$2"
      shift 2
      ;;
    --runs)
      runs="$2"
      shift 2
      ;;
    --model)
      model="$2"
      shift 2
      ;;
    --results)
      results_root="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if ! [[ "$runs" =~ ^[1-9][0-9]*$ ]]; then
  printf 'Invalid --runs value: %s\n' "$runs" >&2
  exit 2
fi

if ! command -v "$pi_bin" >/dev/null 2>&1; then
  printf 'Pi executable not found: %s\n' "$pi_bin" >&2
  exit 1
fi

for required in "$evals_file" "$skill_file" "$verifier"; do
  if [[ ! -f "$required" ]]; then
    printf 'Required file not found: %s\n' "$required" >&2
    exit 1
  fi
done

case_names=(fresh-topic partial-resume missing-mission)
if [[ "$selected_case" != "all" ]]; then
  valid=0
  for name in "${case_names[@]}"; do
    [[ "$selected_case" == "$name" ]] && valid=1
  done
  if (( valid == 0 )); then
    printf 'Unknown case: %s\n' "$selected_case" >&2
    exit 2
  fi
  case_names=("$selected_case")
fi

if [[ -z "$results_root" ]]; then
  timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
  results_root="$repo_root/.eval-results/learn/$timestamp"
else
  mkdir -p "$results_root"
  results_root="$(cd "$results_root" && pwd)"
fi
mkdir -p "$results_root"

read_prompt() {
  local eval_id="$1"
  python3 - "$evals_file" "$eval_id" <<'PY'
import json
import sys

path, eval_id = sys.argv[1], int(sys.argv[2])
with open(path, encoding="utf-8") as file:
    data = json.load(file)
for item in data["evals"]:
    if item["id"] == eval_id:
        print(item["prompt"])
        raise SystemExit(0)
raise SystemExit(f"Eval id not found: {eval_id}")
PY
}

skill_revision="$(git -C "$repo_root" rev-parse --short HEAD 2>/dev/null || printf unknown)"
if ! git -C "$repo_root" diff --quiet -- skills/learn-init docs/learning-protocol.md 2>/dev/null; then
  skill_revision="$skill_revision-dirty"
fi

summary="$results_root/summary.md"
{
  printf '# Learn Init Skill Eval\n\n'
  printf -- '- Skill: `%s`\n' "$skill_file"
  printf -- '- Skill revision: `%s`\n' "$skill_revision"
  printf -- '- Host: `pi`\n'
  printf -- '- Model: `%s`\n' "${model:-default}"
  printf -- '- Runs per case: %s\n\n' "$runs"
  printf '| Case | Run | Agent | Verifier | Seconds |\n'
  printf '|---|---:|---|---|---:|\n'
} > "$summary"

failures=0

for case_name in "${case_names[@]}"; do
  case "$case_name" in
    fresh-topic)
      eval_id=1
      fixture=""
      ;;
    partial-resume)
      eval_id=2
      fixture="$fixtures_root/partial-resume/vault"
      ;;
    missing-mission)
      eval_id=3
      fixture=""
      ;;
  esac

  prompt="$(read_prompt "$eval_id")"

  for (( run_number=1; run_number<=runs; run_number++ )); do
    run_dir="$results_root/$case_name/run-$run_number"
    initial_vault="$run_dir/initial-vault"
    vault="$run_dir/vault"
    events="$run_dir/events.jsonl"
    stderr_log="$run_dir/stderr.log"
    verification="$run_dir/verification.json"

    mkdir -p "$initial_vault" "$vault"
    if [[ -n "$fixture" ]]; then
      cp -a "$fixture/." "$initial_vault/"
      cp -a "$initial_vault/." "$vault/"
    fi

    pi_args=(
      --mode json
      --no-session
      --approve
      --no-context-files
      --no-extensions
      --no-skills
      --no-prompt-templates
      --skill "$skill_file"
      --tools read,bash,edit,write,grep,find,ls
    )
    if [[ -n "$model" ]]; then
      pi_args+=(--model "$model")
    fi

    printf 'Running %s #%d...\n' "$case_name" "$run_number"
    started_at="$(date +%s)"
    set +e
    if command -v timeout >/dev/null 2>&1; then
      (
        cd "$vault"
        timeout "$timeout_seconds" "$pi_bin" "${pi_args[@]}" "$prompt"
      ) >"$events" 2>"$stderr_log"
    else
      (
        cd "$vault"
        "$pi_bin" "${pi_args[@]}" "$prompt"
      ) >"$events" 2>"$stderr_log"
    fi
    agent_rc=$?
    set -e
    duration_seconds=$(( $(date +%s) - started_at ))

    verify_args=(
      --case "$case_name"
      --vault "$vault"
      --events "$events"
      --output "$verification"
      --research-unavailable
    )
    if [[ -n "$fixture" ]]; then
      verify_args+=(--initial-vault "$initial_vault")
    fi

    set +e
    python3 "$verifier" "${verify_args[@]}"
    verifier_rc=$?
    set -e

    agent_label=PASS
    verifier_label=PASS
    (( agent_rc == 0 )) || agent_label=FAIL
    (( verifier_rc == 0 )) || verifier_label=FAIL
    printf '| %s | %d | %s | %s | %d |\n' "$case_name" "$run_number" "$agent_label" "$verifier_label" "$duration_seconds" >> "$summary"

    cat > "$run_dir/run.json" <<EOF
{
  "case": "$case_name",
  "run": $run_number,
  "host": "pi",
  "model": "${model:-default}",
  "skill_revision": "$skill_revision",
  "duration_seconds": $duration_seconds,
  "agent_exit_code": $agent_rc,
  "verifier_exit_code": $verifier_rc,
  "events": "events.jsonl",
  "verification": "verification.json"
}
EOF

    if (( agent_rc != 0 || verifier_rc != 0 )); then
      failures=$((failures + 1))
      printf 'Failure artifacts preserved: %s\n' "$run_dir" >&2
    fi
  done
done

printf '\nResults: %s\n' "$results_root"
printf 'Summary: %s\n' "$summary"
if (( failures > 0 )); then
  printf 'Failed runs: %d\n' "$failures" >&2
  exit 1
fi
printf 'All runs passed.\n'
