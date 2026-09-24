#!/usr/bin/env bash

set -euo pipefail

workspace_prefix="banking-complaint-resolution-workbench"

usage() {
  cat <<EOF
Usage: ./setup-workspace.sh [--dry-run]

Create the lowest available numbered Banking Complaint Resolution Workbench
workspace, starting with ${workspace_prefix}-1. The new workspace contains
only AGENTS.md and .agents/ workspace guidance, rules, skills, SDLC subagents,
and the Conductor plugin.

Options:
  --dry-run  Print the directory that would be created without changing files.
  -h, --help Show this help.

Optional environment variables:
  AGENTS_CLI_REF  google/agents-cli branch, tag, or commit (default: main)
  CONDUCTOR_REF   gemini-cli-extensions/conductor ref (default: main)
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
repository_root="$(cd -- "$script_dir/../../../.." && pwd)"
seed_script="$repository_root/src/scripts/seed-workspace.sh"
agents_cli_importer="$repository_root/src/scripts/import_google_agents_cli_skills.py"
conductor_importer="$repository_root/src/scripts/import_conductor_plugin.py"
agents_cli_ref="${AGENTS_CLI_REF:-main}"
conductor_ref="${CONDUCTOR_REF:-main}"

required_files=(
  "$seed_script"
  "$agents_cli_importer"
  "$conductor_importer"
)

for required_file in "${required_files[@]}"; do
  if [[ ! -f "$required_file" ]]; then
    printf 'Required setup resource is missing: %s\n' "$required_file" >&2
    exit 1
  fi
done

next_index=1
while [[ -e "$script_dir/$workspace_prefix-$next_index" || -L "$script_dir/$workspace_prefix-$next_index" ]]; do
  next_index=$((next_index + 1))
done

target_root="$script_dir/$workspace_prefix-$next_index"

if [[ "$dry_run" == true ]]; then
  printf 'Would create: %s\n' "$target_root"
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  printf 'python3 is required to import workspace-local skills and plugins.\n' >&2
  exit 1
fi

setup_complete=false

cleanup() {
  if [[ "$setup_complete" == false && -n "${target_root:-}" ]]; then
    case "$target_root" in
      "$script_dir"/"$workspace_prefix"-[1-9]* )
        rm -rf -- "$target_root"
        ;;
      * )
        printf 'Refusing to clean unexpected setup target: %s\n' "$target_root" >&2
        ;;
    esac
  fi
}

trap cleanup EXIT HUP INT TERM

# mkdir is the reservation step. If another process creates the same numbered
# workspace first, continue to the next number without touching that directory.
while ! mkdir -- "$target_root" 2>/dev/null; do
  if [[ -e "$target_root" || -L "$target_root" ]]; then
    next_index=$((next_index + 1))
    target_root="$script_dir/$workspace_prefix-$next_index"
    continue
  fi
  printf 'Unable to create workspace directory: %s\n' "$target_root" >&2
  exit 1
done

"$seed_script" "$target_root"
python3 "$agents_cli_importer" "$target_root" --ref "$agents_cli_ref"
python3 "$conductor_importer" "$target_root" --ref "$conductor_ref"

required_paths=(
  "$target_root/AGENTS.md"
  "$target_root/.agents/agents"
  "$target_root/.agents/rules"
  "$target_root/.agents/skills"
  "$target_root/.agents/plugins/conductor/plugin.json"
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

printf 'Created Banking Complaint Resolution Workbench workspace: %s\n' "$target_root"
printf 'Open it as the workspace and read AGENTS.md before starting development.\n'
