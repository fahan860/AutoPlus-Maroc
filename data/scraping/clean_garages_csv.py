"""
Nettoyage du CSV brut de garages scrapes (telecontact.ma) avant import en base.

Regles appliquees :
  - trim + collapse des espaces multiples sur nom / adresse
  - normalisation du telephone au format marocain local "0X XX XX XX XX"
    (garde le format local, valide que c'est bien 10 chiffres commencant par 0)
  - telephone invalide/absent -> champ vide + colonne a_completer = true
  - note/nb_avis a 0/0 (= pas de vrai avis, valeur par defaut du site source)
    -> note mise a vide plutot que "0" pour ne pas laisser croire a une vraie
       note de 0/5
  - lien_fiche = cle de dedup (garde la 1ere occurrence si jamais un doublon
    strict apparait ; les etablissements de meme nom a des adresses
    differentes -- franchises/succursales -- sont conserves tels quels)
  - ajoute une colonne source='telecontact.ma'

Usage :
    python clean_garages_csv.py garages_casablanca_telecontact.csv garages_casablanca_clean.csv
"""

import csv
import re
import sys


def normalize_space(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def normalize_phone(raw: str) -> str:
    """Retourne le tel au format '0X XX XX XX XX' si valide, sinon ''."""
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    if len(digits) != 10 or not digits.startswith("0"):
        return ""
    return " ".join([digits[0:2], digits[2:4], digits[4:6], digits[6:8], digits[8:10]])


def clean_row(row: dict) -> dict:
    nom = normalize_space(row.get("nom", ""))
    adresse = normalize_space(row.get("adresse", ""))
    ville = normalize_space(row.get("ville", "")) or "Casablanca"
    categorie = normalize_space(row.get("categorie", ""))
    lien_fiche = normalize_space(row.get("lien_fiche", ""))

    telephone = normalize_phone(row.get("telephone", ""))

    try:
        note_val = float(row.get("note", 0) or 0)
    except ValueError:
        note_val = 0.0
    try:
        nb_avis_val = int(row.get("nb_avis", 0) or 0)
    except ValueError:
        nb_avis_val = 0

    # 0/0 = pas de vrai avis sur le site source -> on vide plutot que d'afficher "0"
    note = "" if nb_avis_val == 0 else str(note_val)

    a_completer = "true" if not telephone else "false"

    return {
        "nom": nom,
        "categorie": categorie,
        "adresse": adresse,
        "ville": ville,
        "telephone": telephone,
        "note": note,
        "nb_avis": str(nb_avis_val),
        "lien_fiche": lien_fiche,
        "source": "telecontact.ma",
        "a_completer": a_completer,
    }


def main():
    if len(sys.argv) < 3:
        print("Usage: python clean_garages_csv.py <in.csv> <out.csv>")
        sys.exit(1)

    in_path, out_path = sys.argv[1], sys.argv[2]

    with open(in_path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    seen_liens = set()
    cleaned = []
    dropped_dupes = 0

    for row in rows:
        cleaned_row = clean_row(row)
        key = cleaned_row["lien_fiche"]
        if key and key in seen_liens:
            dropped_dupes += 1
            continue
        seen_liens.add(key)
        cleaned.append(cleaned_row)

    fieldnames = ["nom", "categorie", "adresse", "ville", "telephone", "note",
                  "nb_avis", "lien_fiche", "source", "a_completer"]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned)

    n_a_completer = sum(1 for r in cleaned if r["a_completer"] == "true")

    print(f"Lignes lues        : {len(rows)}")
    print(f"Doublons stricts    : {dropped_dupes} (memes lien_fiche, supprimes)")
    print(f"Lignes ecrites      : {len(cleaned)}")
    print(f"A completer (tel manquant) : {n_a_completer}")
    print(f"Fichier : {out_path}")


if __name__ == "__main__":
    main()
