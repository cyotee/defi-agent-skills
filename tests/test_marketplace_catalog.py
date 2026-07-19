#!/usr/bin/env python3
"""Structural tests for the shipped agent marketplace catalog."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
GITMODULES = ROOT / ".gitmodules"

ALLOWED = {
    "foundry-agent",
    "bankr-ops",
    "defi-primitives",
    "permit2-ops",
    "balancer-v3-ops",
    "indexedex-ops",
}

FORBIDDEN_SUBSTRINGS = (
    "crane",
    "forge-fuzz",
    "playwright",
    "synpress",
    "boardgame",
    "aave-v3-skill",
    "uniswap-v3-skill",
)


class MarketplaceCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.assertTrue(MARKETPLACE.is_file())
        self.data = json.loads(MARKETPLACE.read_text())

    def test_plugins_are_agent_ops_only(self) -> None:
        names = [p["name"] for p in self.data["plugins"]]
        self.assertTrue(names)
        for name in names:
            for bad in FORBIDDEN_SUBSTRINGS:
                self.assertNotIn(bad, name.lower())
            self.assertTrue(name in ALLOWED or name.endswith("-ops"), name)

    def test_every_plugin_has_public_github_source(self) -> None:
        for p in self.data["plugins"]:
            src = p["source"]
            self.assertEqual(src.get("source"), "github")
            self.assertTrue(src.get("repo", "").startswith("cyotee/"))

    def test_required_mvp_plugins_present(self) -> None:
        names = {p["name"] for p in self.data["plugins"]}
        for required in ALLOWED:
            self.assertIn(required, names)

    def test_all_skills_have_frontmatter(self) -> None:
        for plugin in (ROOT / "plugins").iterdir():
            if not plugin.is_dir():
                continue
            skills = list((plugin / "skills").glob("*/SKILL.md"))
            self.assertTrue(skills, plugin.name)
            for skill in skills:
                text = skill.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---"), skill)
                self.assertIn("name:", text)
                self.assertIn("description:", text)

    def test_each_plugin_has_runbook_skill(self) -> None:
        for plugin in (ROOT / "plugins").iterdir():
            if not plugin.is_dir():
                continue
            skills = list((plugin / "skills").glob("*/SKILL.md"))
            has_goal = False
            has_safety = False
            for skill in skills:
                lower = skill.read_text(encoding="utf-8").lower()
                if "goal" in lower or "inspect" in lower or "when to use" in lower:
                    has_goal = True
                if "safety" in lower or "confirm" in lower or "verify" in lower:
                    has_safety = True
            self.assertTrue(has_goal, f"{plugin.name} missing goal/inspect skill")
            self.assertTrue(has_safety, f"{plugin.name} missing safety/verify skill")

    def test_gitmodules_covers_plugins(self) -> None:
        gm = GITMODULES.read_text()
        for p in self.data["plugins"]:
            self.assertIn(f"plugins/{p['name']}", gm)


if __name__ == "__main__":
    unittest.main()
