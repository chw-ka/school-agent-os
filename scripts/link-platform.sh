#!/usr/bin/env bash
# Recreate symlinks from personal repo root → _platform/ (after clone or submodule update).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ ! -d _platform/shared-tools ]]; then
  echo "Run first: git submodule update --init --recursive" >&2
  exit 1
fi

link() {
  local target="$1" linkpath="$2"
  if [[ -e "$linkpath" && ! -L "$linkpath" ]]; then
    echo "Skip $linkpath (exists and is not a symlink)" >&2
    return
  fi
  ln -sfn "$target" "$linkpath"
  echo "Linked $linkpath -> $target"
}

link "_platform/shared-tools" "shared-tools"
link "_platform/templates" "templates"

# Cursor skills
link "../../_platform/.cursor/skills/meeting-minutes" ".cursor/skills/meeting-minutes"
link "../../_platform/.cursor/skills/_template" ".cursor/skills/_template"
link "../../_platform/.cursor/skills/tidy-up" ".cursor/skills/tidy-up"

# Cursor rules (platform-level, always-apply)
mkdir -p .cursor/rules
link "../../_platform/.cursor/rules/privacy.mdc" ".cursor/rules/privacy.mdc"

echo "Platform symlinks OK."
echo "Note: CLAUDE.md already imports _platform/CLAUDE.md via @_platform/CLAUDE.md — no symlink needed."
