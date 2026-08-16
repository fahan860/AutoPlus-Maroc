#!/usr/bin/env python3
"""
Validation de la Knowledge Base AUTO+ (ai/data/processed/*.csv)

Vérifie, pour chaque entrée d'un corpus CSV conforme à ai/docs/KB_SCHEMA.md :
  - champs obligatoires manquants
  - catégories (`systeme`) invalides (hors liste fermée du schéma)
  - codes DTC mal formés
  - doublons (id, ou couple symptome+vehicule identique)
  - source manquante ou non tracée
  - incohérences évidentes (gravite/langue hors enum, dtc_code sans systeme=obd_dtc, etc.)

Usage :
    python validate_knowledge_base.py chemin/vers/corpus.csv [autre_corpus.csv ...]

Code de sortie : 0 si aucune erreur bloquante, 1 sinon.
Les avertissements n'empêchent pas la validation (code 0) mais sont affichés.
"""

import csv
import re
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "id", "symptome", "vehicule", "systeme", "cause", "explication",
    "verification", "gravite", "source", "langue", "date_maj",
]
OPTIONAL_FIELDS = ["dtc_code", "page_source", "tags"]
ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS

VALID_CATEGORIES = {
    "obd_dtc", "moteur", "transmission", "freins", "electrique",
    "refroidissement", "carburant", "demarrage", "surchauffe",
    "perte_puissance", "bruit_vibration", "maintenance",
}
VALID_GRAVITE = {"faible", "moyenne", "elevee", "critique"}
VALID_LANGUE = {"fr", "ar", "darija"}

DTC_RE = re.compile(r"^[PBCU][0-9]{4}$")  # ex: P0301, B0012, C0035, U0100
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Issue:
    def __init__(self, level, entry_id, field, message):
        self.level = level  # "ERROR" ou "WARNING"
        self.entry_id = entry_id or "?"
        self.field = field or "-"
        self.message = message

    def __str__(self):
        return f"[{self.level}] {self.entry_id} ({self.field}): {self.message}"


def load_rows(path: Path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing_header = [c for c in REQUIRED_FIELDS if c not in (reader.fieldnames or [])]
        if missing_header:
            raise SystemExit(
                f"Fichier {path}: colonnes obligatoires absentes de l'en-tête : {missing_header}"
            )
        return list(reader)


def validate(rows, source_file):
    issues = []
    seen_ids = {}
    seen_symptome_vehicule = {}

    for i, row in enumerate(rows, start=2):  # ligne 1 = header
        rid = (row.get("id") or "").strip()
        loc = rid or f"ligne {i}"

        # 1. Champs obligatoires manquants
        for field in REQUIRED_FIELDS:
            if not (row.get(field) or "").strip():
                issues.append(Issue("ERROR", loc, field, "champ obligatoire manquant ou vide"))

        # Si pas d'id, impossible de tracer proprement le doublon plus loin
        if not rid:
            continue

        # 2. Doublons d'id
        if rid in seen_ids:
            issues.append(Issue("ERROR", rid, "id",
                                 f"id dupliqué (déjà vu ligne {seen_ids[rid]})"))
        else:
            seen_ids[rid] = i

        # 2bis. Doublons quasi-exacts (même symptôme + même véhicule)
        key = ((row.get("symptome") or "").strip().lower(),
               (row.get("vehicule") or "").strip().lower())
        if key[0]:
            if key in seen_symptome_vehicule:
                issues.append(Issue("WARNING", rid, "symptome",
                                     f"symptôme+véhicule très proche de {seen_symptome_vehicule[key]} "
                                     "— vérifier qu'il ne s'agit pas d'un doublon"))
            else:
                seen_symptome_vehicule[key] = rid

        # 3. Catégories invalides
        systeme_raw = (row.get("systeme") or "").strip()
        categories = [c.strip() for c in systeme_raw.split(";") if c.strip()]
        if not categories:
            issues.append(Issue("ERROR", rid, "systeme", "aucune catégorie renseignée"))
        else:
            invalid = [c for c in categories if c not in VALID_CATEGORIES]
            if invalid:
                issues.append(Issue("ERROR", rid, "systeme",
                                     f"catégorie(s) invalide(s) hors KB_SCHEMA.md : {invalid}"))

        # 4. gravite / langue hors enum
        gravite = (row.get("gravite") or "").strip()
        if gravite and gravite not in VALID_GRAVITE:
            issues.append(Issue("ERROR", rid, "gravite",
                                 f"valeur '{gravite}' hors enum {sorted(VALID_GRAVITE)}"))

        langue = (row.get("langue") or "").strip()
        if langue and langue not in VALID_LANGUE:
            issues.append(Issue("ERROR", rid, "langue",
                                 f"valeur '{langue}' hors enum {sorted(VALID_LANGUE)}"))

        # 5. DTC mal formés
        dtc = (row.get("dtc_code") or "").strip()
        if dtc and not DTC_RE.match(dtc):
            issues.append(Issue("ERROR", rid, "dtc_code",
                                 f"code DTC '{dtc}' mal formé (attendu ex. P0301)"))

        # 5bis. Incohérence dtc_code renseigné mais systeme ne contient pas obd_dtc
        if dtc and "obd_dtc" not in categories:
            issues.append(Issue("WARNING", rid, "dtc_code/systeme",
                                 f"dtc_code='{dtc}' renseigné mais 'obd_dtc' absent de systeme={systeme_raw}"))

        # 6. Source manquante / non tracée
        source = (row.get("source") or "").strip()
        if not source:
            issues.append(Issue("ERROR", rid, "source", "source manquante — traçabilité impossible"))

        # 7. date_maj mal formée
        date_maj = (row.get("date_maj") or "").strip()
        if date_maj and not DATE_RE.match(date_maj):
            issues.append(Issue("WARNING", rid, "date_maj",
                                 f"date '{date_maj}' ne respecte pas le format AAAA-MM-JJ"))

        # 8. Incohérence évidente : texte cause/explication identique au symptome (signe de remplissage automatique)
        cause = (row.get("cause") or "").strip().lower()
        symptome = (row.get("symptome") or "").strip().lower()
        if cause and symptome and cause == symptome:
            issues.append(Issue("WARNING", rid, "cause",
                                 "cause identique au symptôme mot pour mot — probable remplissage artificiel"))

    return issues


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1

    total_errors = 0
    total_warnings = 0

    for arg in argv[1:]:
        path = Path(arg)
        if not path.exists():
            print(f"Fichier introuvable : {path}")
            total_errors += 1
            continue

        rows = load_rows(path)
        issues = validate(rows, path)

        errors = [i for i in issues if i.level == "ERROR"]
        warnings = [i for i in issues if i.level == "WARNING"]
        total_errors += len(errors)
        total_warnings += len(warnings)

        print(f"\n=== {path} — {len(rows)} entrées ===")
        if not issues:
            print("OK — aucune anomalie détectée.")
        else:
            for issue in issues:
                print(str(issue))
            print(f"\n{len(errors)} erreur(s), {len(warnings)} avertissement(s).")

    print(f"\n=== Résumé global : {total_errors} erreur(s), {total_warnings} avertissement(s) ===")
    return 1 if total_errors > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
