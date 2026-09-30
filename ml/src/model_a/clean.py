"""
Modèle A (estimation prix véhicule) — étape A.2 : nettoyage du dataset MUCars-2024.

Entrée  : ml/data/raw/mucars_2024.csv          (voir ml/data/README.md pour le téléchargement)
Sorties : ml/data/processed/mucars_clean.parquet
          ml/reports/model_a_cleaning.json      (nombre de lignes retirées à chaque règle)

Le nettoyage ne fait que corriger / écarter des données fausses. Tout ce qui s'apprend
sur les données (regroupement des modèles rares, encodage des catégories...) est fait
plus tard, dans le pipeline d'entraînement, sur le seul jeu d'entraînement — sinon fuite
d'information du jeu de test vers le modèle.

Usage : ml/venv/Scripts/python ml/src/model_a/clean.py
"""

import ast
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ML_DIR = Path(__file__).resolve().parents[2]
RAW_PATH = ML_DIR / "data" / "raw" / "mucars_2024.csv"
OUT_PATH = ML_DIR / "data" / "processed" / "mucars_clean.parquet"
REPORT_PATH = ML_DIR / "reports" / "model_a_cleaning.json"

ANNEE_COLLECTE = 2024  # annonces collectées en 2024 : l'âge du véhicule se calcule par rapport à cette année

# Bornes métier : en dessous de 15 000 DH ce sont des épaves, acomptes ou prix mensuels ;
# au-dessus de 1,5 M DH des fautes de frappe (zéros en trop) — les rares supercars réelles
# au-delà sont trop peu nombreuses pour être apprises de toute façon.
PRIX_MIN, PRIX_MAX = 15_000, 1_500_000

KM_AN_MIN = 3_000  # en dessous (véhicule de 3 ans ou plus), le kilométrage déclaré n'est pas crédible

# Écart maximal (en MAD robuste, sur le log du prix) au prix médian d'un même
# marque + modèle + tranche d'âge avant qu'une annonce soit jugée aberrante.
SEUIL_MAD = 3.5
MIN_GROUPE_MAD = 10  # en dessous, la médiane du groupe n'est pas fiable : on ne filtre pas
# Plancher de la dispersion : la dispersion typique d'un groupe est ~0.15 (log) ; avec 0.2,
# une annonce n'est écartée que si son prix est > ~2x ou < ~0.5x la médiane de son groupe
# (exp(3.5 * 0.2) ≈ 2.0). Un plancher plus bas (0.05) rejetait des prix plausibles.
PLANCHER_DISPERSION = 0.2

VILLES_AR = {
    "الدار البيضاء": "Casablanca",
    "طنجة": "Tanger",
    "الرباط": "Rabat",
    "فاس": "Fès",
    "مراكش": "Marrakech",
    "أكادير": "Agadir",
    "تطوان": "Tétouan",
    "مكناس": "Meknès",
    "تمارة": "Temara",
    "المحمدية": "Mohammedia",
    "الجديدة": "El Jadida",
    "القنيطرة": "Kénitra",
    "الناظور": "Nador",
    "وجدة": "Oujda",
}

CARBURANTS = {"Diesel": "diesel", "Petrol": "essence", "Hybrid": "hybride", "Electrique": "electrique", "LPG": "gpl"}
ETATS = {"New": "neuf", "Excellent": "excellent", "Very Good": "tres_bon", "Good": "bon", "Fair": "correct"}
ORIGINES = {
    "WW in Morocco": "ww_maroc",
    "Customs-cleared car": "dedouanee",
    "Imported New": "importee_neuve",
    "Car not yet customs-cleared": "non_dedouanee",
}

