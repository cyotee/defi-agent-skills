#!/usr/bin/env bash
# Install agent skills into OpenCode skill directories.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="${OPENCODE_SKILLS_DIR:-$HOME/.config/opencode/skills}"
mkdir -p "$DEST"

install_plugin() {
  local name="$1"
  local src="$ROOT/plugins/$name/skills"
  if [[ ! -d "$src" ]]; then
    echo "skip $name (no skills dir)"
    return
  fi
  for skill in "$src"/*; do
    [[ -d "$skill" ]] || continue
    local base
    base="$(basename "$skill")"
    rm -rf "$DEST/$base"
    cp -R "$skill" "$DEST/$base"
    echo "installed $base -> $DEST/$base"
  done
}

if [[ $# -eq 0 ]]; then
  for p in "$ROOT/plugins"/*; do
    [[ -d "$p" ]] || continue
    install_plugin "$(basename "$p")"
  done
else
  for name in "$@"; do
    install_plugin "$name"
  done
fi
echo "Done. OpenCode skills dir: $DEST"
