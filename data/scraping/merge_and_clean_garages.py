"""
Fusion + nettoyage des 3 CSV bruts de garages scrapes (telecontact.ma)
avant import dans la table Postgres `garages` (voir api/migrations/001_create_garages.sql).

Sources (toutes centrees sur les memes ~100 fiches telecontact.ma,
scrapees a des moments differents avec des configs differentes) :
  - garages.csv                          (100 lignes, categorie = slug, adresse partielle)
  - garages_v2.csv                       (100 lignes, memes ids, adresse TOUJOURS vide)
  - garages_casablanca_telecontact.csv   (85 lignes, categorie lisible, adresse quasi complete,
                                           notes/avis reels -> source la plus fiable)

Strategie de fusion (cle = lien_fiche, unique par fiche) :
  - Union des 3 sources -> 1 ligne par lien_fiche (100 fiches uniques au total)
  - Pour chaque champ, on prend la 1ere valeur non vide dans l'ordre de priorite
    telecontact (le + complet) > garages.csv > garages_v2.csv
  - encodage source ISO-8859-1 -> reecrit en UTF-8
  - telephone normalise au format "0X XX XX XX XX" (10 chiffres, sinon vide)
  - note : virgule francaise -> point ; mise a vide si nb_avis = 0 (pas de vrai avis)
  - a_completer = true si telephone toujours manquant apres fusion
  - source = 'telecontact.ma'

Usage :
    python merge_and_clean_garages.py garages.csv garages_v2.csv garages_casablanca_telecontact.csv -o garages_clean.csv
"""

import argparse
import csv
import re
import sys

FIELDNAMES = [
    "nom", "categorie", "adresse", "ville", "telephone",
    "note", "nb_avis", "lien_fiche", "source", "a_completer",
]


def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def normalize_phone(raw: str) -> str:
    """Retourne le tel au format '0X XX XX XX XX' si valide (10 chiffres, commence par 0), sinon ''."""
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if len(digits) != 10 or not digits.startswith("0"):
        return ""
    return " ".join([digits[0:2], digits[2:4], digits[4:6], digits[6:8], digits[8:10]])


def parse_note(raw: str) -> float:
    raw = (raw or "").strip().replace(",", ".")
    try:
        return float(raw)
    except ValueError:
        return 0.0


def parse_int(raw: str) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return 0


def load_csv(path: str) -> list:
    with open(path, encoding="iso-8859-1", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def first_nonempty(*values: str) -> str:
    for v in values:
        v = normalize_space(v)
        if v:
            return v
    return ""


def merge_sources(paths: list) -> list:
    """paths donnes dans l'ordre de PRIORITE decroissante."""
    sources = [load_csv(p) for p in paths]
    indexed = [{normalize_space(r["lien_fiche"]): r for r in rows if normalize_space(r.get("lien_fiche", ""))}
               for rows in sources]

    # union ordonnee des cles (garde l'ordre d'apparition, priorite au 1er fichier)
    seen = set()
    ordered_keys = []
    for idx in indexed:
        for k in idx:
            if k not in seen:
                seen.add(k)
                ordered_keys.append(k)

    merged = []
    for key in ordered_keys:
        rows_for_key = [idx[key] for idx in indexed if key in idx]

        nom = first_nonempty(*[r.get("nom", "") for r in rows_for_key])
        categorie = first_nonempty(*[r.get("categorie", "") for r in rows_for_key])
        adresse = first_nonempty(*[r.get("adresse", "") for r in rows_for_key])
        ville = first_nonempty(*[r.get("ville", "") for r in rows_for_key]) or "Casablanca"
        telephone_raw = first_nonempty(*[r.get("telephone", "") for r in rows_for_key])
        telephone = normalize_phone(telephone_raw)

        # note/nb_avis : on prend la 1ere source qui a un vrai avis (nb_avis > 0),
        # sinon 0/0 par defaut
        note_val, nb_avis_val = 0.0, 0
        for r in rows_for_key:
            n = parse_int(r.get("nb_avis", 0))
            if n > 0:
                note_val = parse_note(r.get("note", 0))
                nb_avis_val = n
                break

        note = "" if nb_avis_val == 0 else f"{note_val:.1f}"
        a_completer = "true" if not telephone else "false"

        merged.append({
            "nom": nom,
            "categorie": categorie,
            "adresse": adresse,
            "ville": ville,
            "telephone": telephone,
            "note": note,
            "nb_avis": str(nb_avis_val),
            "lien_fiche": key,
            "source": "telecontact.ma",
            "a_completer": a_completer,
        })

    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("inputs", nargs="+", help="CSV sources, dans l'ordre de priorite decroissante")
    parser.add_argument("-o", "--out", required=True, help="CSV de sortie (UTF-8)")
    args = parser.parse_args()

    merged = merge_sources(args.inputs)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(merged)

    n_a_completer = sum(1 for r in merged if r["a_completer"] == "true")
    n_avec_avis = sum(1 for r in merged if r["nb_avis"] != "0")

    print(f"Sources fusionnees   : {len(args.inputs)}")
    print(f"Fiches uniques       : {len(merged)}")
    print(f"Avec un vrai avis    : {n_avec_avis}")
    print(f"A completer (tel manquant) : {n_a_completer}")
    print(f"Fichier ecrit        : {args.out}")


if __name__ == "__main__":
    main()
