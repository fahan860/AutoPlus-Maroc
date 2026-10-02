"""
Modèle C — entraînement du modèle servi en production (étape C.4).

Système retenu à l'étape C.3 (compare_avis.py) : gradient boosting + règle « avis sur un
RDV annulé ». Le seuil de décision est celui choisi sur la validation à l'étape C.3 ; le
modèle final est réentraîné sur l'ensemble des avis simulés.

À REMPLACER dès que l'app aura de vrais avis vérifiés par un admin : les décisions
« valide » / « rejete » de la modération deviennent les étiquettes d'entraînement.

Sorties : ml/models/model_c/ (gradient_boosting.joblib, vectoriseur.joblib, fiche_modele.json)
Usage   : ml/venv/Scripts/python ml/src/model_c/train_avis.py
"""

import json
from datetime import date

import joblib
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

import signaux
from compare_avis import GRAINE, REPORT_PATH
from signaux import transformer
from simulate_avis import ML_DIR, SORTIE

MODEL_DIR = ML_DIR / "models" / "model_c"


def main():
    avis = pd.read_parquet(SORTIE)
    X, vectoriseur = signaux.calculer(avis)
    y = avis.loc[X.index, "faux"].to_numpy()
    seuil = json.loads(REPORT_PATH.read_text(encoding="utf-8"))["systeme_retenu"]["seuil_gradient_boosting"]

    modele = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, class_weight="balanced",
                                            random_state=GRAINE).fit(transformer(X), y)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(modele, MODEL_DIR / "gradient_boosting.joblib")
    joblib.dump(vectoriseur, MODEL_DIR / "vectoriseur.joblib")
    (MODEL_DIR / "fiche_modele.json").write_text(json.dumps({
        "nom": "AUTO+ Modèle C — détection de faux avis",
        "algorithme": "HistGradientBoosting (scikit-learn) + règle « avis sur un RDV annulé »",
        "version": date.today().isoformat(),
        "donnees": f"{len(avis)} avis SIMULÉS (simulate_avis.py) — à remplacer par les décisions de modération réelles",
        "seuil_gradient_boosting": seuil,
        "signaux": signaux.COLONNES,
        "mesures_test_simule": json.loads(REPORT_PATH.read_text(encoding="utf-8"))["resultats_test"][
            "Retenu : masqué (GB + RDV annulé)"],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Modèle entraîné sur {len(X)} avis ({y.mean():.1%} de faux), seuil {seuil:.3f} -> {MODEL_DIR}")


if __name__ == "__main__":
    main()
