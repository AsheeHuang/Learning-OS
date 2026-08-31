#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
init_evals="$repo_root/skills/learn-init/evals/evals.json"
init_skill="$repo_root/skills/learn-init/SKILL.md"
quiz_cases_file="$repo_root/evals/learn/quiz-cases.json"
quiz_skill="$repo_root/skills/learn-quiz/SKILL.md"
quiz_fixture="$repo_root/evals/learn/fixtures/quiz-base/vault"
quiz_prepare="$repo_root/evals/learn/prepare_quiz_fixture.py"
note_cases_file="$repo_root/evals/learn/note-cases.json"
note_skill="$repo_root/skills/learn-note/SKILL.md"
note_fixture="$repo_root/evals/learn/fixtures/quiz-base/vault"
note_prepare="$repo_root/evals/learn/prepare_note_fixture.py"
note_verifier="$repo_root/evals/learn/verify_note.py"
verifier="$repo_root/evals/learn/verify.py"
fixtures_root="$repo_root/evals/learn/fixtures"
pi_bin="${PI_BIN:-pi}"
runs=1
selected_suite="init"
selected_case="all"
model="${PI_MODEL:-}"
results_root=""
timeout_seconds="${PI_EVAL_TIMEOUT:-600}"

init_cases=(fresh-topic partial-resume missing-mission)
quiz_cases=(
  quiz-candidates
  quiz-strong
  quiz-remediation
  quiz-unknown
  quiz-resume
  quiz-abandon
  quiz-unverified
  quiz-ambiguity
  quiz-interruption
  quiz-dispute
  quiz-conflict
  quiz-finalization
)
note_cases=(
  note-create
  note-resume
  note-promotion
  note-unverified
  note-ambiguity
)

usage() {
  cat <<'EOF'
Usage: evals/learn/run.sh [options]

Options:
  --suite <name>    init, quiz, note, or all (default: init)
  --case <name>     Run one case from the selected suite, or all
  --runs <count>    Number of fresh trials per case (default: 1)
  --model <id>      Pi model override (or set PI_MODEL)
  --results <path>  Result directory (default: .eval-results/learn/<timestamp>)
  -h, --help        Show this help

Environment:
  PI_BIN             Pi executable (default: pi)
  PI_MODEL           Model ID when --model is omitted
  PI_EVAL_TIMEOUT    Seconds allowed per agent turn (default: 600)
EOF
}

