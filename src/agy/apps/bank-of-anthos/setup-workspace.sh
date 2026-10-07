#!/usr/bin/env bash

set -euo pipefail

workspace_prefix="bank-of-anthos"
upstream_url="https://github.com/mehtasanjit/bank-of-anthos.git"
default_bank_of_anthos_ref="db35fea9fd090150e2398106aadb475576f80d94"

usage() {
  cat <<EOF
Usage: ./setup-workspace.sh [--dry-run]

Create the lowest available numbered Bank of Anthos workspace next to this
script. The script clones the Bank of Anthos fork at a pinned revision and
adds AGENTS.md and the workspace memory rule.

Options:
  --dry-run  Print the clone and target that would be used without changing files.
  -h, --help Show this help.

Optional environment variables:
  BANK_OF_ANTHOS_REF  Branch, tag, or commit of the fork
                      (default: ${default_bank_of_anthos_ref})
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
guidance_root="$repository_root/src/resources/workspace-guidance"
agents_source="$guidance_root/agents/base.md"
memory_rule_source="$guidance_root/rules/workspace-memory.md"
bank_of_anthos_ref="${BANK_OF_ANTHOS_REF:-$default_bank_of_anthos_ref}"

if [[ -z "$bank_of_anthos_ref" ]]; then
  printf 'Repository and tooling refs must not be empty.\n' >&2
  exit 2
fi

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

next_index=1
while [[ -e "$script_dir/$workspace_prefix-$next_index" || -L "$script_dir/$workspace_prefix-$next_index" ]]; do
  next_index=$((next_index + 1))
done

target_root="$script_dir/$workspace_prefix-$next_index"

if [[ "$dry_run" == true ]]; then
  printf 'Would clone: %s\n' "$upstream_url"
  printf 'Ref: %s\n' "$bank_of_anthos_ref"
  printf 'Would create: %s\n' "$target_root"
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  printf 'git is required to clone the brownfield application.\n' >&2
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

# mkdir atomically reserves the next workspace number. If another setup wins
# the same number, advance without modifying its directory.
while ! mkdir -- "$target_root" 2>/dev/null; do
  if [[ -e "$target_root" || -L "$target_root" ]]; then
    next_index=$((next_index + 1))
    target_root="$script_dir/$workspace_prefix-$next_index"
    continue
  fi
  printf 'Unable to reserve workspace directory: %s\n' "$target_root" >&2
  exit 1
done

git -C "$target_root" init --quiet
git -C "$target_root" remote add origin "$upstream_url"
git -C "$target_root" fetch --depth 1 origin "$bank_of_anthos_ref"
git -C "$target_root" -c advice.detachedHead=false checkout --quiet --detach FETCH_HEAD

resolved_commit="$(git -C "$target_root" rev-parse HEAD)"
if [[ "$bank_of_anthos_ref" =~ ^[0-9a-fA-F]{40}$ ]] \
  && [[ "${resolved_commit,,}" != "${bank_of_anthos_ref,,}" ]]; then
  printf 'Resolved commit %s does not match requested commit %s.\n' \
    "$resolved_commit" "$bank_of_anthos_ref" >&2
  exit 1
fi

mkdir -p -- "$target_root/.agents/rules"
cp -- "$agents_source" "$target_root/AGENTS.md"
cp -- "$memory_rule_source" "$target_root/.agents/rules/workspace-memory.md"

# Keep workspace-only context out of the application diff while retaining the
# nested clone and its clean brownfield baseline.
{
  printf '\n# Antigravity workshop-local files\n'
  printf '/AGENTS.md\n'
  printf '/.agents/\n'
  printf '/.memory/\n'
  printf '/.scratch/\n'
} >> "$target_root/.git/info/exclude"

required_paths=(
  "$target_root/.git"
  "$target_root/README.md"
  "$target_root/AGENTS.md"
  "$target_root/.agents/rules/workspace-memory.md"
)

for required_path in "${required_paths[@]}"; do
  if [[ ! -e "$required_path" ]]; then
    printf 'Workspace setup is incomplete; required path is missing: %s\n' "$required_path" >&2
    exit 1
  fi
done

if [[ "$(git -C "$target_root" remote get-url origin)" != "$upstream_url" ]]; then
  printf 'Workspace origin does not match the approved repository.\n' >&2
  exit 1
fi

if [[ -n "$(git -C "$target_root" status --porcelain --untracked-files=all)" ]]; then
  printf 'Generated workspace does not have a clean application baseline.\n' >&2
  git -C "$target_root" status --short >&2
  exit 1
fi

setup_complete=true
trap - EXIT HUP INT TERM

printf 'Created Bank of Anthos workspace: %s\n' "$target_root"
printf 'Commit: %s\n' "$resolved_commit"
printf 'Open the clone as the workspace and read AGENTS.md before starting.\n'
