"""
Scraper de garages / ateliers / mecaniciens au Maroc via telecontact.ma
(annuaire "Pages Jaunes du Maroc", donnees professionnelles publiques,
consultables sans compte).

A LANCER SUR TA MACHINE (pas dans le sandbox Cowork) car il faut un acces
internet reel. Cowork n'a pas d'acces internet direct en shell, uniquement
via ses propres outils de fetch - ce script est fait pour tourner chez toi.

Installation :
    pip install requests beautifulsoup4

Usage :
    python scraper_garages_telecontact.py --ville casablanca --categorie garage-automobile --pages 20 --out garages_casablanca.csv

Notes :
- Categories utiles pour la vitrine AUTO+ : garage-automobile,
  garages-d-automobiles-mecanique-reparation, carrosserie, pneumatique,
  auto-ecole (a exclure), pieces-detachees-automobiles, etc.
  Regarde l'URL de la categorie sur https://www.telecontact.ma quand tu
  navigues manuellement pour trouver le bon slug.
- Le script est volontairement lent (delai entre requetes) pour rester
  respectueux du site source et eviter d'etre bloque (rate limiting).
- Les champs manquants (telephone absent, note absente) sont laisses vides,
  jamais inventes.
- Pense a dedupliquer par lien_fiche (URL) si tu combines plusieurs
  categories qui se recoupent (beaucoup de garages apparaissent dans
  plusieurs categories proches).
"""

import argparse
import csv
import re
import time
import sys
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://www.telecontact.ma"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}
DELAY_SECONDS = 1.5  # pause entre chaque requete HTTP, a ne pas descendre trop bas


def listing_url(categorie: str, ville: str, page: int) -> str:
    base_url = f"{BASE}/liens/{categorie}/{ville}.php"
    if page <= 1:
        return base_url
    return f"{base_url}&page={page}&page={page}"


