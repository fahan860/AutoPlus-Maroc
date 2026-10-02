"""
Modèle C — étape C.3 : comparaison de 4 méthodes de détection de faux avis.

Données SIMULÉES (simulate_avis.py). Découpage temporel :
  entraînement = 9 premiers mois (dont les 2 derniers servent de validation pour fixer
  les seuils), test = 3 derniers mois, qui contient en plus un type de fraude jamais vu
  à l'entraînement (« sophistique »).

Méthodes :
  1. Règles du planning (aucun apprentissage)
  2. Isolation Forest : non supervisé, apprend ce qui est « normal » sans étiquettes
  3. Régression logistique : supervisée, interprétable
  4. Gradient boosting (HistGradientBoosting) : supervisé, non linéaire

Mesures sur le test : précision (part des avis signalés qui sont vraiment faux), rappel
(part des faux avis détectés), F1, PR-AUC, et rappel par type de fraude.

Sorties : ml/reports/model_c_comparaison.json, ml/reports/figures/c3_*.png
Usage   : ml/venv/Scripts/python ml/src/model_c/compare_avis.py
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import signaux
from signaux import transformer
from simulate_avis import DEBUT_TEST, ML_DIR, SORTIE

GRAINE = 42
DEBUT_VALIDATION = DEBUT_TEST - pd.Timedelta(days=61)
REPORT_PATH = ML_DIR / "reports" / "model_c_comparaison.json"
FIG_DIR = ML_DIR / "reports" / "figures"


def regles(X: pd.DataFrame, avis: pd.DataFrame) -> np.ndarray:
    """Règles comportementales du planning (S6), sans apprentissage. Score 0/1."""
    note = avis.loc[X.index, "note"]
    compte_neuf = X["anciennete_compte_h"] < 24
    return (
        (compte_neuf & (note == 5))                                                          # compte < 24 h + 5★
        | ((X["rdv_termine"] == 0) & (X["note_extreme"] == 1) & (X["anciennete_compte_h"] < 24 * 7))  # sans RDV, note extrême, compte < 7 j
        | (X["avis_garage_48h"] >= 3)                                                        # rafale sur le garage
    ).astype(float).to_numpy()



def seuil_f1(y, scores) -> float:
    """Seuil qui maximise le F1 sur la validation."""
    candidats = np.unique(np.quantile(scores, np.linspace(0.5, 0.995, 200)))
    return float(max(candidats, key=lambda s: f1_score(y, scores >= s, zero_division=0)))


def mesures(y, decision, scores, types) -> dict:
    par_type = {t: 100 * float(decision[(types == t)].mean()) for t in sorted(set(types)) if t != "authentique"}
    return {
        "precision_pct": 100 * precision_score(y, decision, zero_division=0),
        "rappel_pct": 100 * recall_score(y, decision),
        "F1": f1_score(y, decision),
        "PR_AUC": average_precision_score(y, scores),
        "faux_positifs_pct_des_vrais_avis": 100 * float(decision[~y].mean()),
        "rappel_par_type_pct": par_type,
    }


def main():
    avis = pd.read_parquet(SORTIE)
    entr = avis[avis.jeu == "entrainement"]
    X_entr, vectoriseur = signaux.calculer(entr)
    # Le test est calculé avec tout l'historique disponible (les avis antérieurs comptent pour
    # les rafales et la similarité), mais le vectoriseur reste celui appris à l'entraînement
    X_tout, _ = signaux.calculer(avis, vectoriseur)
    X_test = X_tout.loc[avis.index[avis.jeu == "test"]]

    y_entr = entr["faux"].to_numpy()
    est_val = (entr["date"] >= DEBUT_VALIDATION).to_numpy()
    y_test = avis.loc[X_test.index, "faux"].to_numpy()
    types_test = avis.loc[X_test.index, "type_fraude"].to_numpy()
    types_val = entr["type_fraude"].to_numpy()[est_val]
    print(f"Entraînement {len(X_entr)} avis (dont validation {est_val.sum()}), test {len(X_test)} avis, "
          f"{y_test.mean():.1%} de faux dans le test")

    resultats, scores_test = {}, {}

    # 1. Règles
    s = regles(X_test, avis)
    resultats["Règles (planning)"] = mesures(y_test, s >= 0.5, s, types_test)
    scores_test["Règles (planning)"] = s

    # 2. Isolation Forest : appris sur les avis du début de l'entraînement, sans étiquettes.
    # Seuil fixé par le taux de signalement visé (10 %), pas par les étiquettes.
    iforest = make_pipeline(StandardScaler(), IsolationForest(n_estimators=300, contamination=0.10, random_state=GRAINE))
    iforest.fit(transformer(X_entr[~est_val]))
    s = -iforest.decision_function(transformer(X_test))
    resultats["Isolation Forest"] = mesures(y_test, s >= 0, s, types_test)
    scores_test["Isolation Forest"] = s

    # 3 et 4. Supervisés : appris sur le début de l'entraînement, seuil choisi sur la validation
    supervises = {
        "Régression logistique": make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=2000)),
        "Gradient boosting": HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, class_weight="balanced",
                                                            random_state=GRAINE),
    }
    for nom, modele in supervises.items():
        modele.fit(transformer(X_entr[~est_val]), y_entr[~est_val])
        seuil = seuil_f1(y_entr[est_val], modele.predict_proba(transformer(X_entr[est_val]))[:, 1])
        modele.fit(transformer(X_entr), y_entr)  # réentraîné sur tout l'entraînement, même seuil
        s = modele.predict_proba(transformer(X_test))[:, 1]
        resultats[nom] = {**mesures(y_test, s >= seuil, s, types_test), "seuil": seuil}
        scores_test[nom] = s

    # 5. Système retenu, fixé par raisonnement produit (pas réglé sur le test) :
    #    - MASQUÉ (en attente de vérification) : gradient boosting OU avis sur un RDV annulé
    #      (on ne note pas un garage où l'on n'est pas allé). Doit être très précis : masquer
    #      l'avis d'un vrai client est grave.
    #    - À SURVEILLER (reste publié, signalé à l'admin) : le 1 % d'avis les plus inhabituels
    #      selon un Isolation Forest appris sur les avis authentiques. Capacité de vérification
    #      de l'admin ; c'est ce niveau qui peut repérer une fraude d'un type nouveau.
    gb = supervises["Gradient boosting"]
    masque = (scores_test["Gradient boosting"] >= resultats["Gradient boosting"]["seuil"]) | (X_test["rdv_annule"].to_numpy() == 1)
    if_normal = make_pipeline(StandardScaler(), IsolationForest(n_estimators=300, random_state=GRAINE))
    if_normal.fit(transformer(X_entr[~y_entr]))
    seuil_surveillance = float(np.quantile(-if_normal.decision_function(transformer(X_entr[~y_entr])), 0.99))
    surveille = (-if_normal.decision_function(transformer(X_test)) >= seuil_surveillance) & ~masque
    s = scores_test["Gradient boosting"] + masque
    resultats["Retenu : masqué (GB + RDV annulé)"] = mesures(y_test, masque, s, types_test)
    resultats["Retenu : masqué + surveillé"] = mesures(y_test, masque | surveille, s, types_test)
    systeme = {
        "seuil_gradient_boosting": resultats["Gradient boosting"]["seuil"],
        "seuil_surveillance_isolation_forest": seuil_surveillance,
        "avis_masques_test": int(masque.sum()), "avis_surveilles_test": int(surveille.sum()),
        "faux_parmi_surveilles": int(y_test[surveille].sum()),
    }
    print(f"Système retenu : {masque.sum()} avis masqués, {surveille.sum()} à surveiller "
          f"(dont {y_test[surveille].sum()} vraiment faux) sur {len(y_test)}")

    print(f"\n{'Méthode':<34} {'Précision':>9} {'Rappel':>7} {'F1':>5} {'PR-AUC':>7} {'Faux +':>7} | rappel par type")
    for nom, m in resultats.items():
        types = " ".join(f"{t[:10]}={v:.0f}%" for t, v in m["rappel_par_type_pct"].items())
        print(f"{nom:<34} {m['precision_pct']:8.1f}% {m['rappel_pct']:6.1f}% {m['F1']:5.2f} {m['PR_AUC']:7.3f} "
              f"{m['faux_positifs_pct_des_vrais_avis']:6.1f}% | {types}")

    # Importance des signaux (régression logistique : coefficients sur variables standardisées)
    logit = supervises["Régression logistique"]
    coefs = pd.Series(logit[-1].coef_[0], index=signaux.COLONNES).sort_values()

    REPORT_PATH.write_text(json.dumps({
        "avertissement": "Avis simulés (simulate_avis.py) : comparaison des méthodes, pas une performance réelle",
        "tailles": {"entrainement": len(X_entr), "test": len(X_test), "part_faux_test": float(y_test.mean())},
        "resultats_test": resultats,
        "systeme_retenu": systeme,
        "coefficients_regression_logistique": coefs.round(3).to_dict(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
    noms = list(resultats)
    x = np.arange(len(noms))
    for i, (cle, libelle) in enumerate([("precision_pct", "Précision"), ("rappel_pct", "Rappel")]):
        barres = axes[0].bar(x + (i - 0.5) * 0.38, [resultats[n][cle] for n in noms], 0.38, label=libelle,
                             color=["#4C72B0", "#DD8452"][i])
        axes[0].bar_label(barres, fmt="%.0f", fontsize=8)
    axes[0].set_xticks(x, [n.replace(" (planning)", "\n(planning)").replace("Régression ", "Régression\n") for n in noms],
                       fontsize=8)
    axes[0].set_ylim(0, 110)
    axes[0].set_title("Jeu de test (3 derniers mois)")
    axes[0].legend(fontsize=8)
    types = list(resultats[noms[0]]["rappel_par_type_pct"])
    for j, nom in enumerate(noms):
        axes[1].bar(np.arange(len(types)) + (j - 1.5) * 0.2, [resultats[nom]["rappel_par_type_pct"][t] for t in types],
                    0.2, label=nom)
    axes[1].set_xticks(np.arange(len(types)), [t.replace("_", " ") + ("\n(jamais vu)" if t == "sophistique" else "")
                                               for t in types], fontsize=8)
    axes[1].set_ylim(0, 105)
    axes[1].set_title("Part des faux avis détectés, par type")
    axes[1].legend(fontsize=7)
    for ax in axes:
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Détection de faux avis — données simulées", y=1.02)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "c3_comparaison.png", dpi=110, bbox_inches="tight")


if __name__ == "__main__":
    main()
