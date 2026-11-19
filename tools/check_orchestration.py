"""Vérifie les règles d'orchestration CSO d'AUTO+.

Contrôles :
1. Chaque sous-agent cité dans le routage et la matrice de vérification existe dans .claude/agents/.
2. Matrice : producteur != vérificateur ; un seul vérificateur par producteur ; chaque sous-agent business
   en a un ; les paires réciproques (A vérifie B et B vérifie A) ne sont admises qu'entre rôles de recherche.
3. Aucun sous-agent ne peut lancer de sous-agent (pas d'outil Agent ni Task) : le CSO reste la session principale.
4. Chaque sous-agent business rend une section « À contre-vérifier ».
5. Le contradicteur par défaut du contre-examen existe.

Usage : python tools/check_orchestration.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / ".claude" / "agents"
CSO = ROOT / ".claude" / "skills" / "autoplus-cso" / "SKILL.md"

BUSINESS = {
    "startup-strategist", "market-researcher", "competitor-analyst", "customer-researcher",
    "business-strategist", "pmm", "growth-lead", "garage-partnerships", "gtm-strategist", "pitch-coach",
}
RESEARCH_PAIRS_OK = {frozenset({"market-researcher", "competitor-analyst"}),
                     frozenset({"startup-strategist", "customer-researcher"})}


def block(text: str, tag: str) -> str:
    m = re.search(rf"<!-- {tag} -->\n(.*?)\n<!-- /{tag} -->", text, re.S)
    if not m:
        raise SystemExit(f"bloc <!-- {tag} --> introuvable dans {CSO}")
    return m.group(1)


def agents_in(md: str) -> list[list[str]]:
    rows = []
    for line in md.splitlines():
        if line.startswith("|") and "`" in line:
            rows.append(re.findall(r"`([a-z-]+)`", line))
    return rows


def agent_meta(path: Path) -> tuple[str, list[str], str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    fm = dict(l.split(": ", 1) for l in m.group(1).splitlines() if ": " in l)
    return fm["name"], [t.strip() for t in fm.get("tools", "").split(",")], m.group(2)


def main() -> int:
    errors: list[str] = []
    meta = {p.stem: agent_meta(p) for p in AGENTS.glob("*.md")}
    cso = CSO.read_text(encoding="utf-8")

    routed = {a for row in agents_in(block(cso, "routage")) for a in row}
    for a in sorted(routed - meta.keys()):
        errors.append(f"routage : sous-agent inconnu {a}")
    for a in sorted(BUSINESS - routed):
        errors.append(f"routage : sous-agent business absent du routage {a}")

    matrix: dict[str, str] = {}
    for row in agents_in(block(cso, "matrice-verification")):
        if len(row) != 2:
            errors.append(f"matrice : ligne invalide {row}")
            continue
        prod, verif = row
        for a in row:
            if a not in meta:
                errors.append(f"matrice : sous-agent inconnu {a}")
        if prod == verif:
            errors.append(f"matrice : {prod} se vérifie lui-même")
        if prod in matrix:
            errors.append(f"matrice : {prod} a deux vérificateurs")
        matrix[prod] = verif
    for a in sorted(BUSINESS - matrix.keys()):
        errors.append(f"matrice : aucun vérificateur pour {a}")
    for p, v in matrix.items():
        if matrix.get(v) == p and frozenset({p, v}) not in RESEARCH_PAIRS_OK:
            errors.append(f"matrice : vérification réciproque non autorisée {p} <-> {v}")

    for name, (fname, tools, body) in meta.items():
        if name != fname:
            errors.append(f"{name}.md : name={fname}")
        if {"Agent", "Task"} & set(tools):
            errors.append(f"{name} : peut lancer des sous-agents (outil Agent/Task)")
        if name in BUSINESS and "À contre-vérifier" not in body:
            errors.append(f"{name} : pas de section « À contre-vérifier »")

    m = re.search(r"par défaut `([a-z-]+)`", cso)
    if not m or m.group(1) not in meta:
        errors.append("contre-examen : contradicteur par défaut absent ou inconnu")

    for e in errors:
        print("ERREUR", e)
    print(f"{len(meta)} sous-agents, {len(routed)} routés, {len(matrix)} paires de vérification : "
          + ("OK" if not errors else f"{len(errors)} erreur(s)"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
