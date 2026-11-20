#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: ./setup-workspace.sh [--dry-run]

Create the lowest available numbered RFP Evaluation and Award Agent workspace,
starting with rfp-eval-and-award-1. Each new workspace contains only two empty
subdirectories: adk/ and langgraph/.

Options:
  --dry-run  Print the directories that would be created without changing files.
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
while [[ -e "$script_dir/rfp-eval-and-award-$next_index" || -L "$script_dir/rfp-eval-and-award-$next_index" ]]; do
  next_index=$((next_index + 1))
done

target_root="$script_dir/rfp-eval-and-award-$next_index"

if [[ "$dry_run" == true ]]; then
  printf 'Would create: %s (with empty adk/ and langgraph/ subdirectories)\n' "$target_root"
  exit 0
fi

setup_complete=false

cleanup() {
  if [[ "$setup_complete" == false && -n "${target_root:-}" ]]; then
    case "$target_root" in
      "$script_dir"/rfp-eval-and-award-[1-9]* )
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
    target_root="$script_dir/rfp-eval-and-award-$next_index"
    continue
  fi
  printf 'Unable to create workspace directory: %s\n' "$target_root" >&2
  exit 1
done

mkdir -p -- "$target_root/adk" "$target_root/langgraph"

unexpected_root_entry="$(find "$target_root" -mindepth 1 -maxdepth 1 \
  ! -name adk ! -name langgraph -print -quit)"
if [[ -n "$unexpected_root_entry" ]]; then
  printf 'Workspace setup created an unexpected root entry: %s\n' "$unexpected_root_entry" >&2
  exit 1
fi

setup_complete=true
trap - EXIT HUP INT TERM

printf 'Created RFP Evaluation and Award Agent workspace: %s\n' "$target_root"
printf '  - %s/adk\n' "$target_root"
printf '  - %s/langgraph\n' "$target_root"
