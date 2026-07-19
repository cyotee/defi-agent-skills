#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN="${1:-}"
if [[ -z "$PLUGIN" ]]; then
  echo "Usage: $0 plugins/<name>"
  exit 1
fi
PATH_REL="${PLUGIN#./}"
cd "$ROOT/$PATH_REL"
git fetch origin
git checkout main 2>/dev/null || git checkout master
git pull --ff-only
echo "Updated $PATH_REL to $(git rev-parse --short HEAD)"
echo "Stage from repo root: git add $PATH_REL && git commit -m \"chore: bump $(basename "$PATH_REL") submodule\""
