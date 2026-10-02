"""
Modèle A — étape A.5 / A.6 : réglage du meilleur modèle (XGBoost) avec Optuna,
puis entraînement final et évaluation unique sur le jeu de test.

1. Optuna cherche les meilleurs paramètres : entraînement sur le train, score = MAE (DH)
   sur la validation. Le nombre d'arbres est fixé par arrêt anticipé sur la validation.
2. Choix de l'essai : parmi les essais à moins de TOLERANCE_MAE du meilleur, le plus léger
   (nombre d'arbres × 2^profondeur). Le meilleur essai brut faisait 80 Mo compressé ; un essai
   à +0,03 % d'erreur donne le même score avec un modèle ~2x plus léger.
3. Le modèle final est réentraîné sur train + validation avec ces paramètres.
4. Il est évalué UNE SEULE FOIS sur le jeu de test, jamais vu jusque-là : c'est le score
   à annoncer dans le rapport. Le XGBoost non réglé de compare.py est évalué dans les
   mêmes conditions pour mesurer le gain du réglage.

Sorties : ml/models/model_a/           (modèle + préparateur JSON + fiche du modèle avec fourchettes)
          ml/reports/model_a_final.json, ml/reports/figures/a6_*.png
          runs MLflow dans ml/mlflow.db (expérience "model_a_reglage")

Usage : ml/venv/Scripts/python ml/src/model_a/tune.py [nb_essais]
        ml/venv/Scripts/python ml/src/model_a/tune.py --depuis-mlflow [nb_essais]
            -> saute Optuna et reprend les nb_essais derniers essais enregistrés dans MLflow
               (utile pour refaire l'étape finale sans relancer ~1 h de réglage)
"""

import json
import sys
from datetime import date

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import numpy as np
import optuna
import pandas as pd
from xgboost import XGBRegressor

import calibrate
from compare import candidats, configurer_mlflow
from features import CATEGORIELLES, GRAINE, ML_DIR, Preparateur, charger, cible, decouper, mesures, sauver_modele

MODEL_DIR = ML_DIR / "models" / "model_a"
REPORT_PATH = ML_DIR / "reports" / "model_a_final.json"
FIG_DIR = ML_DIR / "reports" / "figures"
DEPUIS_MLFLOW = "--depuis-mlflow" in sys.argv
_args = [a for a in sys.argv[1:] if not a.startswith("--")]
NB_ESSAIS = int(_args[0]) if _args else 40
MAX_ARBRES = 4000
TOLERANCE_MAE = 0.001  # 0,1 % : écart de MAE jugé négligeable (~13 DH sur ~12 700 DH)
PARAMS_ENTIERS = {"max_depth", "n_estimators", "max_cat_to_onehot"}


def params_essai(essai: optuna.Trial) -> dict:
    return {
        "learning_rate": essai.suggest_float("learning_rate", 0.01, 0.15, log=True),
        "max_depth": essai.suggest_int("max_depth", 4, 12),
        "min_child_weight": essai.suggest_float("min_child_weight", 1, 30, log=True),
        "subsample": essai.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": essai.suggest_float("colsample_bytree", 0.4, 1.0),
        "reg_lambda": essai.suggest_float("reg_lambda", 1e-3, 30, log=True),
        "reg_alpha": essai.suggest_float("reg_alpha", 1e-3, 10, log=True),
        "max_cat_to_onehot": essai.suggest_categorical("max_cat_to_onehot", [1, 8]),
    }


def xgb(**params) -> XGBRegressor:
    return XGBRegressor(tree_method="hist", enable_categorical=True, n_jobs=-1, random_state=GRAINE, **params)


def taille_relative(params: dict) -> int:
    """Nombre maximal de feuilles du modèle : proportionnel à sa taille sur disque et en mémoire."""
    return params["n_estimators"] * 2 ** params["max_depth"]


def choisir_essai(essais: list[dict]) -> dict:
    meilleure = min(e["mae"] for e in essais)
    equivalents = [e for e in essais if e["mae"] <= meilleure * (1 + TOLERANCE_MAE)]
    return min(equivalents, key=lambda e: taille_relative(e["params"]))


