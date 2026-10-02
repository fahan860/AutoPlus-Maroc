"""
Modèle B (recommandation de garages) — étape B.1 : collecte des fiches Telecontact.

Pour chaque garage de source telecontact.ma en base, télécharge sa fiche publique
(/annonceur/..., autorisé par le robots.txt du site) et en extrait :
  - les mots-clés « produits / services » (ex : Mécanique, Pneumatique, Carrosserie)
  - la description libre (ex : « Mécanique, électricité, climatisation... »)
  - la rubrique principale
  - les coordonnées GPS et la note publiées dans les données structurées (JSON-LD)

Rien n'est écrit en base ici : le résultat brut va dans garages_fiches_telecontact.csv,
qui sert aussi de cache (une fiche déjà récupérée n'est jamais retéléchargée).
L'interprétation (spécialités, mise à jour de la table garages) est faite par
enrich_garages.py.

Volontairement lent (DELAI_S entre deux requêtes) pour rester respectueux du site.

Usage : ml/venv/Scripts/python data/scraping/fetch_fiches_telecontact.py
Nécessite DATABASE_URL dans api/.env.
"""

import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import truststore

truststore.inject_into_ssl()  # magasin de certificats Windows (contourne l'interception TLS d'Avast)

import psycopg2
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
load_dotenv(ROOT / "api" / ".env")

SORTIE = HERE / "garages_fiches_telecontact.csv"
DELAI_S = 3
USER_AGENT = "Mozilla/5.0 (compatible; AutoPlus-PFA/1.0; projet etudiant, collecte lente)"
COLONNES = ["lien_fiche", "statut_http", "rubrique", "mots_cles", "description",
            "latitude", "longitude", "note", "nb_avis", "recupere_le"]


def lire_cache() -> dict:
    if not SORTIE.exists():
        return {}
    with SORTIE.open(encoding="utf-8-sig", newline="") as f:
        return {ligne["lien_fiche"]: ligne for ligne in csv.DictReader(f, delimiter=";")}


def ecrire(lignes: dict) -> None:
    with SORTIE.open("w", encoding="utf-8-sig", newline="") as f:  # BOM : lisible par Excel FR
        ecrivain = csv.DictWriter(f, fieldnames=COLONNES, delimiter=";")
        ecrivain.writeheader()
        ecrivain.writerows(lignes.values())


def extraire(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")

    # Mots-clés : liens suivis par l'événement analytics "Page_Annonceur_mots-cles"
    mots_cles = []
    for li in soup.find_all("li", onclick=re.compile("Page_Annonceur_mots-cles")):
        texte = li.get_text(" ", strip=True)
        if texte and texte not in mots_cles:
            mots_cles.append(texte)

    description = soup.find(attrs={"itemprop": "description"})
    description = description.get_text(" ", strip=True) if description else ""

    infos = {"latitude": "", "longitude": "", "note": "", "nb_avis": "", "rubrique": ""}
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            donnees = json.loads(script.string or "")
        except json.JSONDecodeError:
            continue
        for bloc in donnees if isinstance(donnees, list) else [donnees]:
            if not isinstance(bloc, dict):
                continue
            geo = bloc.get("geo") or {}
            if geo.get("latitude") and geo.get("longitude"):
                infos["latitude"], infos["longitude"] = geo["latitude"], geo["longitude"]
            note = bloc.get("aggregateRating") or {}
            if note.get("ratingValue"):
                infos["note"], infos["nb_avis"] = note["ratingValue"], note.get("reviewCount", "")

    # Rubrique principale : premier lien d'activité (/liens/...) qui n'est pas un mot-clé
    # (ex : "Garages d'automobiles (mécanique, réparation)")
    for lien in soup.find_all("a", href=re.compile(r"^/liens/")):
        parent = lien.find_parent("li")
        if parent is None or "Page_Annonceur_mots-cles" not in (parent.get("onclick") or ""):
            infos["rubrique"] = lien.get_text(" ", strip=True)
            break

    return {"mots_cles": " | ".join(mots_cles), "description": description, **infos}


def main():
    url_base = os.environ.get("DATABASE_URL")
    if not url_base:
        sys.exit("DATABASE_URL introuvable (attendu dans api/.env)")
    with psycopg2.connect(url_base) as conn, conn.cursor() as cur:
        cur.execute("SELECT lien_fiche FROM garages WHERE source = 'telecontact.ma' AND lien_fiche IS NOT NULL ORDER BY id")
        liens = [r[0] for r in cur.fetchall()]

    cache = lire_cache()
    a_faire = [l for l in liens if cache.get(l, {}).get("statut_http") != "200"]
    print(f"{len(liens)} fiches telecontact, {len(liens) - len(a_faire)} déjà en cache, {len(a_faire)} à récupérer "
          f"(~{len(a_faire) * DELAI_S // 60 + 1} min)")

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    for i, lien in enumerate(a_faire, 1):
        try:
            reponse = session.get(lien, timeout=20)
            ligne = {"lien_fiche": lien, "statut_http": str(reponse.status_code)}
            if reponse.ok:
                ligne.update(extraire(reponse.text))
        except requests.RequestException as err:
            ligne = {"lien_fiche": lien, "statut_http": f"erreur: {type(err).__name__}"}
        ligne["recupere_le"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cache[lien] = ligne
        ecrire(cache)  # sauvegarde à chaque fiche : une interruption ne fait rien perdre
        print(f"[{i}/{len(a_faire)}] {ligne['statut_http']} {ligne.get('mots_cles', '')[:60]}", flush=True)
        time.sleep(DELAI_S)

    ok = sum(1 for l in cache.values() if l.get("statut_http") == "200")
    print(f"\nTerminé : {ok}/{len(liens)} fiches récupérées -> {SORTIE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
