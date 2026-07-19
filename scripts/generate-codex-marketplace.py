#!/usr/bin/env python3
"""Generate Codex-native marketplace artifacts from Claude marketplace SoT.

Source of truth:
  .claude-plugin/marketplace.json
  plugins/<name>/  (skills, .claude-plugin/plugin.json)

Writes (committed, lean — wshobson-style dual-ship):
  .agents/plugins/marketplace.json
  plugins/<name>/.codex-plugin/plugin.json

Does NOT rewrite skill bodies. Hooks remain Claude-first; Codex may ignore
or trust-review them separately.

Usage:
  python3 scripts/generate-codex-marketplace.py
  python3 scripts/generate-codex-marketplace.py --check   # exit 1 on drift
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGINS_DIR = ROOT / "plugins"

# Map Claude categories / free-form tags to Codex-style categories when missing.
DEFAULT_CATEGORY = "Productivity"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_claude_plugin_manifest(plugin_dir: Path) -> dict[str, Any]:
    path = plugin_dir / ".claude-plugin" / "plugin.json"
    if path.is_file():
        return load_json(path)
    return {}


def has_skill_packages(plugin_dir: Path) -> bool:
    skills = plugin_dir / "skills"
    if not skills.is_dir():
        return False
    for child in skills.iterdir():
        if child.is_dir() and (child / "SKILL.md").is_file():
            return True
    return False


def has_hooks(plugin_dir: Path) -> bool:
    return (plugin_dir / "hooks" / "hooks.json").is_file()


def has_mcp(plugin_dir: Path) -> bool:
    return (plugin_dir / ".mcp.json").is_file()


def ensure_root_skill_package(plugin_dir: Path, name: str) -> bool:
    """If plugin has root SKILL.md but no skills/* packages, promote into skills/<name>/."""
    root_skill = plugin_dir / "SKILL.md"
    if not root_skill.is_file():
        return False
    if has_skill_packages(plugin_dir):
        return False
    dest = plugin_dir / "skills" / name / "SKILL.md"
    if dest.is_file():
        return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(root_skill.read_text(encoding="utf-8"), encoding="utf-8")
    return True


def codex_plugin_manifest(
    name: str,
    claude_entry: dict[str, Any],
    claude_plugin: dict[str, Any],
    plugin_dir: Path,
    *,
    promote: bool = True,
) -> dict[str, Any]:
    version = (
        claude_plugin.get("version")
        or claude_entry.get("version")
        or "0.1.0"
    )
    description = (
        claude_plugin.get("description")
        or claude_entry.get("description")
        or f"{name} plugin"
    )
    author = claude_plugin.get("author") or claude_entry.get("author")
    keywords = claude_plugin.get("keywords") or claude_entry.get("tags") or []

    manifest: dict[str, Any] = {
        "name": name,
        "version": version,
        "description": description,
    }
    if author:
        if isinstance(author, str):
            manifest["author"] = {"name": author}
        else:
            manifest["author"] = author
    if keywords:
        manifest["keywords"] = list(keywords)
    license_ = claude_plugin.get("license")
    if license_:
        manifest["license"] = license_

    # Prefer standard skills/ packages; promote root SKILL.md when needed.
    if promote:
        ensure_root_skill_package(plugin_dir, name)
    if has_skill_packages(plugin_dir) or (plugin_dir / "skills" / name / "SKILL.md").is_file():
        manifest["skills"] = "./skills/"

    if has_hooks(plugin_dir):
        # Codex auto-discovers hooks/hooks.json; explicit path is fine and clear.
        manifest["hooks"] = "./hooks/hooks.json"

    if has_mcp(plugin_dir):
        manifest["mcpServers"] = "./.mcp.json"

    # Install-surface metadata (Codex desktop / plugin directory)
    category = claude_entry.get("category") or DEFAULT_CATEGORY
    # Codex categories often use Title Case
    category_display = category[0].upper() + category[1:] if category else DEFAULT_CATEGORY
    manifest["interface"] = {
        "displayName": name,
        "shortDescription": description[:120] if len(description) > 120 else description,
        "longDescription": description,
        "category": category_display,
        "developerName": (
            author.get("name")
            if isinstance(author, dict)
            else (author if isinstance(author, str) else "cyotee")
        ),
    }

    return manifest


def codex_marketplace_entry(
    name: str,
    claude_entry: dict[str, Any],
) -> dict[str, Any]:
    category = claude_entry.get("category") or "development"
    category_display = category[0].upper() + category[1:]

    entry: dict[str, Any] = {
        "name": name,
        "source": {
            "source": "local",
            "path": f"./plugins/{name}",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": category_display,
    }

    # Helpful optional metadata for humans / UIs
    if claude_entry.get("description"):
        entry["description"] = claude_entry["description"]
    if claude_entry.get("version"):
        entry["version"] = claude_entry["version"]
    if claude_entry.get("author"):
        entry["author"] = claude_entry["author"]

    return entry


def generate(*, promote_root_skills: bool = True) -> dict[str, str]:
    """Return map of relative path -> file contents to write."""
    if not CLAUDE_MARKETPLACE.is_file():
        raise SystemExit(f"Missing Claude marketplace SoT: {CLAUDE_MARKETPLACE}")

    claude = load_json(CLAUDE_MARKETPLACE)
    plugins_meta = claude.get("plugins") or []
    if not plugins_meta:
        raise SystemExit("Claude marketplace has no plugins[]")

    written: dict[str, str] = {}
    codex_plugins: list[dict[str, Any]] = []
    skipped: list[str] = []

    for entry in plugins_meta:
        name = entry.get("name")
        if not name:
            continue
        plugin_dir = PLUGINS_DIR / name
        if not plugin_dir.is_dir():
            skipped.append(f"{name} (missing plugins/{name})")
            continue

        claude_plugin = read_claude_plugin_manifest(plugin_dir)
        if promote_root_skills:
            ensure_root_skill_package(plugin_dir, name)
        manifest = codex_plugin_manifest(
            name, entry, claude_plugin, plugin_dir, promote=False
        )
        rel_manifest = f"plugins/{name}/.codex-plugin/plugin.json"
        written[rel_manifest] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

        codex_plugins.append(codex_marketplace_entry(name, entry))

    meta = claude.get("metadata") or {}
    display = meta.get("description") or "cyotee plugin marketplace"
    # Keep displayName short for pickers
    marketplace = {
        "name": claude.get("name") or "cyotee",
        "interface": {
            "displayName": "cyotee",
            "shortDescription": (
                display[:160] + "…" if len(display) > 160 else display
            ),
        },
        "metadata": {
            "description": display,
            "version": meta.get("version") or "0.0.0",
            "generatedFrom": ".claude-plugin/marketplace.json",
            "generator": "scripts/generate-codex-marketplace.py",
            "notes": (
                "Claude Code is the source of truth. Skills (SKILL.md) are portable. "
                "Hooks and Claude-specific automation may not fully apply on Codex."
            ),
        },
        "plugins": codex_plugins,
    }
    written[".agents/plugins/marketplace.json"] = (
        json.dumps(marketplace, indent=2, ensure_ascii=False) + "\n"
    )

    if skipped:
        print("Skipped entries:", file=sys.stderr)
        for s in skipped:
            print(f"  - {s}", file=sys.stderr)

    return written


def apply_writes(files: dict[str, str], check: bool) -> int:
    drift = []
    for rel, content in sorted(files.items()):
        path = ROOT / rel
        if check:
            if not path.is_file():
                drift.append(f"missing {rel}")
                continue
            existing = path.read_text(encoding="utf-8")
            if existing != content:
                drift.append(f"stale {rel}")
            continue

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"wrote {rel}")

    if check:
        if drift:
            print("Codex marketplace drift detected:", file=sys.stderr)
            for d in drift:
                print(f"  - {d}", file=sys.stderr)
            print(
                "\nRun: python3 scripts/generate-codex-marketplace.py",
                file=sys.stderr,
            )
            return 1
        print("OK: Codex marketplace artifacts match generator output")
        return 0

    print(f"\nGenerated {len(files)} file(s) for Codex dual-ship.")
    print("Claude SoT unchanged: .claude-plugin/marketplace.json")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit 1 if committed Codex artifacts drift from generator",
    )
    args = parser.parse_args()
    files = generate(promote_root_skills=not args.check)
    return apply_writes(files, check=args.check)


if __name__ == "__main__":
    raise SystemExit(main())
