#!/usr/bin/env bash

set -euo pipefail

workspace_prefix="bank-of-anthos-sdlc"
upstream_url="https://github.com/GoogleCloudPlatform/bank-of-anthos.git"
default_bank_of_anthos_ref="674d9fea755df9938bc9563b559fbbbb6358b6f3"

usage() {
  cat <<EOF
Usage: ./scripts/setup-workspace.sh [--dry-run]

Create the lowest available numbered Bank of Anthos SDLC workspace under
demo/. The script clones the official Bank of Anthos repository at a pinned
revision and adds Antigravity workspace guidance, rules, skills, SDLC
subagents, and the Conductor plugin.

Options:
  --dry-run  Print the clone and target that would be used without changing files.
  -h, --help Show this help.

Optional environment variables:
  BANK_OF_ANTHOS_REF  Upstream branch, tag, or commit
                      (default: ${default_bank_of_anthos_ref})
  AGENTS_CLI_REF      google/agents-cli branch, tag, or commit (default: main)
  CONDUCTOR_REF       gemini-cli-extensions/conductor ref (default: main)
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
project_root="$(cd -- "$script_dir/.." && pwd)"
repository_root="$(cd -- "$project_root/../../../.." && pwd)"
demo_root="$project_root/demo"
seed_script="$repository_root/src/scripts/seed-workspace.sh"
agents_cli_importer="$repository_root/src/scripts/import_google_agents_cli_skills.py"
conductor_importer="$repository_root/src/scripts/import_conductor_plugin.py"
bank_of_anthos_ref="${BANK_OF_ANTHOS_REF:-$default_bank_of_anthos_ref}"
agents_cli_ref="${AGENTS_CLI_REF:-main}"
conductor_ref="${CONDUCTOR_REF:-main}"

if [[ -z "$bank_of_anthos_ref" || -z "$agents_cli_ref" || -z "$conductor_ref" ]]; then
  printf 'Repository and tooling refs must not be empty.\n' >&2
  exit 2
fi

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

if [[ -L "$demo_root" ]]; then
  printf 'Refusing symlink demo directory: %s\n' "$demo_root" >&2
  exit 2
fi
if [[ -e "$demo_root" && ! -d "$demo_root" ]]; then
  printf 'Demo path is not a directory: %s\n' "$demo_root" >&2
  exit 2
fi
mkdir -p -- "$demo_root"

next_index=1
while [[ -e "$demo_root/$workspace_prefix-$next_index" || -L "$demo_root/$workspace_prefix-$next_index" ]]; do
  next_index=$((next_index + 1))
done

target_root="$demo_root/$workspace_prefix-$next_index"

if [[ "$dry_run" == true ]]; then
  printf 'Would clone: %s\n' "$upstream_url"
  printf 'Upstream ref: %s\n' "$bank_of_anthos_ref"
  printf 'Would create: %s\n' "$target_root"
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  printf 'git is required to clone the brownfield application.\n' >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  printf 'python3 is required to import workspace-local skills and plugins.\n' >&2
  exit 1
fi

setup_complete=false

cleanup() {
  if [[ "$setup_complete" == false && -n "${target_root:-}" ]]; then
    case "$target_root" in
      "$demo_root"/"$workspace_prefix"-[1-9]* )
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
    target_root="$demo_root/$workspace_prefix-$next_index"
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

"$seed_script" "$target_root"
python3 "$agents_cli_importer" "$target_root" --ref "$agents_cli_ref"
python3 "$conductor_importer" "$target_root" --ref "$conductor_ref"

# Keep workspace-only context out of the upstream application diff while
# retaining the nested clone and its clean brownfield baseline.
{
  printf '\n# Antigravity workshop-local files\n'
  printf '/AGENTS.md\n'
  printf '/.agents/\n'
  printf '/.memory/\n'
} >> "$target_root/.git/info/exclude"

required_paths=(
  "$target_root/.git"
  "$target_root/README.md"
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

if [[ "$(git -C "$target_root" remote get-url origin)" != "$upstream_url" ]]; then
  printf 'Workspace origin does not match the approved upstream repository.\n' >&2
  exit 1
fi

if [[ -n "$(git -C "$target_root" status --porcelain --untracked-files=all)" ]]; then
  printf 'Generated workspace does not have a clean application baseline.\n' >&2
  git -C "$target_root" status --short >&2
  exit 1
fi

setup_complete=true
trap - EXIT HUP INT TERM

printf 'Created Bank of Anthos SDLC workspace: %s\n' "$target_root"
printf 'Upstream commit: %s\n' "$resolved_commit"
printf 'Open the clone as the workspace and read AGENTS.md before starting.\n'