def optimiser(X_train, y_train, X_val, y_val, prix_val) -> list[dict]:
    optuna.logging.set_verbosity(optuna.logging.WARNING)

    def objectif(essai):
        params = params_essai(essai)
        modele = xgb(n_estimators=MAX_ARBRES, early_stopping_rounds=100, **params)
        modele.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        m = mesures(prix_val, np.exp(modele.predict(X_val)))
        essai.set_user_attr("n_estimators", modele.best_iteration + 1)
        with mlflow.start_run(run_name=f"essai_{essai.number:02d}"):
            mlflow.log_params({**params, "n_estimators": modele.best_iteration + 1})
            mlflow.log_metrics({k.replace("%", "pct"): v for k, v in m.items()})
        print(f"essai {essai.number:02d} : MAE {m['MAE_DH']:,.0f} DH ({modele.best_iteration + 1} arbres)", flush=True)
        return m["MAE_DH"]

    etude = optuna.create_study(direction="minimize", sampler=optuna.samplers.TPESampler(seed=GRAINE))
    etude.optimize(objectif, n_trials=NB_ESSAIS)
    return [
        {"nom": f"essai_{e.number:02d}", "mae": e.value, "params": {**e.params, "n_estimators": e.user_attrs["n_estimators"]}}
        for e in etude.trials
    ]


def essais_depuis_mlflow() -> list[dict]:
    """Les NB_ESSAIS derniers essais enregistrés (les plus récents = le dernier réglage complet)."""
    runs = mlflow.search_runs(experiment_names=["model_a_reglage"], filter_string="attributes.run_name LIKE 'essai_%'",
                              order_by=["attributes.start_time DESC"], max_results=NB_ESSAIS)
    essais = []
    for _, run in runs.iterrows():
        params = {k.removeprefix("params."): v for k, v in run.items() if k.startswith("params.") and v is not None}
        params = {k: int(v) if k in PARAMS_ENTIERS else float(v) for k, v in params.items()}
        essais.append({"nom": run["tags.mlflow.runName"], "mae": run["metrics.MAE_DH"], "params": params})
    return essais


