#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./setup-workspace.sh [--dry-run] [name]

Create the lowest available numbered Empty Workspace workspace, starting
with empty-workspace-1. The new workspace contains only AGENTS.md and
.agents/rules/workspace-memory.md.

With a name, create that workspace instead, next to this script. The name may
contain letters, digits, dots, hyphens, and underscores, and must not already
exist.

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

if [[ $# -gt 1 ]]; then
  usage >&2
  exit 2
fi

workspace_name="${1:-}"
if [[ -n "$workspace_name" && ! "$workspace_name" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  printf 'Invalid workspace name: %s\n' "$workspace_name" >&2
  usage >&2
  exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/../../../.." && pwd)"
guidance_root="$repository_root/src/resources/workspace-guidance"
agents_source="$guidance_root/agents/base.md"
memory_rule_source="$guidance_root/rules/workspace-memory.md"

required_files=(
  "$agents_source"
  "$memory_rule_source"
)

for required_file in "${required_files[@]}"; do
  if [[ ! -f "$required_file" ]]; then
    printf 'Required setup resource is missing: %s\n' "$required_file" >&2
    exit 1
  fi
done

if [[ -n "$workspace_name" ]]; then
  target_root="$script_dir/$workspace_name"
  if [[ -e "$target_root" || -L "$target_root" ]]; then
    printf 'Workspace already exists: %s\n' "$target_root" >&2
    exit 1
  fi
else
  next_index=1
  while [[ -e "$script_dir/empty-workspace-$next_index" || -L "$script_dir/empty-workspace-$next_index" ]]; do
    next_index=$((next_index + 1))
  done
  target_root="$script_dir/empty-workspace-$next_index"
fi

if [[ "$dry_run" == true ]]; then
  printf 'Would create: %s\n' "$target_root"
  exit 0
fi

setup_complete=false
target_created=false

# Only ever remove a directory this run created itself.
cleanup() {
  if [[ "$setup_complete" == false && "$target_created" == true ]]; then
    if [[ "$(dirname -- "$target_root")" == "$script_dir" ]]; then
      rm -rf -- "$target_root"
    else
      printf 'Refusing to clean unexpected setup target: %s\n' "$target_root" >&2
    fi
  fi
}

trap cleanup EXIT HUP INT TERM

# mkdir is the reservation step. If another process creates the same numbered
# workspace first, continue to the next number without touching that directory.
# A named workspace is never retried under another name.
while ! mkdir -- "$target_root" 2>/dev/null; do
  if [[ -z "$workspace_name" ]] && [[ -e "$target_root" || -L "$target_root" ]]; then
    next_index=$((next_index + 1))
    target_root="$script_dir/empty-workspace-$next_index"
    continue
  fi
  printf 'Unable to create workspace directory: %s\n' "$target_root" >&2
  exit 1
done
target_created=true

mkdir -p -- "$target_root/.agents/rules"
cp -- "$agents_source" "$target_root/AGENTS.md"
cp -- "$memory_rule_source" "$target_root/.agents/rules/workspace-memory.md"

required_paths=(
  "$target_root/AGENTS.md"
  "$target_root/.agents/rules/workspace-memory.md"
)

for required_path in "${required_paths[@]}"; do
  if [[ ! -e "$required_path" ]]; then
    printf 'Workspace setup is incomplete; required path is missing: %s\n' "$required_path" >&2
    exit 1
  fi
done

unexpected_root_entry="$(find "$target_root" -mindepth 1 -maxdepth 1 \
  ! -name AGENTS.md ! -name .agents -print -quit)"
if [[ -n "$unexpected_root_entry" ]]; then
  printf 'Workspace setup created an unexpected root entry: %s\n' "$unexpected_root_entry" >&2
  exit 1
fi

setup_complete=true
trap - EXIT HUP INT TERM

printf 'Created Empty Workspace workspace: %s\n' "$target_root"
printf 'Open it as the workspace and read AGENTS.md before starting development.\n'
