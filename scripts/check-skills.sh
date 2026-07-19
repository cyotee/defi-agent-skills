#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
count=0
while IFS= read -r -d '' f; do
  count=$((count + 1))
  if ! head -n 1 "$f" | grep -q '^---$'; then
    echo "FAIL: missing frontmatter: $f"
    fail=1
  fi
  if ! grep -q '^name:' "$f"; then
    echo "FAIL: missing name: $f"
    fail=1
  fi
  if ! grep -q '^description:' "$f"; then
    echo "FAIL: missing description: $f"
    fail=1
  fi
done < <(find "$ROOT/plugins" -name SKILL.md -print0 2>/dev/null || true)

if [[ "$count" -eq 0 ]]; then
  echo "OK: no skills yet (plugins empty or not checked out)"
  exit 0
fi
if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "OK: $count skill(s) passed frontmatter checks"