def main():
    df = charger()
    train, val, test = decouper(df)
    configurer_mlflow("model_a_reglage")

    if DEPUIS_MLFLOW:
        essais = essais_depuis_mlflow()
        print(f"{len(essais)} essais repris depuis MLflow")
    else:
        prep = Preparateur().fit(train)
        essais = optimiser(prep.transform(train), cible(train), prep.transform(val), cible(val), val["prix"].to_numpy())

    meilleur = min(essais, key=lambda e: e["mae"])
    retenu = choisir_essai(essais)
    meilleurs = retenu["params"]
    print(f"\nMeilleur essai : {meilleur['nom']} — MAE validation {meilleur['mae']:,.0f} DH, "
          f"taille relative {taille_relative(meilleur['params']):,}")
    print(f"Essai retenu   : {retenu['nom']} — MAE validation {retenu['mae']:,.0f} DH, "
          f"taille relative {taille_relative(meilleurs):,} (le plus léger à moins de {TOLERANCE_MAE:.1%} du meilleur)")
    print(f"Paramètres : {meilleurs}")

    # --- Entraînement final sur train + validation, évaluation unique sur le test ---
    train_val = pd.concat([train, val], ignore_index=True)
    prep_final = Preparateur().fit(train_val)
    X_tv, X_test = prep_final.transform(train_val), prep_final.transform(test)
    y_tv = cible(train_val)
    prix_test = test["prix"].to_numpy()

    final = xgb(**meilleurs).fit(X_tv, y_tv)
    prix_predit = np.exp(final.predict(X_test))
    m_final = mesures(prix_test, prix_predit)

    numeriques = [c for c in X_tv.columns if c not in CATEGORIELLES]
    non_regle, params_defaut = candidats(numeriques)["XGBoost"]
    m_defaut = mesures(prix_test, np.exp(non_regle.fit(X_tv, y_tv).predict(X_test)))

    print(f"TEST — XGBoost réglé     : MAE {m_final['MAE_DH']:,.0f} DH | MAPE {m_final['MAPE_pct']:.1f} % "
          f"| R² {m_final['R2']:.3f} | ±15 % : {m_final['part_a_moins_de_15pct']:.1f} %")
    print(f"TEST — XGBoost non réglé : MAE {m_defaut['MAE_DH']:,.0f} DH | MAPE {m_defaut['MAPE_pct']:.1f} % "
          f"| R² {m_defaut['R2']:.3f} | ±15 % : {m_defaut['part_a_moins_de_15pct']:.1f} %")

    with mlflow.start_run(run_name=f"final_test_{retenu['nom']}"):
        mlflow.log_params(meilleurs)
        mlflow.log_metrics({f"test_{k.replace('%', 'pct')}": v for k, v in m_final.items()})

    # --- Sauvegarde du modèle retenu ---
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    sauver_modele(final, MODEL_DIR)
    prep_final.sauver(MODEL_DIR / "preparateur.json")
    fiche = {
        "nom": "AUTO+ Modèle A — estimation du prix d'un véhicule d'occasion",
        "algorithme": "XGBoost (régression sur log(prix))",
        "version": date.today().isoformat(),
        "donnees": "MUCars-2024 (DOI 10.17632/vjrbcb2rrt.2, CC BY 4.0), nettoyé par clean.py",
        "entraine_sur": f"train + validation ({len(train_val):,} annonces)",
        "parametres": meilleurs,
        "variables": prep_final.variables,
        "mesures_test": m_final,
        "limites": [
            "Prix demandés dans des annonces 2024, pas des prix de transaction",
            "Modèles/villes vus moins de 20 fois à l'entraînement traités comme 'autre'",
        ],
    }
    (MODEL_DIR / "fiche_modele.json").write_text(json.dumps(fiche, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- Rapport + figures ---
    erreur_rel = np.abs(prix_predit - prix_test) / prix_test
    tranches = pd.cut(prix_test, [0, 50_000, 100_000, 200_000, 400_000, 1_500_000],
                      labels=["< 50k", "50–100k", "100–200k", "200–400k", "> 400k"])
    par_tranche = (pd.DataFrame({"tranche": tranches, "err": np.abs(prix_predit - prix_test), "rel": erreur_rel})
                   .groupby("tranche", observed=True)
                   .agg(annonces=("err", "size"), MAE_DH=("err", "mean"), MAPE_pct=("rel", lambda s: s.mean() * 100)))
    importance = pd.Series(final.get_booster().get_score(importance_type="gain")).sort_values(ascending=False)
    importance = (importance / importance.sum() * 100).round(2)

    REPORT_PATH.write_text(json.dumps({
        "optuna": {
            "essais": len(essais),
            "meilleur_essai": {"nom": meilleur["nom"], "MAE_validation_DH": meilleur["mae"], "parametres": meilleur["params"]},
            "essai_retenu": {"nom": retenu["nom"], "MAE_validation_DH": retenu["mae"], "parametres": meilleurs},
            "regle_de_choix": f"le plus léger (arbres × 2^profondeur) parmi les essais à moins de {TOLERANCE_MAE:.1%} "
                              "de la meilleure MAE de validation",
        },
        "test_xgboost_regle": m_final,
        "test_xgboost_non_regle": {"parametres": params_defaut, **m_defaut},
        "erreur_par_tranche_de_prix": par_tranche.round(1).reset_index().to_dict(orient="records"),
        "importance_variables_pct_gain": importance.to_dict(),
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(prix_test, prix_predit, s=3, alpha=0.25)
    bornes = [15_000, 1_500_000]
    ax.plot(bornes, bornes, color="#C44E52", lw=1)
    ax.set(xscale="log", yscale="log", xlabel="Prix réel (DH)", ylabel="Prix prédit (DH)",
           title=f"Jeu de test — MAE {m_final['MAE_DH']:,.0f} DH, R² {m_final['R2']:.3f}")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG_DIR / "a6_reel_vs_predit.png", dpi=110)

    fig, ax = plt.subplots(figsize=(7, 5))
    top = importance.head(15).iloc[::-1]
    ax.barh(top.index, top.values, color="#4C72B0")
    ax.set(xlabel="Part du gain total (%)", title="Variables les plus utiles au modèle (XGBoost, gain)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG_DIR / "a6_importance_variables.png", dpi=110)

    print(f"\nModèle sauvegardé dans {MODEL_DIR.relative_to(ML_DIR.parent)}")
    print(par_tranche.round(1).to_string())
    print("\nFourchettes de prix (service de prédiction) :")
    calibrate.main()


if __name__ == "__main__":
    main()
