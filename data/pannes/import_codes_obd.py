"""
Semaine 4 du stage — telecharge et importe les codes OBD-II (DTC) depuis
mytrile/obd-trouble-codes (licence MIT, ~3071 codes), categorise
categorie_probable par mots-cles, upsert dans codes_obd. A executer apres
codes_obd_schema.sql (et apres schema.sql, pour la FK panne_code_lie).

Usage : python data/pannes/import_codes_obd.py
Necessite DATABASE_URL dans l'environnement (voir api/.env).
"""

import csv
import io
import os
import re
import sys
from pathlib import Path

import truststore

truststore.inject_into_ssl()  # utilise le magasin de certificats Windows (contourne
# l'interception TLS d'Avast, cf. ml/README.md) au lieu du bundle certifi statique.

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

load_dotenv(ROOT / "api" / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print(
        "DATABASE_URL introuvable (attendu dans api/.env). "
        "Je ne devine jamais des identifiants : merci de le renseigner puis relancer.",
        file=sys.stderr,
    )
    sys.exit(1)

CSV_URL_RAW = "https://raw.githubusercontent.com/mytrile/obd-trouble-codes/master/obd-trouble-codes.csv"
# Repli : raw.githubusercontent.com est regulierement throttle (429/503) depuis
# les environnements sandbox a IP de sortie partagee, contrairement a
# api.github.com (Contents API) qui sert le meme fichier sans ce throttling.
CSV_URL_API_FALLBACK = "https://api.github.com/repos/mytrile/obd-trouble-codes/contents/obd-trouble-codes.csv"
EXPECTED_ROWS_APPROX = 3071

# Ordre = priorite en cas de description qui matche plusieurs categories.
KEYWORD_MAP = [
    ("freins", ["brake"]),
    ("climatisation", ["climate", "hvac"]),
    ("echappement", ["emission", "catalyst", "egr"]),
    ("transmission", ["transmission", "gear", "clutch"]),
    ("direction", ["steering"]),
    ("pneus_suspension", ["wheel speed", "suspension", "tire"]),
    ("electrique", ["battery", "alternator", "network"]),
    ("moteur", ["engine", "fuel", "ignition"]),
]

CODE_PATTERN = re.compile(r"^[PBCU]\d{4}$", re.IGNORECASE)


def categorize(description: str) -> str | None:
    desc_lower = description.lower()
    for categorie, keywords in KEYWORD_MAP:
        if any(kw in desc_lower for kw in keywords):
            return categorie
    return None


def fetch_csv_text() -> str:
    import requests

    try:
        resp = requests.get(CSV_URL_RAW, timeout=15)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as err:
        print(f"raw.githubusercontent.com indisponible ({err}), repli sur l'API GitHub...", file=sys.stderr)
        resp = requests.get(
            CSV_URL_API_FALLBACK,
            headers={"Accept": "application/vnd.github.raw"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.text


def parse_rows(csv_text: str):
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)
    if not rows:
        raise ValueError("CSV vide")

    header = [h.strip().lower() for h in rows[0]]
    data_rows = rows[1:]

    # Detection souple des colonnes code/description : par nom si possible,
    # sinon on suppose "code" en premiere colonne et "description" en
    # deuxieme (format le plus courant pour ce type de fichier).
    code_idx = next((i for i, h in enumerate(header) if "code" in h), None)
    desc_idx = next((i for i, h in enumerate(header) if "desc" in h), None)

    if code_idx is None or desc_idx is None:
        if len(header) >= 2 and CODE_PATTERN.match(header[0].upper()):
            # Pas de vraie ligne d'entete : la "premiere ligne" est deja une donnee.
            data_rows = rows
            code_idx, desc_idx = 0, 1
        else:
            code_idx, desc_idx = 0, 1

    parsed = []
    for row in data_rows:
        if len(row) <= max(code_idx, desc_idx):
            continue
        code = row[code_idx].strip().upper()
        description = row[desc_idx].strip()
        if not code or not description:
            continue
        parsed.append((code, description))
    return parsed


def main():
    import psycopg2

    print(f"Telechargement de {CSV_URL_RAW} ...")
    csv_text = fetch_csv_text()

    rows = parse_rows(csv_text)
    print(f"{len(rows)} lignes parsees.")

    if abs(len(rows) - EXPECTED_ROWS_APPROX) > EXPECTED_ROWS_APPROX * 0.1:
        print(
            f"ATTENTION : {len(rows)} lignes trouvees, attendu ~{EXPECTED_ROWS_APPROX}. "
            "Le format du CSV source a peut-etre change. Verification manuelle recommandee "
            "avant d'utiliser ces donnees.",
            file=sys.stderr,
        )

    invalid = [code for code, _ in rows if not CODE_PATTERN.match(code)]
    if invalid:
        print(
            f"ATTENTION : {len(invalid)} code(s) ne matchent pas le format DTC standard "
            f"(ex: {invalid[:5]}). Ils seront ignores.",
            file=sys.stderr,
        )
        rows = [(c, d) for c, d in rows if CODE_PATTERN.match(c)]

    categorized_count = 0
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            for code, description in rows:
                famille = code[0].upper()
                categorie_probable = categorize(description)
                if categorie_probable:
                    categorized_count += 1
                cur.execute(
                    """
                    INSERT INTO codes_obd (code, description_en, famille, categorie_probable)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (code) DO UPDATE SET
                        description_en = EXCLUDED.description_en,
                        famille = EXCLUDED.famille,
                        categorie_probable = EXCLUDED.categorie_probable
                    """,
                    (code, description, famille, categorie_probable),
                )
        conn.commit()
        print(f"{len(rows)} codes OBD upsertes ({categorized_count} categorises automatiquement).")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
