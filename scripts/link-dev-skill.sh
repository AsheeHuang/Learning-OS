#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skill_name="${1:-learn}"
skill_source="$repo_root/skills/$skill_name"
vault_prefix="learning-os"

if [[ ! -f "$skill_source/SKILL.md" ]]; then
  printf 'Skill not found: %s\n' "$skill_source" >&2
  exit 1
fi

vault_path="$(mktemp -d "${TMPDIR:-/tmp}/${vault_prefix}-XXXXXX")"

mkdir -p \
  "$vault_path/.claude/skills" \
  "$vault_path/.agents/skills"

link_skill() {
  local destination="$1"

  if [[ -L "$destination" ]]; then
    if [[ "$(readlink "$destination")" == "$skill_source" ]]; then
      printf 'Already linked: %s -> %s\n' "$destination" "$skill_source"
      return
    fi

    printf 'Refusing to replace existing symlink: %s -> %s\n' \
      "$destination" "$(readlink "$destination")" >&2
    exit 1
  fi

  if [[ -e "$destination" ]]; then
    printf 'Refusing to replace existing path: %s\n' "$destination" >&2
    exit 1
  fi

  ln -s "$skill_source" "$destination"
  printf 'Linked: %s -> %s\n' "$destination" "$skill_source"
}

link_skill "$vault_path/.claude/skills/$skill_name"
link_skill "$vault_path/.agents/skills/$skill_name"

printf '\nDevelopment vault ready: %s\n' "$vault_path"
printf 'Claude Code: cd %q && claude       then run /%s <topic>\n' "$vault_path" "$skill_name"
printf 'Codex:      cd %q && codex        then run $%s <topic>\n' "$vault_path" "$skill_name"
printf 'Pi:         cd %q && pi --approve then run /skill:%s <topic>\n' "$vault_path" "$skill_name"