while (( $# > 0 )); do
  case "$1" in
    --suite)
      selected_suite="$2"
      shift 2
      ;;
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
if [[ "$selected_suite" != "init" && "$selected_suite" != "quiz" && "$selected_suite" != "note" && "$selected_suite" != "all" ]]; then
  printf 'Invalid --suite value: %s\n' "$selected_suite" >&2
  exit 2
fi
if ! command -v "$pi_bin" >/dev/null 2>&1; then
  printf 'Pi executable not found: %s\n' "$pi_bin" >&2
  exit 1
fi

required_files=("$verifier")
if [[ "$selected_suite" == "init" || "$selected_suite" == "all" ]]; then
  required_files+=("$init_evals" "$init_skill")
fi
if [[ "$selected_suite" == "quiz" || "$selected_suite" == "all" ]]; then
  required_files+=("$quiz_cases_file" "$quiz_skill" "$quiz_prepare")
fi
if [[ "$selected_suite" == "note" || "$selected_suite" == "all" ]]; then
  required_files+=("$note_cases_file" "$note_skill" "$note_prepare" "$note_verifier")
fi
for required in "${required_files[@]}"; do
  if [[ ! -f "$required" ]]; then
    printf 'Required file not found: %s\n' "$required" >&2
    exit 1
  fi
done

case_names=()
if [[ "$selected_suite" == "init" || "$selected_suite" == "all" ]]; then
  case_names+=("${init_cases[@]}")
fi
if [[ "$selected_suite" == "quiz" || "$selected_suite" == "all" ]]; then
  case_names+=("${quiz_cases[@]}")
fi
if [[ "$selected_suite" == "note" || "$selected_suite" == "all" ]]; then
  case_names+=("${note_cases[@]}")
fi
if [[ "$selected_case" != "all" ]]; then
  valid=0
  for name in "${case_names[@]}"; do
    [[ "$selected_case" == "$name" ]] && valid=1
  done
  if (( valid == 0 )); then
    printf 'Unknown case for suite %s: %s\n' "$selected_suite" "$selected_case" >&2
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

is_init_case() {
  local candidate="$1"
  for name in "${init_cases[@]}"; do
    [[ "$candidate" == "$name" ]] && return 0
  done
  return 1
}

is_note_case() {
  local candidate="$1"
  for name in "${note_cases[@]}"; do
    [[ "$candidate" == "$name" ]] && return 0
  done
  return 1
}

read_init_prompt() {
  local eval_id="$1"
  python3 - "$init_evals" "$eval_id" <<'PY'
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

read_quiz_turns() {
  local case_name="$1"
  python3 - "$quiz_cases_file" "$case_name" <<'PY'
import json
import sys

path, case_name = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as file:
    data = json.load(file)
for item in data["cases"]:
    if item["name"] == case_name:
        for turn in item["turns"]:
            sys.stdout.write(turn)
            sys.stdout.write("\0")
        raise SystemExit(0)
raise SystemExit(f"Quiz case not found: {case_name}")
PY
}

read_note_turns() {
  local case_name="$1"
  python3 - "$note_cases_file" "$case_name" <<'PY'
import json
import sys

path, case_name = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as file:
    data = json.load(file)
for item in data["cases"]:
    if item["name"] == case_name:
        for turn in item["turns"]:
            sys.stdout.write(turn)
            sys.stdout.write("\0")
        raise SystemExit(0)
raise SystemExit(f"Note case not found: {case_name}")
PY
}

skill_revision="$(git -C "$repo_root" rev-parse --short HEAD 2>/dev/null || printf unknown)"
if ! git -C "$repo_root" diff --quiet -- skills docs/learning-protocol.md evals/learn examples/operating-systems 2>/dev/null; then
  skill_revision="$skill_revision-dirty"
fi

summary="$results_root/summary.md"
{
  printf '# Learning Skill Behavioral Eval\n\n'
  printf -- '- Suite: `%s`\n' "$selected_suite"
  printf -- '- Skill revision: `%s`\n' "$skill_revision"
  printf -- '- Host: `pi`\n'
  printf -- '- Model: `%s`\n' "${model:-default}"
  printf -- '- Runs per case: %s\n\n' "$runs"
  printf '| Case | Run | Agent | Verifier | Seconds |\n'
  printf '|---|---:|---|---|---:|\n'
} > "$summary"

failures=0

for case_name in "${case_names[@]}"; do
  if is_init_case "$case_name"; then
    skill_file="$init_skill"
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
    turns=("$(read_init_prompt "$eval_id")")
  elif is_note_case "$case_name"; then
    skill_file="$note_skill"
    fixture="$note_fixture"
    mapfile -d '' -t turns < <(read_note_turns "$case_name")
  else
    skill_file="$quiz_skill"
    fixture="$quiz_fixture"
    mapfile -d '' -t turns < <(read_quiz_turns "$case_name")
  fi

  for (( run_number=1; run_number<=runs; run_number++ )); do
    run_dir="$results_root/$case_name/run-$run_number"
    initial_vault="$run_dir/initial-vault"
    vault="$run_dir/vault"
    session_dir="$run_dir/session"
    events="$run_dir/events.jsonl"
    stderr_log="$run_dir/stderr.log"
    verification="$run_dir/verification.json"

    snapshots_dir="$run_dir/snapshots"
    mkdir -p "$initial_vault" "$vault" "$session_dir" "$snapshots_dir"
    if [[ -n "$fixture" ]]; then
      cp -a "$fixture/." "$initial_vault/"
    fi
    if is_note_case "$case_name"; then
      python3 "$note_prepare" --case "$case_name" --vault "$initial_vault"
    elif ! is_init_case "$case_name"; then
      python3 "$quiz_prepare" --case "$case_name" --vault "$initial_vault"
    fi
    cp -a "$initial_vault/." "$vault/"

    base_args=(
      --mode json
      --approve
      --no-context-files
      --no-extensions
      --no-skills
      --no-prompt-templates
      --skill "$skill_file"
      --tools read,bash,edit,write,grep,find,ls
    )
    if [[ -n "$model" ]]; then
      base_args+=(--model "$model")
    fi

    printf 'Running %s #%d (%d turns)...\n' "$case_name" "$run_number" "${#turns[@]}"
    started_at="$(date +%s)"
    agent_rc=0
    : > "$events"
    : > "$stderr_log"

    for (( turn_index=0; turn_index<${#turns[@]}; turn_index++ )); do
      turn_args=("${base_args[@]}")
      if is_init_case "$case_name" || is_note_case "$case_name"; then
        turn_args+=(--no-session)
      else
        turn_args+=(--session-dir "$session_dir")
        (( turn_index > 0 )) && turn_args+=(--continue)
      fi

      set +e
      if command -v timeout >/dev/null 2>&1; then
        (
          cd "$vault"
          timeout "$timeout_seconds" "$pi_bin" "${turn_args[@]}" "${turns[$turn_index]}"
        ) >>"$events" 2>>"$stderr_log"
      else
        (
          cd "$vault"
          "$pi_bin" "${turn_args[@]}" "${turns[$turn_index]}"
        ) >>"$events" 2>>"$stderr_log"
      fi
      turn_rc=$?
      set -e
      snapshot="$snapshots_dir/turn-$((turn_index + 1))-vault"
      mkdir -p "$snapshot"
      cp -a "$vault/." "$snapshot/"
      if (( turn_rc != 0 )); then
        agent_rc=$turn_rc
        break
      fi
    done
    duration_seconds=$(( $(date +%s) - started_at ))

    verifier_for_case="$verifier"
    if is_note_case "$case_name"; then
      verifier_for_case="$note_verifier"
    fi
    verify_args=(
      --case "$case_name"
      --vault "$vault"
      --events "$events"
      --output "$verification"
    )
    if [[ -n "$fixture" ]]; then
      verify_args+=(--initial-vault "$initial_vault")
    fi
    if is_init_case "$case_name"; then
      verify_args+=(--research-unavailable)
    fi

    set +e
    python3 "$verifier_for_case" "${verify_args[@]}"
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
