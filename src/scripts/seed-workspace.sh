#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: seed-workspace.sh [--dry-run] <workspace-directory>

Seed a workspace with the repository's baseline AGENTS.md, rules, skills, and subagents.
Existing destination files are never overwritten.
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

if [[ $# -ne 1 ]]; then
  usage >&2
  exit 2
fi

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repository_root="$(cd -- "$script_dir/../.." && pwd)"
guidance_root="$repository_root/src/resources/workspace-guidance"
subagents_root="$repository_root/src/resources/subagents/sdlc-subagents/.agents/agents"
target_root="$1"

target_name="$(basename -- "$target_root")"
if [[ -z "$target_root" || "$target_root" =~ ^/+$ || "$target_name" == "." || "$target_name" == ".." ]]; then
  printf 'Refusing unsafe workspace target: %s\n' "$target_root" >&2
  exit 2
fi

if [[ -L "$target_root" ]]; then
  printf 'Refusing symlink workspace target: %s\n' "$target_root" >&2
  exit 2
fi

if [[ -e "$target_root" && ! -d "$target_root" ]]; then
  printf 'Workspace target is not a directory: %s\n' "$target_root" >&2
  exit 2
fi

required_sources=(
  "$guidance_root/agents/base.md"
  "$guidance_root/rules"
  "$guidance_root/skills"
  "$subagents_root"
)

for required_source in "${required_sources[@]}"; do
  if [[ ! -e "$required_source" ]]; then
    printf 'Required source is missing: %s\n' "$required_source" >&2
    exit 1
  fi
done

managed_directories=(
  "$target_root/.agents"
  "$target_root/.agents/agents"
  "$target_root/.agents/rules"
  "$target_root/.agents/skills"
)

for managed_directory in "${managed_directories[@]}"; do
  if [[ -L "$managed_directory" ]]; then
    printf 'Refusing symlink managed directory: %s\n' "$managed_directory" >&2
    exit 2
  fi
  if [[ -e "$managed_directory" && ! -d "$managed_directory" ]]; then
    printf 'Managed path is not a directory: %s\n' "$managed_directory" >&2
    exit 2
  fi
done

sources=("$guidance_root/agents/base.md")
destinations=("$target_root/AGENTS.md")

while IFS= read -r -d '' source_file; do
  relative_path="${source_file#"$guidance_root/rules/"}"
  sources+=("$source_file")
  destinations+=("$target_root/.agents/rules/$relative_path")
done < <(find "$guidance_root/rules" -type f -print0)

while IFS= read -r -d '' source_file; do
  relative_path="${source_file#"$guidance_root/skills/"}"
  sources+=("$source_file")
  destinations+=("$target_root/.agents/skills/$relative_path")
done < <(find "$guidance_root/skills" -type f -print0)

while IFS= read -r -d '' source_file; do
  relative_path="${source_file#"$subagents_root/"}"
  sources+=("$source_file")
  destinations+=("$target_root/.agents/agents/$relative_path")
done < <(find "$subagents_root" -type f -print0)

conflicts=()
for destination in "${destinations[@]}"; do
  if [[ -e "$destination" || -L "$destination" ]]; then
    conflicts+=("$destination")
  fi
done

if (( ${#conflicts[@]} > 0 )); then
  printf 'Refusing to overwrite existing workspace files:\n' >&2
  printf '  %s\n' "${conflicts[@]}" >&2
  exit 1
fi

if [[ "$dry_run" == true ]]; then
  printf 'Would seed workspace: %s\n' "$target_root"
  for index in "${!sources[@]}"; do
    printf '  %s -> %s\n' "${sources[$index]}" "${destinations[$index]}"
  done
  exit 0
fi

mkdir -p -- "$target_root"

for index in "${!sources[@]}"; do
  destination="${destinations[$index]}"
  mkdir -p -- "$(dirname -- "$destination")"
  cp -- "${sources[$index]}" "$destination"
done

printf 'Seeded workspace: %s\n' "$target_root"
printf 'Created %d files.\n' "${#sources[@]}"
