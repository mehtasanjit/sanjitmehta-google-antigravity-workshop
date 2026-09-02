#!/usr/bin/env bash

set -euo pipefail

workspace_prefix="kanban-board-lab"

usage() {
  cat <<EOF
Usage: ./setup-workspace.sh [--dry-run]

Create the lowest available numbered Kanban Board Lab directory. The new
directory is intentionally empty and contains no prescribed workspace tools.

Options:
  --dry-run  Print the directory that would be created without changing files.
  -h, --help Show this help.
EOF
}

dry_run=false

case "${1:-}" in
  --dry-run)
    dry_run=true
    shift
    ;;
  -h|--help)
    usage
    exit 0
    ;;
esac

if [[ $# -ne 0 ]]; then
  usage >&2
  exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
next_index=1

while [[ -e "$script_dir/$workspace_prefix-$next_index" || -L "$script_dir/$workspace_prefix-$next_index" ]]; do
  next_index=$((next_index + 1))
done

target_root="$script_dir/$workspace_prefix-$next_index"

if [[ "$dry_run" == true ]]; then
  printf 'Would create empty workspace: %s\n' "$target_root"
  exit 0
fi

# mkdir atomically reserves the number. If another process creates the same
# directory first, continue to the next number without touching that run.
while ! mkdir -- "$target_root" 2>/dev/null; do
  if [[ -e "$target_root" || -L "$target_root" ]]; then
    next_index=$((next_index + 1))
    target_root="$script_dir/$workspace_prefix-$next_index"
    continue
  fi
  printf 'Unable to create workspace directory: %s\n' "$target_root" >&2
  exit 1
done

printf 'Created empty Kanban Board Lab workspace: %s\n' "$target_root"
