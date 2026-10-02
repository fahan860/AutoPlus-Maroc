"""
Modèle A — fourchettes de prix pour le service de prédiction.

Le modèle donne un prix ; l'utilisateur a aussi besoin de savoir à quel point s'y fier.
Pour chaque tranche de prix PRÉDIT, on mesure sur le jeu de test (jamais vu à
l'entraînement) le rapport prix_réel / prix_prédit, et on garde ses quantiles 10 % et 90 % :
la fourchette [prédit × q10 ; prédit × q90] contient le prix réel de ~80 % des annonces.
Elle est plus large pour les voitures bon marché, où le modèle est moins précis.

Écrit aussi le préparateur en JSON (lu par le service, sans pickle).
Appelé à la fin de tune.py ; peut être relancé seul :
    ml/venv/Scripts/python ml/src/model_a/calibrate.py
"""

import json

import joblib
import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from features import ML_DIR, Preparateur, charger, charger_modele, decouper, sauver_modele

MODEL_DIR = ML_DIR / "models" / "model_a"
COUVERTURE = 0.80
# Bornes des tranches de prix prédit (DH) ; la dernière tranche va jusqu'à l'infini
BORNES_TRANCHES = [0, 50_000, 100_000, 200_000, 400_000]


def calculer_fourchettes(prix_reel: np.ndarray, prix_predit: np.ndarray) -> list[dict]:
    q_bas, q_haut = (1 - COUVERTURE) / 2, 1 - (1 - COUVERTURE) / 2
    ratio = prix_reel / prix_predit
    bornes = BORNES_TRANCHES + [np.inf]
    tranches = pd.cut(prix_predit, bornes, right=False, labels=False)
    fourchettes = []
    for i in range(len(BORNES_TRANCHES)):
        r = ratio[tranches == i]
        fourchettes.append({
            "prix_predit_min": BORNES_TRANCHES[i],
            "prix_predit_max": None if np.isinf(bornes[i + 1]) else bornes[i + 1],
            "facteur_bas": round(float(np.quantile(r, q_bas)), 4),
            "facteur_haut": round(float(np.quantile(r, q_haut)), 4),
            "annonces": int(len(r)),
        })
    return fourchettes


def main():
    # Modèle produit par une version de tune.py antérieure au format compressé / à l'export
    # JSON du préparateur : on le convertit, puis on supprime les anciens fichiers.
    ancien_modele, ancien_prep = MODEL_DIR / "xgboost.json", MODEL_DIR / "preparateur.joblib"
    if ancien_modele.exists():
        modele = XGBRegressor()
        modele.load_model(ancien_modele)
        sauver_modele(modele, MODEL_DIR)
        ancien_modele.unlink()
    if ancien_prep.exists():
        joblib.load(ancien_prep).sauver(MODEL_DIR / "preparateur.json")
        ancien_prep.unlink()

    modele = charger_modele(MODEL_DIR)
    prep = Preparateur.charger(MODEL_DIR / "preparateur.json")

    _train, _val, test = decouper(charger())
    prix_reel = test["prix"].to_numpy()
    prix_predit = np.exp(modele.predict(prep.transform(test)))
    fourchettes = calculer_fourchettes(prix_reel, prix_predit)

    # Vérification : part des prix réels effectivement dans leur fourchette
    tranches = pd.cut(prix_predit, BORNES_TRANCHES + [np.inf], right=False, labels=False)
    bas = np.array([fourchettes[t]["facteur_bas"] for t in tranches]) * prix_predit
    haut = np.array([fourchettes[t]["facteur_haut"] for t in tranches]) * prix_predit
    couverture = float(((prix_reel >= bas) & (prix_reel <= haut)).mean())

    chemin_fiche = MODEL_DIR / "fiche_modele.json"
    fiche = json.loads(chemin_fiche.read_text(encoding="utf-8"))
    fiche["fourchettes"] = {
        "methode": f"quantiles {100 * (1 - COUVERTURE) / 2:.0f} % / {100 * (1 + COUVERTURE) / 2:.0f} % "
                   "du rapport prix réel / prix prédit sur le jeu de test, par tranche de prix prédit",
        "couverture_visee": COUVERTURE,
        "couverture_mesuree": round(couverture, 4),
        "tranches": fourchettes,
    }
    chemin_fiche.write_text(json.dumps(fiche, ensure_ascii=False, indent=2), encoding="utf-8")

    for f in fourchettes:
        fin = f"{f['prix_predit_max']:,}" if f["prix_predit_max"] else "+"
        print(f"{f['prix_predit_min']:>8,} – {fin:>8} DH : [{f['facteur_bas']:.2f} ; {f['facteur_haut']:.2f}] × prédit "
              f"({f['annonces']} annonces)")
    print(f"Couverture mesurée : {couverture:.1%} (visée {COUVERTURE:.0%})")


if __name__ == "__main__":
    main()
