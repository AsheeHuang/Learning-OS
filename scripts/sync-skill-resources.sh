#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
protocol_source="$repo_root/docs/learning-protocol.md"
skills_root="$repo_root/skills"
mode="${1:-sync}"

if [[ ! -f "$protocol_source" ]]; then
  printf 'Protocol not found: %s\n' "$protocol_source" >&2
  exit 1
fi

shopt -s nullglob
skill_manifests=("$skills_root"/*/SKILL.md)

if (( ${#skill_manifests[@]} == 0 )); then
  printf 'No skills found under: %s\n' "$skills_root" >&2
  exit 1
fi

case "$mode" in
  sync)
    for manifest in "${skill_manifests[@]}"; do
      skill_dir="${manifest%/SKILL.md}"
      destination="$skill_dir/references/learning-protocol.md"

      mkdir -p "$(dirname "$destination")"
      cp "$protocol_source" "$destination"
      printf 'Synced: %s\n' "$destination"
    done
    ;;

  --check)
    stale=0

    for manifest in "${skill_manifests[@]}"; do
      skill_dir="${manifest%/SKILL.md}"
      destination="$skill_dir/references/learning-protocol.md"

      if [[ ! -f "$destination" ]]; then
        printf 'Missing generated resource: %s\n' "$destination" >&2
        stale=1
      elif ! cmp -s "$protocol_source" "$destination"; then
        printf 'Stale generated resource: %s\n' "$destination" >&2
        stale=1
      else
        printf 'Current: %s\n' "$destination"
      fi
    done

    if (( stale != 0 )); then
      printf 'Run scripts/sync-skill-resources.sh to refresh generated resources.\n' >&2
      exit 1
    fi
    ;;

  *)
    printf 'Usage: %s [--check]\n' "${0##*/}" >&2
    exit 2
    ;;
esac
