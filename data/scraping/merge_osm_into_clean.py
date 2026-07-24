"""
Fusionne les garages OpenStreetMap (data/garages_osm.csv, scrapes via Overpass
par scrape_garages_osm.py) dans le CSV nettoye telecontact.ma (garages_clean.csv),
en excluant les doublons (meme etablissement present dans les deux sources).

Dedup : comparaison de noms normalises (accents/casse/ponctuation ignores),
match si l'un est inclus dans l'autre. Les points OSM sans nom (frequents sur
un POI pose sans tag "name") sont ignores : un garage sans nom n'est pas
exploitable dans un annuaire.

Colonnes ajoutees par rapport a garages_clean.csv : lat, lon (vides pour les
lignes telecontact.ma, remplies pour les lignes OSM -> permettent de peupler
la colonne geom en base sans geocoding).

Usage (depuis data/scraping/) :
    python merge_osm_into_clean.py
"""

import csv
import os
import re
import unicodedata

SCRAPING_DIR = os.path.dirname(os.path.abspath(__file__))
CLEAN_PATH = os.path.join(SCRAPING_DIR, "garages_clean.csv")
OSM_PATH = os.path.join(os.path.dirname(SCRAPING_DIR), "garages_osm.csv")

FIELDNAMES = [
    "nom", "categorie", "adresse", "ville", "telephone",
    "note", "nb_avis", "lien_fiche", "source", "a_completer", "lat", "lon",
]

OSM_CATEGORIE = "Garage automobile / Mécanique"


def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def normalize_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def normalize_phone(raw: str) -> str:
    """Meme regle que merge_and_clean_garages.py : '0X XX XX XX XX' ou vide.
    Les numeros OSM sont souvent en format international (+212 6 ..)."""
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("212"):
        digits = "0" + digits[3:]
    if len(digits) != 10 or not digits.startswith("0"):
        return ""
    return " ".join([digits[0:2], digits[2:4], digits[4:6], digits[6:8], digits[8:10]])


def load_clean(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def load_osm(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def merge():
    clean_rows = load_clean(CLEAN_PATH)
    osm_rows = load_osm(OSM_PATH)

    for row in clean_rows:
        row.setdefault("lat", "")
        row.setdefault("lon", "")

    known_names = {normalize_name(r["nom"]) for r in clean_rows if r.get("nom")}

    added, skipped_noname, skipped_dupe = 0, 0, 0
    for r in osm_rows:
        nom = normalize_space(r.get("nom", ""))
        if not nom:
            skipped_noname += 1
            continue

        n = normalize_name(nom)
        if any(n in kn or kn in n for kn in known_names):
            skipped_dupe += 1
            continue

        telephone = normalize_phone(r.get("telephone", ""))
        clean_rows.append({
            "nom": nom,
            "categorie": OSM_CATEGORIE,
            "adresse": normalize_space(r.get("adresse", "")),
            "ville": r.get("ville", "") or "Casablanca",
            "telephone": telephone,
            "note": "",
            "nb_avis": "0",
            "lien_fiche": f"https://www.openstreetmap.org/{r['osm_type']}/{r['osm_id']}",
            "source": "openstreetmap",
            "a_completer": "true" if not telephone else "false",
            "lat": r.get("lat", ""),
            "lon": r.get("lon", ""),
        })
        known_names.add(n)
        added += 1

    with open(CLEAN_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES, delimiter=";")
        writer.writeheader()
        writer.writerows(clean_rows)

    print(f"OSM lus              : {len(osm_rows)}")
    print(f"Sans nom (ignores)   : {skipped_noname}")
    print(f"Doublons (ignores)   : {skipped_dupe}")
    print(f"Ajoutes              : {added}")
    print(f"Total garages_clean.csv : {len(clean_rows)}")


if __name__ == "__main__":
    merge()