EQUIPEMENTS = {
    "Electric Windows": "eq_vitres_electriques",
    "CD/MP3/Bluetooth": "eq_bluetooth",
    "Alloy Wheels": "eq_jantes_alu",
    "Air Conditioning": "eq_climatisation",
    "Airbags": "eq_airbags",
    "Central Locking": "eq_verrouillage_central",
    "Rear Camera": "eq_camera_recul",
    "ABS": "eq_abs",
    "Leather Seats": "eq_sieges_cuir",
    "Speed Limiter": "eq_limiteur_vitesse",
    "Cruise Control": "eq_regulateur_vitesse",
    "Parking Sensors": "eq_radar_recul",
    "Onboard Computer": "eq_ordinateur_bord",
    "ESP": "eq_esp",
    "Navigation System/GPS": "eq_gps",
    "Sunroof": "eq_toit_ouvrant",
}


def kilometrage_milieu(tranche) -> float:
    """'200 000 - 249 999' -> 225 000 (milieu de tranche) ; 'Plus de 500 000' -> 550 000."""
    if not isinstance(tranche, str):
        return np.nan
    nombres = [int(n.replace(" ", "")) for n in re.findall(r"\d[\d ]*\d|\d", tranche)]
    if tranche.startswith("Plus de"):
        return nombres[0] * 1.1
    if len(nombres) != 2:
        return np.nan
    return (nombres[0] + nombres[1] + 1) / 2


def lire_equipements(valeur) -> list:
    try:
        return ast.literal_eval(valeur)
    except (ValueError, SyntaxError):
        return []


def filtre_mad(df: pd.DataFrame) -> pd.Series:
    """True pour les annonces dont le prix est cohérent avec les annonces comparables."""
    tranche_age = pd.cut(df["age"], bins=[-1, 3, 6, 10, 15, 100])
    groupes = df.groupby(["marque", "modele", tranche_age], observed=True)["prix"]
    log_prix = np.log(df["prix"])
    mediane = groupes.transform(lambda s: np.log(s).median())
    mad = groupes.transform(lambda s: (np.log(s) - np.log(s).median()).abs().median())
    taille = groupes.transform("size")
    # MAD * 1.4826 ≈ écart-type pour une loi normale
    score = (log_prix - mediane).abs() / np.maximum(mad * 1.4826, PLANCHER_DISPERSION)
    return (taille < MIN_GROUPE_MAD) | (score <= SEUIL_MAD)