def fetch(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        # telecontact.ma sert du UTF-8, mais requests devine parfois mal
        # l'encodage a partir des en-tetes HTTP et retombe sur ISO-8859-1,
        # ce qui casse tous les caracteres accentues (mojibake). On force
        # explicitement l'encodage plutot que de laisser requests deviner.
        r.encoding = "utf-8"
        return BeautifulSoup(r.text, "html.parser")
    except requests.RequestException as e:
        print(f"  [!] Erreur sur {url} : {e}", file=sys.stderr)
        return None


def _find_adresse(lines):
    """Heuristique commune pour extraire l'adresse a partir d'une liste de lignes
    de texte deja nettoyees (une string par noeud de texte du DOM).

    Sur telecontact.ma, la ville ("Casablanca - Maroc") est souvent dans un tag
    <strong> separe de la rue, ce qui cree DEUX lignes distinctes une fois le
    HTML applati en texte (ex: "36 rue Beni Amar Hay mohammadi" puis
    "Casablanca - Maroc"). On cherche donc la ligne "<Ville> - Maroc" et on
    prend la ligne juste avant comme adresse. Si ce motif n'est pas trouve,
    on retombe sur l'ancienne heuristique (une seule ligne qui se termine par
    "Maroc").
    """
    for i, line in enumerate(lines):
        if i > 0 and re.search(r"-\s*Maroc\s*$", line):
            candidate = lines[i - 1]
            if len(candidate) > 8 and not candidate.lower().startswith(("accueil", "recherche", "trouver")):
                return candidate

    for line in lines:
        if re.search(r"Maroc\s*$", line) and len(line) > 15:
            return line

    return ""


def _find_note_avis(text):
    """Cherche un motif 'X.X ... (N avis)' (present sur les fiches detail dans
    le bloc Evaluations) ou 'note Avis' (present sur les pages de listing).
    Retourne (note, nb_avis) en chaines, vides si rien trouve."""
    m = re.search(r"(\d(?:[.,]\d)?)\s*[★☆]{1,5}\s*\(\s*(\d+)\s*avis\)", text, re.IGNORECASE)
    if m:
        return m.group(1).replace(",", "."), m.group(2)

    note_match = re.search(r"★\s*([\d.,]+)", text)
    avis_match = re.search(r"(\d+)\s*Avis", text, re.IGNORECASE)
    if note_match or avis_match:
        note = note_match.group(1).replace(",", ".") if note_match else ""
        nb_avis = avis_match.group(1) if avis_match else "0"
        return note, nb_avis

    return "", "0"


def parse_listing_page(soup):
    """Retourne une liste de dicts partiels (sans telephone confirme) pour une page de listing."""
    results = []
    # Chaque fiche est un <h2><a href="...annonceur...">Nom</a></h2>
    for h2 in soup.select("h2 a[href*='/annonceur/']"):
        name = h2.get_text(strip=True)
        detail_url = urljoin(BASE, h2["href"])

        # Le bloc parent contient la note / avis / adresse juste apres le titre
        block = h2.find_parent()
        block_lines = [l.strip() for l in block.stripped_strings] if block else []
        block_text = " ".join(block_lines)

        note, nb_avis = _find_note_avis(block_text)
        adresse = _find_adresse(block_lines)

        results.append({
            "nom": name,
            "lien_fiche": detail_url,
            "adresse": adresse,
            "note": note,
            "nb_avis": nb_avis,
        })
    return results


def parse_detail_page(soup):
    """Extrait telephone / adresse / note depuis une fiche detail (plus fiable
    que la page de listing car chaque fiche a sa propre page dediee)."""
    text = soup.get_text("\n", strip=True)
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    tel_match = re.search(r"Tel\s*1\s*:\s*([\d\s]{8,})", text)
    telephone = tel_match.group(1).strip() if tel_match else ""

    adresse = _find_adresse(lines)
    note, nb_avis = _find_note_avis(text)

    return {"telephone": telephone, "adresse": adresse, "note": note, "nb_avis": nb_avis}


def scrape(categorie, ville, max_pages, fetch_details):
    all_rows = {}  # cle = lien_fiche pour dedupliquer

    for page in range(1, max_pages + 1):
        url = listing_url(categorie, ville, page)
        print(f"[listing] page {page} -> {url}")
        soup = fetch(url)
        time.sleep(DELAY_SECONDS)
        if soup is None:
            continue

        rows = parse_listing_page(soup)
        if not rows:
            print("  -> aucune fiche trouvee, arret de la pagination.")
            break

        for row in rows:
            row["categorie"] = categorie
            row["ville"] = ville.capitalize()
            all_rows[row["lien_fiche"]] = row

    print(f"\n{len(all_rows)} etablissements uniques trouves sur les listings.\n")

    if fetch_details:
        for i, (url, row) in enumerate(all_rows.items(), start=1):
            print(f"[detail {i}/{len(all_rows)}] {row['nom']}")
            soup = fetch(url)
            time.sleep(DELAY_SECONDS)
            if soup is None:
                continue
            detail = parse_detail_page(soup)
            row["telephone"] = detail["telephone"]
            # on ne remplace l'adresse/note du listing que si la fiche detail
            # a effectivement trouve quelque chose (sinon on garde le fallback
            # deja recupere sur la page de listing)
            if detail["adresse"]:
                row["adresse"] = detail["adresse"]
            if detail["note"]:
                row["note"] = detail["note"]
                row["nb_avis"] = detail["nb_avis"]

    return list(all_rows.values())


def main():
    parser = argparse.ArgumentParser(description="Scraper garages/ateliers telecontact.ma")
    parser.add_argument("--categorie", default="garage-automobile",
                         help="slug de categorie telecontact.ma (ex: garage-automobile, carrosserie, pneumatique)")
    parser.add_argument("--ville", default="casablanca")
    parser.add_argument("--pages", type=int, default=5, help="nombre de pages de listing a parcourir")
    parser.add_argument("--no-details", action="store_true",
                         help="ne pas aller chercher le telephone sur chaque fiche (plus rapide)")
    parser.add_argument("--out", default="garages.csv")
    args = parser.parse_args()

    rows = scrape(args.categorie, args.ville, args.pages, fetch_details=not args.no_details)

    fieldnames = ["nom", "categorie", "adresse", "ville", "telephone", "note", "nb_avis", "lien_fiche"]
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    print(f"\nTermine : {len(rows)} lignes ecrites dans {args.out}")


if __name__ == "__main__":
    main()
