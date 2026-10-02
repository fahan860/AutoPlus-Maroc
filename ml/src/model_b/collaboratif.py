"""
Modèle B — étape B.3 : filtrage collaboratif (SVD) et recommandation hybride.

Données : interactions SIMULÉES (simulate.py) — démonstration du mécanisme, pas une mesure
de performance réelle. Le simulateur donne aux garages une qualité et un positionnement
cachés : seul l'historique des notes permet de les retrouver, c'est ce que le SVD doit
apprendre et que le filtrage par contenu ne peut pas voir.

Protocole (pour chaque utilisateur ayant ≥ 3 interventions) :
  - dernière intervention = test, avant-dernière = validation, le reste = entraînement ;
  - question : le garage réellement choisi est-il dans le top 5 recommandé ?
Stratégies comparées : popularité, contenu seul (étape B.2), SVD seul, hybride
(contenu + poids × SVD, poids choisi sur la validation).

Sorties : ml/reports/model_b_collaboratif.json, ml/reports/figures/b3_collaboratif.png
Usage   : ml/venv/Scripts/python ml/src/model_b/collaboratif.py
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from surprise import SVD, Dataset, Reader, accuracy
from surprise.model_selection import GridSearchCV

from recommandeur import ML_DIR, charger_depuis_base, scorer
from simulate import SORTIE as INTERACTIONS

GRAINE = 42
K = 5
POIDS_SVD_TESTES = [0.0, 0.2, 0.5, 0.8, 1.2, 2.0, 3.0, 5.0]
REPORT_PATH = ML_DIR / "reports" / "model_b_collaboratif.json"
FIG_PATH = ML_DIR / "reports" / "figures" / "b3_collaboratif.png"


def decouper(df: pd.DataFrame):
    df = df.sort_values(["user_id", "rang"])
    rang_inverse = df.groupby("user_id").cumcount(ascending=False)
    eligible = df.groupby("user_id")["rang"].transform("size") >= 3
    test = df[eligible & (rang_inverse == 0)]
    val = df[eligible & (rang_inverse == 1)]
    train = df.drop(test.index).drop(val.index)
    return train, val, test


def entrainer_svd(ratings: pd.DataFrame, params: dict) -> SVD:
    donnees = Dataset.load_from_df(ratings[["user_id", "garage_id", "note"]], Reader(rating_scale=(1, 5)))
    modele = SVD(random_state=GRAINE, **params)
    modele.fit(donnees.build_full_trainset())
    return modele


def regler_svd(train: pd.DataFrame) -> dict:
    donnees = Dataset.load_from_df(train[["user_id", "garage_id", "note"]], Reader(rating_scale=(1, 5)))
    grille = {"n_factors": [5, 20, 50], "reg_all": [0.02, 0.1], "n_epochs": [30], "lr_all": [0.005]}
    recherche = GridSearchCV(SVD, grille, measures=["rmse"], cv=3, joblib_verbose=0)
    recherche.fit(donnees)
    return recherche.best_params["rmse"]


def classements(cas: pd.DataFrame, garages, svd: SVD, popularite: pd.Series, poids_svd: list[float]) -> dict:
    """Pour chaque cas : rang du garage réellement choisi selon chaque stratégie."""
    ids = np.array([g.id for g in garages])
    pop = popularite.reindex(ids).fillna(0).to_numpy()
    rangs = {"Popularité": [], "SVD seul": [], **{f"hybride_{w}": [] for w in poids_svd}}

    def rang(scores, vrai):
        ordre = ids[np.argsort(-scores, kind="stable")]
        return int(np.where(ordre == vrai)[0][0]) + 1

    for ligne in cas.itertuples():
        # La catégorie est supposée connue : sa détection depuis le texte est évaluée à l'étape B.2
        contenu = np.array([r.score for r in scorer({ligne.categorie: 1.0}, garages, ligne.user_lat, ligne.user_lon)])
        collab = np.array([(svd.predict(ligne.user_id, gid).est - 1) / 4 for gid in ids])
        rangs["Popularité"].append(rang(pop, ligne.garage_id))
        rangs["SVD seul"].append(rang(collab, ligne.garage_id))
        for w in poids_svd:
            rangs[f"hybride_{w}"].append(rang(contenu + w * collab, ligne.garage_id))
    return rangs


def mesures(rangs: list[int]) -> dict:
    r = np.array(rangs)
    return {"hit_rate_top5_pct": 100 * float((r <= K).mean()), "MRR": float((1 / r).mean()),
            "rang_median": float(np.median(r))}


def main():
    _pannes, tous = charger_depuis_base()
    garages = [g for g in tous if g.lat is not None]
    df = pd.read_parquet(INTERACTIONS)
    train, val, test = decouper(df)
    print(f"Simulé : {len(train)} interactions d'entraînement, {len(val)} de validation, {len(test)} de test")

    # 1. SVD sur les notes (réglage par validation croisée sur le train)
    params = regler_svd(train)
    svd = entrainer_svd(train, params)
    ref = train["note"].mean()
    rmse_svd = accuracy.rmse([(r.user_id, r.garage_id, r.note, svd.predict(r.user_id, r.garage_id).est, None)
                              for r in val.itertuples()], verbose=False)
    rmse_ref = float(np.sqrt(((val["note"] - ref) ** 2).mean()))
    print(f"SVD {params} : RMSE validation {rmse_svd:.3f} (référence « note moyenne » : {rmse_ref:.3f})")

    # 2. Choix du poids du SVD dans l'hybride, sur la validation
    rangs_val = classements(val, garages, svd, train.groupby("garage_id").size(), POIDS_SVD_TESTES)
    mrr_val = {w: mesures(rangs_val[f"hybride_{w}"])["MRR"] for w in POIDS_SVD_TESTES}
    meilleur_w = max(mrr_val, key=mrr_val.get)
    print("MRR validation selon le poids du SVD :", {w: round(v, 3) for w, v in mrr_val.items()},
          f"-> poids retenu {meilleur_w}")

    # 3. Évaluation finale sur le test (modèle réentraîné sur train + validation)
    train_val = pd.concat([train, val])
    svd_final = entrainer_svd(train_val, params)
    rangs = classements(test, garages, svd_final, train_val.groupby("garage_id").size(), [0.0, meilleur_w])
    resultats = {
        "Popularité": mesures(rangs["Popularité"]),
        "Contenu seul (B.2)": mesures(rangs["hybride_0.0"]),
        "SVD seul": mesures(rangs["SVD seul"]),
        f"Hybride (contenu + {meilleur_w} × SVD)": mesures(rangs[f"hybride_{meilleur_w}"]),
    }
    print(f"\nTest ({len(test)} utilisateurs, {len(garages)} garages candidats) :")
    for nom, m in resultats.items():
        print(f"   {nom:<32} garage choisi dans le top 5 : {m['hit_rate_top5_pct']:5.1f} % | MRR {m['MRR']:.3f} "
              f"| rang médian {m['rang_median']:.0f}")

    REPORT_PATH.write_text(json.dumps({
        "avertissement": "Interactions simulées (simulate.py) : démonstration du mécanisme, pas une performance réelle",
        "tailles": {"train": len(train), "validation": len(val), "test": len(test), "garages": len(garages)},
        "svd": {"parametres": params, "rmse_validation": rmse_svd, "rmse_reference_moyenne": rmse_ref},
        "poids_svd": {"testes_mrr_validation": mrr_val, "retenu": meilleur_w},
        "test": resultats,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    noms = list(resultats)[::-1]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    valeurs = [resultats[n]["hit_rate_top5_pct"] for n in noms]
    barres = ax.barh(noms, valeurs, color=["#55A868" if n.startswith("Hybride") else "#4C72B0" for n in noms])
    ax.bar_label(barres, fmt=" %.1f %%", fontsize=9)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Garage réellement choisi présent dans le top 5 (%)")
    ax.set_title("Prochaine réparation : quel garage recommander ? (données simulées)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG_PATH, dpi=110)


if __name__ == "__main__":
    main()
