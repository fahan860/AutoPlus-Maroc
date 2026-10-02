"""
Modèle B — étape B.3 : simulation d'interactions utilisateur ↔ garage.

L'app n'a pas encore d'historique de RDV : pour construire et tester le filtrage
collaboratif, on simule des automobilistes qui font réparer leur voiture au fil du temps.
Les DONNÉES SONT SIMULÉES : elles servent à démontrer le mécanisme, pas à mesurer une
performance réelle. Toutes les règles sont ci-dessous, pour être citées dans le rapport.

Règles :
  - Garages : les garages géolocalisés de la base, avec leurs spécialités réelles.
    Chaque garage reçoit deux propriétés CACHÉES (absentes de la base, donc invisibles
    pour le filtrage par contenu) : une qualité de service, et un positionnement
    « premium » (30 % des garages).
  - Automobilistes : domicile autour d'un des 12 quartiers, ±1,5 km ; 30 % « premium ».
  - Interventions : 1 + Poisson(4) par personne ; catégorie tirée selon des fréquences
    réalistes (l'entretien courant domine).
  - Choix du garage (modèle logit) : utilité = - distance / 2,5 km
                                             + log(compétence pour la catégorie)
                                             + 1,0 × qualité cachée
                                             + 0,8 si le profil premium correspond
                                             + 1,0 si déjà satisfait (note ≥ 4) par ce garage
  - Note donnée : 3,4 + 0,7 × qualité + 0,5 si profil correspondant + bruit N(0 ; 0,6),
    arrondie et bornée entre 1 et 5.

Sortie : ml/data/simulated/interactions.parquet (local, non versionné)
Usage  : ml/venv/Scripts/python ml/src/model_b/simulate.py
"""

import numpy as np
import pandas as pd

from recommandeur import ML_DIR, charger_depuis_base, distance_km

GRAINE = 42
NB_UTILISATEURS = 300
SORTIE = ML_DIR / "data" / "simulated" / "interactions.parquet"

QUARTIERS = {
    "Maârif": (33.5822, -7.6327), "Aïn Sebaâ": (33.6050, -7.5330), "Hay Hassani": (33.5560, -7.6750),
    "Sidi Maârouf": (33.5330, -7.6450), "Mers Sultan": (33.5870, -7.6110), "Aïn Chock": (33.5470, -7.5940),
    "Sidi Bernoussi": (33.6130, -7.5000), "Hay Mohammadi": (33.5960, -7.5600), "Bourgogne": (33.5990, -7.6430),
    "Oulfa": (33.5550, -7.6930), "Roches Noires": (33.6000, -7.5800), "Californie": (33.5420, -7.6200),
}
FREQUENCES_CATEGORIES = {
    "entretien_courant": 0.30, "freins": 0.15, "moteur": 0.12, "electrique": 0.10, "pneus_suspension": 0.10,
    "climatisation": 0.06, "carrosserie": 0.06, "transmission": 0.04, "direction": 0.04, "echappement": 0.03,
}
COMPETENCE = {"confirmee": 1.0, "hypothese_generaliste": 0.8, "aucune": 0.05}
KM_PAR_DEGRE_LAT = 111.0


def competence(garage, categorie) -> float:
    if categorie not in garage.specialites:
        return COMPETENCE["aucune"]
    return COMPETENCE["hypothese_generaliste" if garage.specialites_source == "hypothese_generaliste" else "confirmee"]


def simuler(garages, rng) -> pd.DataFrame:
    garages = [g for g in garages if g.lat is not None]
    qualite = rng.normal(0, 1, len(garages))
    premium_garage = rng.random(len(garages)) < 0.3
    categories, frequences = zip(*FREQUENCES_CATEGORIES.items())
    noms_quartiers = list(QUARTIERS)

    lignes = []
    for u in range(NB_UTILISATEURS):
        quartier = noms_quartiers[rng.integers(len(noms_quartiers))]
        lat0, lon0 = QUARTIERS[quartier]
        lat = lat0 + rng.normal(0, 1.5) / KM_PAR_DEGRE_LAT
        lon = lon0 + rng.normal(0, 1.5) / (KM_PAR_DEGRE_LAT * np.cos(np.radians(lat0)))
        premium = rng.random() < 0.3
        distances = np.array([distance_km(lat, lon, g.lat, g.lon) for g in garages])
        satisfait = np.zeros(len(garages), dtype=bool)

        for rang in range(1 + rng.poisson(4)):
            categorie = rng.choice(categories, p=frequences)
            comp = np.array([competence(g, categorie) for g in garages])
            utilite = (-distances / 2.5 + np.log(comp) + 1.0 * qualite
                       + 0.8 * (premium_garage == premium) + 1.0 * satisfait)
            proba = np.exp(utilite - utilite.max())
            choix = rng.choice(len(garages), p=proba / proba.sum())
            note = int(np.clip(np.round(3.4 + 0.7 * qualite[choix] + 0.5 * (premium_garage[choix] == premium)
                                        + rng.normal(0, 0.6)), 1, 5))
            satisfait[choix] |= note >= 4
            lignes.append({
                "user_id": u, "rang": rang, "quartier": quartier, "user_lat": lat, "user_lon": lon,
                "user_premium": premium, "categorie": categorie, "garage_id": garages[choix].id,
                "distance_km": round(float(distances[choix]), 2), "note": note,
            })
    return pd.DataFrame(lignes)


def main():
    _pannes, garages = charger_depuis_base()
    interactions = simuler(garages, np.random.default_rng(GRAINE))
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    interactions.to_parquet(SORTIE, index=False)
    par_user = interactions.groupby("user_id").size()
    print(f"{len(interactions)} interventions simulées, {interactions.user_id.nunique()} utilisateurs "
          f"({par_user.mean():.1f} en moyenne), {interactions.garage_id.nunique()} garages choisis au moins une fois")
    print(f"Distance moyenne au garage choisi : {interactions.distance_km.mean():.1f} km ; "
          f"note moyenne : {interactions.note.mean():.2f}")
    print("Catégories :", interactions.categorie.value_counts(normalize=True).round(2).to_dict())


if __name__ == "__main__":
    main()