def nettoyer(brut: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    etapes = []

    def garder(df, masque, regle):
        retirees = int((~masque).sum())
        etapes.append({"regle": regle, "lignes_retirees": retirees, "lignes_restantes": int(masque.sum())})
        return df[masque].copy()

    df = brut.copy()
    etapes.append({"regle": "dataset brut", "lignes_retirees": 0, "lignes_restantes": len(df)})

    df = garder(df, ~df.duplicated(), "doublons exacts")
    df = garder(df, df["Price"].notna(), "prix manquant")
    df = garder(df, df["Brand"].notna() & df["Model"].notna(), "marque ou modèle manquant")
    # Quelques marques sont des nombres ("112", "99"...) : colonnes décalées au scraping
    df = garder(df, ~df["Brand"].astype(str).str.fullmatch(r"\d+"), "marque invalide (numérique)")
    # Un véhicule accidenté ou vendu pour pièces n'a pas une valeur de marché comparable
    df = garder(df, ~df["Condition"].isin(["Damaged", "For Parts"]), "véhicule accidenté / pour pièces")
    df = garder(df, df["Fuel"].isin(CARBURANTS.keys()), "carburant invalide")
    df = garder(df, df["Price"].between(PRIX_MIN, PRIX_MAX), f"prix hors [{PRIX_MIN:,} ; {PRIX_MAX:,}] DH")

    propre = pd.DataFrame(index=df.index)
    propre["marque"] = df["Brand"].str.strip().str.lower()
    propre["modele"] = df["Model"].str.strip().str.lower().str.replace(r"\s+", " ", regex=True)
    propre["annee"] = df["Year"].replace("1980 ou plus ancien", "1980").astype(int)
    propre["age"] = ANNEE_COLLECTE - propre["annee"]
    propre["kilometrage"] = df["Mileage"].map(kilometrage_milieu)
    # Kilométrage invraisemblable : moins de KM_AN_MIN km/an pour une voiture de 3 ans ou plus
    # (la moyenne au Maroc est ~15 000 km/an). Cas typiques : "0 - 4 999", valeur par défaut du
    # formulaire, ou un zéro oublié (150 000 saisi 15 000). Le prix reste exploitable : on garde
    # l'annonce avec un kilométrage "inconnu" plutôt que de la supprimer.
    km_par_an = propre["kilometrage"] / propre["age"].clip(lower=1)
    km_invraisemblable = (km_par_an < KM_AN_MIN) & (propre["age"] >= 3)
    propre["km_inconnu"] = km_invraisemblable | propre["kilometrage"].isna()
    propre.loc[propre["km_inconnu"], "kilometrage"] = np.nan
    propre["boite"] = df["Gearbox"].map({"Manual": "manuelle", "Automatic": "automatique"})
    propre["puissance_fiscale"] = pd.to_numeric(df["Fiscal Power"].str.extract(r"(\d+)")[0], errors="coerce")
    propre["carburant"] = df["Fuel"].map(CARBURANTS)
    propre["etat"] = df["Condition"].map(ETATS).fillna("inconnu")
    propre["nb_portes"] = df["Number of Doors"]
    propre["origine"] = df["Origin"].map(ORIGINES).fillna("inconnu")
    propre["premiere_main"] = df["First Owner"].map({"Yes": "oui", "No": "non"}).fillna("inconnu")
    propre["ville"] = df["Location"].str.strip().replace(VILLES_AR)
    propre["secteur"] = df["Sector"].str.strip()

    equipements = df["Equipment"].map(lire_equipements)
    propre["nb_equipements"] = equipements.map(len)
    for libelle, colonne in EQUIPEMENTS.items():
        propre[colonne] = equipements.map(lambda liste, l=libelle: l in liste)

    propre["prix"] = df["Price"].astype(int)

    # Un véhicule "neuf" avec plus de 50 000 km est une erreur de saisie de l'un des deux champs
    propre = garder(
        propre,
        ~((propre["etat"] == "neuf") & (propre["kilometrage"] > 50_000)),
        "incohérence état neuf / kilométrage > 50 000 km",
    )
    propre = garder(propre, filtre_mad(propre), f"prix aberrant vs annonces comparables (> {SEUIL_MAD} MAD)")
    # Doublons après normalisation (même annonce republiée avec une casse ou des espaces différents)
    propre = garder(propre, ~propre.duplicated(), "doublons après normalisation")

    return propre.reset_index(drop=True), etapes


def main():
    brut = pd.read_csv(RAW_PATH)
    propre, etapes = nettoyer(brut)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    propre.to_parquet(OUT_PATH, index=False)

    rapport = {
        "source": "MUCars-2024 (DOI 10.17632/vjrbcb2rrt.2, CC BY 4.0)",
        "lignes_brutes": len(brut),
        "lignes_finales": len(propre),
        "taux_conservation": round(len(propre) / len(brut), 4),
        "etapes": etapes,
        "valeurs_manquantes_finales": {c: int(n) for c, n in propre.isna().sum().items() if n},
        "prix": {k: float(v) for k, v in propre["prix"].describe().round(0).items()},
    }
    REPORT_PATH.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")

    largeur = max(len(e["regle"]) for e in etapes)
    for e in etapes:
        print(f"{e['regle']:<{largeur}}  -{e['lignes_retirees']:>6}  -> {e['lignes_restantes']:>7}")
    print(f"\n{len(propre)} annonces propres ({rapport['taux_conservation']:.1%}) -> {OUT_PATH.relative_to(ML_DIR.parent)}")


if __name__ == "__main__":
    main()
