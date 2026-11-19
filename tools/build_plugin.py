"""Construit le plugin Claude Code AUTO+ à partir de .claude/ (source de vérité).

Le plugin (plugins/autoplus/) est généré : ne pas le modifier à la main.
Modifier les fichiers de .claude/agents/ et .claude/skills/, puis :

    python tools/build_plugin.py --write   # régénère agents/ et skills/ du plugin
    python tools/build_plugin.py --check   # échoue si le plugin diffère de .claude/ (CI)

Les commandes (plugins/autoplus/commands/), le manifeste et le README du plugin
sont propres au plugin et ne sont pas générés.
"""
from __future__ import annotations

import argparse
import filecmp
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / ".claude"
PLUGIN = ROOT / "plugins" / "autoplus"

AGENTS = [
    "startup-strategist", "market-researcher", "competitor-analyst", "customer-researcher",
    "business-strategist", "pmm", "growth-lead", "garage-partnerships", "gtm-strategist", "pitch-coach",
]
SKILLS = [
    "autoplus-cso", "validation-prix", "design-experience", "revue-pitch", "revue-business-hebdo",
    "autoplus-market-intel", "autoplus-business-model", "autoplus-gtm-growth", "autoplus-brand-voice",
]


def expected_files() -> dict[Path, Path]:
    """chemin dans le plugin -> fichier source."""
    out: dict[Path, Path] = {}
    for a in AGENTS:
        out[Path("agents") / f"{a}.md"] = SRC / "agents" / f"{a}.md"
    for s in SKILLS:
        for f in sorted((SRC / "skills" / s).rglob("*")):
            if f.is_file():
                out[Path("skills") / s / f.relative_to(SRC / "skills" / s)] = f
    return out


def run(write: bool) -> int:
    exp = expected_files()
    errors = [f"source manquante : {src.relative_to(ROOT)}" for src in exp.values() if not src.exists()]
    if errors:
        print("\n".join("ERREUR " + e for e in errors))
        return 1

    if write:
        for sub in ("agents", "skills"):
            shutil.rmtree(PLUGIN / sub, ignore_errors=True)
        for rel, src in exp.items():
            dst = PLUGIN / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)

    present = {p.relative_to(PLUGIN) for sub in ("agents", "skills") for p in (PLUGIN / sub).rglob("*") if p.is_file()} \
        if (PLUGIN / "agents").exists() else set()
    for rel, src in exp.items():
        if rel not in present:
            errors.append(f"absent du plugin : {rel}")
        elif not filecmp.cmp(PLUGIN / rel, src, shallow=False):
            errors.append(f"diffère de la source : {rel}")
    for rel in sorted(present - exp.keys()):
        errors.append(f"fichier en trop dans le plugin : {rel}")

    manifest = PLUGIN / ".claude-plugin" / "plugin.json"
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("name") != "autoplus":
            errors.append("plugin.json : name doit être « autoplus »")
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"plugin.json illisible : {e}")

    for e in errors:
        print("ERREUR", e)
    print(f"plugin autoplus : {len(AGENTS)} agents, {len(SKILLS)} skills, {len(exp)} fichiers générés : "
          + ("OK" if not errors else f"{len(errors)} erreur(s)"))
    return 1 if errors else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    a = ap.parse_args()
    sys.exit(run(write=a.write))
