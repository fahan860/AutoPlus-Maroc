"""
Modèle B (recommandation de garages) — étape B.1 : enrichissement de la table garages.

Lit les fiches collectées par fetch_fiches_telecontact.py et met à jour la base :
  1. Coordonnées GPS : pour les garages sans position, celle publiée sur leur fiche.
  2. Spécialités (migration 007) : mots-clés cherchés dans la description de la fiche
     (si elle est spécifique au garage) et dans le nom. Sans aucune indication, le garage
     est supposé de mécanique générale (sa catégorie officielle est « mécanique,
     réparation ») ; la source est notée pour vérifier ces hypothèses sur le terrain.

Idempotent : relançable sans risque. Ne remplace jamais des spécialités saisies par le
garage lui-même (source "declaree").

Usage : ml/venv/Scripts/python data/scraping/enrich_garages.py
Nécessite DATABASE_URL dans api/.env et la migration 007 appliquée.
"""

import csv
import os
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
load_dotenv(ROOT / "api" / ".env")

FICHES = HERE / "garages_fiches_telecontact.csv"

# Mêmes valeurs que base_pannes.categorie. Mots-clés sans accents, en minuscules,
# cherchés comme début de mot ("frein" trouve "freinage", "pot" ne trouve pas "depot").
MOTS_CLES = {
    "moteur": ["moteur", "injection", "diesel", "turbo", "culasse", "rectification"],
    "entretien_courant": ["entretien", "vidange", "revision"],
    "freins": ["frein", "plaquette"],
    "electrique": ["electri", "electro", "electronique", "diag", "batterie", "alternateur", "demarreur"],
    "climatisation": ["climatisation", "clim"],
    "carrosserie": ["carrosserie", "tolerie", "tol", "peinture", "debosselage", "pare-brise", "vitrage"],
    "pneus_suspension": ["pneu", "pneumatique", "amortisseur", "suspension", "equilibrage", "geometrie", "jante"],
    "transmission": ["boite de vitesse", "embrayage", "transmission", "cardan"],
    "direction": ["direction", "cremaillere", "parallelisme"],
    "echappement": ["echappement", "pot", "silencieux", "catalyseur"],
}

# Hypothèse « mécanique générale » : ce que fait un garage de mécanique classique,
# sans les métiers qui demandent un équipement spécifique (carrosserie, climatisation,
# électricité/diagnostic électronique).
GENERALISTE = ["moteur", "entretien_courant", "freins", "transmission", "direction", "echappement"]

DESCRIPTION_GENERIQUE = "active dans le secteur"  # texte produit par le site, pas par le garage


def normaliser(texte: str) -> str:
    sans_accents = unicodedata.normalize("NFKD", texte or "").encode("ascii", "ignore").decode()
    return " ".join(sans_accents.lower().split())


def specialites_du_texte(texte: str) -> list[str]:
    texte = normaliser(texte)
    trouvees = {
        specialite for specialite, mots in MOTS_CLES.items()
        if any(re.search(rf"\b{re.escape(mot)}", texte) for mot in mots)
    }
    if re.search(r"\bmecanique", texte):  # "mécanique" = mécanique générale, pas seulement le moteur
        trouvees.update(GENERALISTE)
    return sorted(trouvees)


def lire_fiches() -> dict:
    with FICHES.open(encoding="utf-8-sig", newline="") as f:
        return {l["lien_fiche"]: l for l in csv.DictReader(f, delimiter=";") if l["statut_http"] == "200"}


def main():
    url_base = os.environ.get("DATABASE_URL")
    if not url_base:
        sys.exit("DATABASE_URL introuvable (attendu dans api/.env)")
    fiches = lire_fiches()

    with psycopg2.connect(url_base) as conn, conn.cursor() as cur:
        cur.execute("SELECT id, nom, lien_fiche, geom IS NOT NULL, specialites_source FROM garages ORDER BY id")
        garages = cur.fetchall()

        gps_ajoutes, sources = 0, Counter()
        for garage_id, nom, lien, a_gps, source_actuelle in garages:
            fiche = fiches.get(lien or "", {})

            if not a_gps and fiche.get("latitude") and fiche.get("longitude"):
                cur.execute(
                    "UPDATE garages SET geom = ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography, updated_at = now() "
                    "WHERE id = %s",
                    (float(fiche["longitude"]), float(fiche["latitude"]), garage_id),
                )
                gps_ajoutes += 1

            if source_actuelle == "declaree":
                sources["declaree"] += 1
                continue
            description = fiche.get("description", "")
            if description and DESCRIPTION_GENERIQUE not in description:
                specialites, source = specialites_du_texte(f"{description} {nom}"), "fiche_telecontact"
            else:
                specialites, source = specialites_du_texte(nom), "nom"
            if not specialites:
                specialites, source = GENERALISTE, "hypothese_generaliste"

            cur.execute(
                "UPDATE garages SET specialites = %s, specialites_source = %s, updated_at = now() WHERE id = %s",
                (specialites, source, garage_id),
            )
            sources[source] += 1

        cur.execute("SELECT count(*), count(geom) FROM garages")
        total, avec_gps = cur.fetchone()
        cur.execute("SELECT unnest(specialites), count(*) FROM garages GROUP BY 1 ORDER BY 2 DESC")
        repartition = cur.fetchall()

    print(f"GPS : {gps_ajoutes} positions ajoutées -> {avec_gps}/{total} garages géolocalisés")
    print("Source des spécialités :", dict(sources))
    print("Garages par spécialité :", ", ".join(f"{s} {n}" for s, n in repartition))


if __name__ == "__main__":
    main()
