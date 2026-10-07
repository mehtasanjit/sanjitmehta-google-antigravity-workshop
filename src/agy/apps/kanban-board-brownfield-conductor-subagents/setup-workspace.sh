#!/usr/bin/env bash

set -euo pipefail

source_name="kanban-board-app"

usage() {
  cat <<EOF
Usage: ./setup-workspace.sh [--dry-run]

Create the lowest available numbered copy of ${source_name}, starting with
${source_name}-1. The copy contains:
  - the application, including frontend/node_modules (without build output,
    local database, or caches), committed as a Git baseline
  - AGENTS.md, copied from src/resources/workspace-guidance/agents/base.md
  - .agents/rules/workspace-memory.md, copied from the workspace memory rule
  - .agents/agents/, copied from the SDLC subagents
  - .agents/plugins/conductor/, the Conductor plugin downloaded at setup

Options:
  --dry-run  Print the directory that would be created without changing files.
  -h, --help Show this help.

Optional environment variables:
  CONDUCTOR_REF  gemini-cli-extensions/conductor commit on main (default: main);
                 release tags lack plugin.json and do not work
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
app_source="$script_dir/../kanban-board-brownfield/$source_name"
guidance_root="$repository_root/src/resources/workspace-guidance"
agents_md_source="$guidance_root/agents/base.md"
memory_rule_source="$guidance_root/rules/workspace-memory.md"
subagents_source="$repository_root/src/resources/subagents/sdlc-subagents/.agents/agents"
conductor_importer="$repository_root/src/scripts/import_conductor_plugin.py"
conductor_ref="${CONDUCTOR_REF:-main}"

for required_path in "$app_source" "$agents_md_source" "$memory_rule_source" "$subagents_source" "$conductor_importer"; do
  if [[ ! -e "$required_path" ]]; then
    printf 'Required setup resource is missing: %s\n' "$required_path" >&2
    exit 1
  fi
done

next_index=1
while [[ -e "$script_dir/$source_name-$next_index" || -L "$script_dir/$source_name-$next_index" ]]; do
  next_index=$((next_index + 1))
done

target_root="$script_dir/$source_name-$next_index"

if [[ "$dry_run" == true ]]; then
  printf 'Would create: %s\n' "$target_root"
  exit 0
fi

if ! command -v git >/dev/null 2>&1; then
  printf 'git is required to record the baseline.\n' >&2
  exit 1
fi
if ! command -v python3 >/dev/null 2>&1; then
  printf 'python3 is required to import the Conductor plugin.\n' >&2
  exit 1
fi

setup_complete=false

cleanup() {
  if [[ "$setup_complete" == false && -n "${target_root:-}" ]]; then
    case "$target_root" in
      "$script_dir"/"$source_name"-[1-9]* )
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
# copy first, continue to the next number without touching that directory.
while ! mkdir -- "$target_root" 2>/dev/null; do
  if [[ -e "$target_root" || -L "$target_root" ]]; then
    next_index=$((next_index + 1))
    target_root="$script_dir/$source_name-$next_index"
    continue
  fi
  printf 'Unable to create workspace directory: %s\n' "$target_root" >&2
  exit 1
done

# 1. Application, including frontend/node_modules so the copy runs without
#    npm install; build output, local database, and caches are left out.
if [[ ! -d "$app_source/frontend/node_modules" ]]; then
  printf 'Warning: %s has no frontend/node_modules; run npm install in the copy.\n' "$app_source" >&2
fi
tar -C "$app_source" \
  --exclude='./frontend/dist' \
  --exclude='./backend/data' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  -cf - . | tar -C "$target_root" -xf -

# 2. Git baseline, so `git diff` shows exactly what the agent changes. The
#    app's own .gitignore keeps node_modules, data, and build output out.
git -C "$target_root" init --quiet
{
  printf '\n# Antigravity workshop-local files\n'
  printf '/AGENTS.md\n'
  printf '/.agents/\n'
  printf '/.memory/\n'
  printf '/.scratch/\n'
} >> "$target_root/.git/info/exclude"
git -C "$target_root" add -A
git -C "$target_root" -c user.name='Workshop setup' -c user.email='setup@localhost' \
  commit --quiet --no-verify -m 'Baseline'

# 3. Workspace guidance.
cp -- "$agents_md_source" "$target_root/AGENTS.md"
mkdir -p -- "$target_root/.agents/rules"
cp -- "$memory_rule_source" "$target_root/.agents/rules/workspace-memory.md"
mkdir -p -- "$target_root/.agents/agents"
cp -R -- "$subagents_source"/. "$target_root/.agents/agents/"
python3 "$conductor_importer" "$target_root" --ref "$conductor_ref"

required_paths=(
  "$target_root/AGENTS.md"
  "$target_root/.agents/rules/workspace-memory.md"
  "$target_root/.agents/agents"
  "$target_root/.agents/plugins/conductor/plugin.json"
  "$target_root/backend/app/service.py"
  "$target_root/frontend/package.json"
  "$target_root/docs/spec.md"
)

for required_path in "${required_paths[@]}"; do
  if [[ ! -e "$required_path" ]]; then
    printf 'Workspace setup is incomplete; required path is missing: %s\n' "$required_path" >&2
    exit 1
  fi
done

if [[ -n "$(git -C "$target_root" status --porcelain --untracked-files=all)" ]]; then
  printf 'Generated workspace does not have a clean Git baseline.\n' >&2
  git -C "$target_root" status --short >&2
  exit 1
fi

setup_complete=true
trap - EXIT HUP INT TERM

printf 'Created Kanban Board Brownfield Conductor Subagents workspace: %s\n' "$target_root"
printf 'Next: install dependencies (see README.md), then open it as the workspace.\n'
