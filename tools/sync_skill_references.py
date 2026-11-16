"""Synchronise et vérifie les références des skills business AUTO+.

Source de vérité : docs/business/*.md et .claude/skills/autoplus-brand-voice/SKILL.md.
Les skills embarquent des copies (dossier references/) pour rester autonomes,
par exemple dans le plugin. Ce script garantit que ces copies et les
procédures recopiées dans les SKILL.md restent identiques à la source.

Usage :
    python tools/sync_skill_references.py --check   # échoue si une copie diverge (CI)
    python tools/sync_skill_references.py --write   # recopie les références depuis docs/business
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "business"
SKILLS = ROOT / ".claude" / "skills"

DOC = {
    "07": "07_strategie_startup.md",
    "08": "08_marche_concurrence.md",
    "09": "09_gtm_lancement_casablanca.md",
    "10": "10_kpi_experiences.md",
    "11": "11_roles_business.md",
    "12": "12_procedures_business.md",
}

# skill -> documents copiés dans references/
MANIFEST: dict[str, list[str]] = {
    "autoplus-cso": ["07", "08", "09", "10", "11", "12"],
    "autoplus-market-intel": ["07", "08", "12"],
    "autoplus-business-model": ["07", "08", "10", "12"],
    "autoplus-gtm-growth": ["07", "09", "10", "12"],
    "validation-prix": ["07", "08", "10"],
    "design-experience": ["10"],
    "revue-pitch": ["07", "08", "10"],
    "revue-business-hebdo": ["09", "10"],
}

PROC_RE = re.compile(r"<!-- procedure:([a-z0-9-]+) -->\n(.*?)\n<!-- /procedure -->", re.S)


def procedures_12() -> dict[str, str]:
    """Sections '## <nom>' du document 12, sans le titre."""
    text = (DOCS / DOC["12"]).read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^## ([a-z0-9-]+)\n(.*?)(?=^## |\Z)", text, re.S | re.M):
        out[m.group(1)] = m.group(2).strip().rstrip("-").strip()
    return out


def check_frontmatter(skill_md: Path, expected: str) -> list[str]:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return [f"{skill_md}: frontmatter absent"]
    fields = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    errs = []
    if fields.get("name", "").strip() != expected:
        errs.append(f"{skill_md}: name != {expected}")
    desc = fields.get("description", "").strip()
    if not desc or len(desc) > 1024:
        errs.append(f"{skill_md}: description vide ou > 1024 caractères")
    return errs


def run(write: bool) -> int:
    if not DOCS.exists():
        print("docs/business/ absent : rien à vérifier (fusionner la PR des documents business d'abord).")
        return 1
    errors: list[str] = []
    procs = procedures_12()

    for skill, docs in MANIFEST.items():
        sdir = SKILLS / skill
        skill_md = sdir / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"{skill}: SKILL.md manquant")
            continue
        errors += check_frontmatter(skill_md, skill)
        refdir = sdir / "references"
        expected = {DOC[d] for d in docs}
        if write:
            refdir.mkdir(exist_ok=True)
        for name in sorted(expected):
            src, dst = DOCS / name, refdir / name
            if write:
                dst.write_bytes(src.read_bytes())
            elif not dst.exists():
                errors.append(f"{skill}: references/{name} manquant")
            elif dst.read_bytes() != src.read_bytes():
                errors.append(f"{skill}: references/{name} diffère de docs/business/{name}")
        if refdir.exists():
            for extra in refdir.iterdir():
                if extra.name not in expected:
                    errors.append(f"{skill}: references/{extra.name} hors manifeste")
        for m in PROC_RE.finditer(skill_md.read_text(encoding="utf-8")):
            name, body = m.group(1), m.group(2).strip()
            if name not in procs:
                errors.append(f"{skill}: procédure « {name} » absente du document 12")
            elif body != procs[name]:
                errors.append(f"{skill}: procédure « {name} » diffère du document 12")

    brand = [p for p in SKILLS.glob("*/SKILL.md") if re.search(r"^name:\s*autoplus-brand-voice\s*$", p.read_text(encoding="utf-8"), re.M)]
    if len(brand) != 1:
        errors.append(f"brand-voice : {len(brand)} définitions (une seule attendue)")

    for e in errors:
        print("ERREUR", e)
    n_refs = sum(len(v) for v in MANIFEST.values())
    print(f"{len(MANIFEST)} skills, {n_refs} références, {len(PROC_RE.findall(''.join(p.read_text(encoding='utf-8') for p in SKILLS.glob('*/SKILL.md'))))} procédures balisées : "
          + ("OK" if not errors else f"{len(errors)} erreur(s)"))
    return 1 if errors else 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if a.write:
        run(write=True)
    sys.exit(run(write=False))
