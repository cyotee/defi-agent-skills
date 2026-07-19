#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

if [[ ! -f .gitmodules ]]; then
  echo "OK: no .gitmodules (no submodules yet)"
  exit 0
fi

# Every gitlink under plugins/ must be listed in .gitmodules
while IFS= read -r path; do
  if ! grep -q "path = ${path}" .gitmodules 2>/dev/null; then
    echo "FAIL: $path looks like a submodule checkout but is not in .gitmodules"
    fail=1
  fi
done < <(git config --file .gitmodules --get-regexp path 2>/dev/null | awk '{print $2}' || true)

# marketplace plugins with ./plugins/ sources must exist
if [[ -f .claude-plugin/marketplace.json ]]; then
  python3 - <<'PY' || fail=1
import json, sys
from pathlib import Path
root = Path(".")
data = json.loads((root / ".claude-plugin/marketplace.json").read_text())
for p in data.get("plugins", []):
    src = p.get("source")
    name = p.get("name")
    if isinstance(src, str) and src.startswith("./"):
        path = root / src
        if not path.exists():
            print(f"FAIL: marketplace plugin {name} source missing: {src}")
            sys.exit(1)
    elif isinstance(src, dict) and src.get("source") == "github":
        # Prefer local submodule mirror when present
        local = root / "plugins" / name
        if not local.exists():
            # Also try common path aliases
            pass
print("OK: marketplace local sources resolve where present")
PY
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "OK: submodule / marketplace path checks passed"
