#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
protocol_source="$repo_root/docs/learning-protocol.md"
skills_root="$repo_root/skills"
vault_prefix="learning-os"
vault_path=""

usage() {
  printf 'Usage: %s --new-env [--agent=<pi|cc|codex>] | --sync-resources [--check] | --clean-env\n\n' "${0##*/}"
  cat <<'EOF'
Development helpers for Learning OS skills.

  --new-env             Create a fresh dev vault under ${TMPDIR:-/tmp}
                        with a copy of every skill under skills/.
  --agent=<pi|cc|codex> Launch the given agent inside the new vault and
                        install only that host's skill directory (pi/codex:
                        .agents/skills, cc: .claude/skills). Requires
                        --new-env.
  --sync-resources      Copy docs/learning-protocol.md into every skill's
                        references/learning-protocol.md.
  --sync-resources --check
                        Verify every skill's bundled protocol is current.
  --clean-env           Remove every dev vault created by --new-env.
  -h, --help            Show this help.
EOF
}

create_env() {
  local name source manifest dir
  local -a skills=() dirs=()

  case "$agent" in
    cc)       dirs=(".claude/skills") ;;
    pi|codex) dirs=(".agents/skills") ;;
    *)        dirs=(".claude/skills" ".agents/skills") ;;
  esac

  vault_path="$(mktemp -d "${TMPDIR:-/tmp}/${vault_prefix}-XXXXXX")"
  for dir in "${dirs[@]}"; do
    mkdir -p "$vault_path/$dir"
  done

  shopt -s nullglob
  for manifest in "$skills_root"/*/SKILL.md; do
    skills+=("$(basename "$(dirname "$manifest")")")
  done
  shopt -u nullglob

  if (( ${#skills[@]} == 0 )); then
    printf 'No skills found under: %s\n' "$skills_root" >&2
    exit 1
  fi

  for name in "${skills[@]}"; do
    source="$skills_root/$name"
    for dir in "${dirs[@]}"; do
      cp -r "$source" "$vault_path/$dir/$name"
      printf 'Copied: %s -> %s\n' "$vault_path/$dir/$name" "$source"
    done
  done

  printf '\nDevelopment vault ready: %s\n' "$vault_path"
  if [[ -z "$agent" ]]; then
    printf 'Claude Code: cd %q && claude       then run /learn <topic> or /explain <concept>\n' "$vault_path"
    printf 'Codex:      cd %q && codex        then run $learn <topic> or $explain <concept>\n' "$vault_path"
    printf 'Pi:         cd %q && pi --approve then run /skill:<name> <args>\n' "$vault_path"
  fi
}

launch_agent() {
  local cmd="" flags=""

  case "$1" in
    pi)    cmd="pi";    flags="--approve" ;;
    cc)    cmd="claude" ;;
    codex) cmd="codex"  ;;
  esac

  printf 'Launching %s in the vault...\n' "$cmd"
  cd "$vault_path"
  exec "$cmd" $flags
}

clean_env() {
  local base="${TMPDIR:-/tmp}"
  local count=0 dir

  for dir in "$base"/${vault_prefix}-*; do
    [[ -d "$dir" ]] || continue
    rm -rf "$dir"
    printf 'Removed: %s\n' "$dir"
    count=$((count + 1))
  done

  if (( count == 0 )); then
    printf 'No development vaults found under %s.\n' "$base"
  else
    printf 'Removed %d development vault(s).\n' "$count"
  fi
}

sync_resources() {
  local manifest destination skill_dir stale=0
  local -a manifests=()

  if [[ ! -f "$protocol_source" ]]; then
    printf 'Protocol not found: %s\n' "$protocol_source" >&2
    exit 1
  fi

  shopt -s nullglob
  manifests=("$skills_root"/*/SKILL.md)
  shopt -u nullglob

  if (( ${#manifests[@]} == 0 )); then
    printf 'No skills found under: %s\n' "$skills_root" >&2
    exit 1
  fi

  for manifest in "${manifests[@]}"; do
    skill_dir="${manifest%/SKILL.md}"
    destination="$skill_dir/references/learning-protocol.md"

    if [[ "$check" == true ]]; then
      if [[ ! -f "$destination" ]]; then
        printf 'Missing generated resource: %s\n' "$destination" >&2
        stale=1
      elif ! cmp -s "$protocol_source" "$destination"; then
        printf 'Stale generated resource: %s\n' "$destination" >&2
        stale=1
      else
        printf 'Current: %s\n' "$destination"
      fi
    else
      mkdir -p "$(dirname "$destination")"
      cp "$protocol_source" "$destination"
      printf 'Synced: %s\n' "$destination"
    fi
  done

  if [[ "$check" == true && "$stale" -ne 0 ]]; then
    printf 'Run scripts/%s --sync-resources to refresh generated resources.\n' "${0##*/}" >&2
    exit 1
  fi
}

mode=""
check=false
agent=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --new-env)
      if [[ -n "$mode" && "$mode" != "new-env" ]]; then
        printf '%s: --new-env, --sync-resources, and --clean-env are mutually exclusive.\n' "${0##*/}" >&2
        exit 2
      fi
      mode="new-env"
      shift
      ;;
    --sync-resources)
      if [[ -n "$mode" && "$mode" != "sync" ]]; then
        printf '%s: --new-env, --sync-resources, and --clean-env are mutually exclusive.\n' "${0##*/}" >&2
        exit 2
      fi
      mode="sync"
      shift
      ;;
    --clean-env)
      if [[ -n "$mode" && "$mode" != "clean-env" ]]; then
        printf '%s: --new-env, --sync-resources, and --clean-env are mutually exclusive.\n' "${0##*/}" >&2
        exit 2
      fi
      mode="clean-env"
      shift
      ;;
    --check)
      check=true
      shift
      ;;
    --agent=*)
      agent="${1#--agent=}"
      shift
      ;;
    --agent)
      shift
      if [[ $# -eq 0 ]]; then
        printf '%s: --agent requires a value (pi, cc, or codex).\n' "${0##*/}" >&2
        exit 2
      fi
      agent="$1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown option: %s\n' "$1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$check" == true && "$mode" != "sync" ]]; then
  printf '%s: --check requires --sync-resources.\n' "${0##*/}" >&2
  exit 2
fi

if [[ -n "$agent" ]]; then
  if [[ "$mode" != "new-env" ]]; then
    printf '%s: --agent requires --new-env.\n' "${0##*/}" >&2
    exit 2
  fi
  case "$agent" in
    pi|cc|codex) ;;
    *)
      printf 'Unknown agent: %s (expected pi, cc, or codex).\n' "$agent" >&2
      exit 2
      ;;
  esac
  cmd=""
  [[ "$agent" == "pi" ]] && cmd="pi"
  [[ "$agent" == "cc" ]] && cmd="claude"
  [[ "$agent" == "codex" ]] && cmd="codex"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    printf 'Agent not found: %s (is it installed?).\n' "$cmd" >&2
    exit 1
  fi
fi

case "$mode" in
  new-env)
    create_env
    if [[ -n "$agent" ]]; then
      launch_agent "$agent"
    fi
    ;;
  sync)
    sync_resources
    ;;
  clean-env)
    clean_env
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
