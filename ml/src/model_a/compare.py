"""
Modèle A — étape A.4 : comparaison de 5 modèles dans les mêmes conditions.

Tous les modèles : même jeu d'entraînement, même jeu de validation, mêmes variables,
même cible (log du prix), mêmes mesures en dirhams. Paramètres raisonnables par défaut,
sans réglage fin : seul le meilleur sera réglé ensuite avec Optuna (tune.py).
Le jeu de test n'est PAS utilisé ici — il est réservé à l'évaluation finale.

Sorties : ml/reports/model_a_comparison.json, ml/reports/figures/a4_comparaison.png,
          runs MLflow dans ml/mlflow.db (expérience "model_a_comparaison")

Usage : ml/venv/Scripts/python ml/src/model_a/compare.py
"""

import json
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

from features import CATEGORIELLES, GRAINE, ML_DIR, Preparateur, charger, cible, decouper, mesures

REPORT_PATH = ML_DIR / "reports" / "model_a_comparison.json"
FIG_PATH = ML_DIR / "reports" / "figures" / "a4_comparaison.png"


class MedianeParGroupe:
    """Référence naïve : le prix médian des annonces du train de même marque + modèle + âge.

    Si le groupe est trop petit (< 5 annonces), on se replie sur marque + modèle,
    puis marque, puis la médiane globale — comme le ferait une personne qui estime
    un prix en regardant des annonces similaires.
    """

    NIVEAUX = [["modele", "age"], ["modele"], ["marque"]]
    MIN_GROUPE = 5

    def fit(self, X, y):
        donnees = X.assign(y=y)
        self.tables = []
        for cles in self.NIVEAUX:
            stats = donnees.groupby(cles, observed=True)["y"].agg(["median", "size"])
            self.tables.append((cles, stats[stats["size"] >= self.MIN_GROUPE]["median"]))
        self.globale = float(np.median(y))
        return self

    def predict(self, X):
        prediction = pd.Series(np.nan, index=X.index)
        for cles, table in self.tables:
            manquants = prediction.isna()
            if not manquants.any():
                break
            index = pd.MultiIndex.from_frame(X.loc[manquants, cles]) if len(cles) > 1 else X.loc[manquants, cles[0]]
            prediction[manquants] = table.reindex(index).to_numpy()
        return prediction.fillna(self.globale).to_numpy()


def regression_lineaire(numeriques):
    """Ridge (régression linéaire avec une légère régularisation, pour rester stable
    avec ~700 colonnes après encodage one-hot des catégories)."""
    preparation = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORIELLES),
        ("num", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), numeriques),
    ])
    return make_pipeline(preparation, Ridge(alpha=1.0))


class EncodageCodes:
    """Random Forest (scikit-learn) ne lit pas les catégories : on les remplace par leur code entier."""

    def __init__(self, modele):
        self.modele = modele

    def _coder(self, X):
        X = X.copy()
        for col in CATEGORIELLES:
            X[col] = X[col].cat.codes
        return X

    def fit(self, X, y):
        self.modele.fit(self._coder(X), y)
        return self

    def predict(self, X):
        return self.modele.predict(self._coder(X))


class CatBoostTexte:
    """CatBoost attend les catégories sous forme de texte, et les traite nativement."""

    def __init__(self, **params):
        self.modele = CatBoostRegressor(**params)

    def _texte(self, X):
        X = X.copy()
        for col in CATEGORIELLES:
            X[col] = X[col].astype(str)
        return X

    def fit(self, X, y):
        self.modele.fit(self._texte(X), y, cat_features=CATEGORIELLES, verbose=False)
        return self

    def predict(self, X):
        return self.modele.predict(self._texte(X))


def candidats(numeriques):
    return {
        "Médiane par groupe": (MedianeParGroupe(), {"niveaux": "modele+age > modele > marque", "min_groupe": 5}),
        "Régression linéaire": (regression_lineaire(numeriques), {"alpha": 1.0, "encodage": "one-hot"}),
        "Random Forest": (
            EncodageCodes(RandomForestRegressor(
                n_estimators=300, max_features=0.5, min_samples_leaf=2, n_jobs=-1, random_state=GRAINE)),
            {"n_estimators": 300, "max_features": 0.5, "min_samples_leaf": 2},
        ),
        "XGBoost": (
            XGBRegressor(
                n_estimators=1000, learning_rate=0.05, max_depth=8, subsample=0.8, colsample_bytree=0.8,
                tree_method="hist", enable_categorical=True, max_cat_to_onehot=1, n_jobs=-1, random_state=GRAINE),
            {"n_estimators": 1000, "learning_rate": 0.05, "max_depth": 8, "subsample": 0.8, "colsample_bytree": 0.8},
        ),
        "CatBoost": (
            CatBoostTexte(iterations=1500, learning_rate=0.08, depth=8, random_seed=GRAINE, thread_count=-1),
            {"iterations": 1500, "learning_rate": 0.08, "depth": 8},
        ),
    }


def configurer_mlflow(experience):
    mlflow.set_tracking_uri(f"sqlite:///{(ML_DIR / 'mlflow.db').as_posix()}")
    if mlflow.get_experiment_by_name(experience) is None:
        mlflow.create_experiment(experience, artifact_location=(ML_DIR / "mlruns").as_uri())
    mlflow.set_experiment(experience)


def main():
    df = charger()
    train, val, _test = decouper(df)
    prep = Preparateur().fit(train)
    X_train, X_val = prep.transform(train), prep.transform(val)
    y_train = cible(train)
    prix_val = val["prix"].to_numpy()
    numeriques = [c for c in X_train.columns if c not in CATEGORIELLES]

    print(f"train {len(train):,} | validation {len(val):,} | test {len(_test):,} (non utilisé ici)")
    print(f"{X_train.shape[1]} variables ; catégories après regroupement : "
          + ", ".join(f"{c}={len(prep.categories[c]) + 1}" for c in CATEGORIELLES) + "\n")

    configurer_mlflow("model_a_comparaison")
    resultats = []
    for nom, (modele, params) in candidats(numeriques).items():
        debut = time.perf_counter()
        modele.fit(X_train, y_train)
        duree_fit = time.perf_counter() - debut
        debut = time.perf_counter()
        prix_predit = np.exp(modele.predict(X_val))
        duree_pred_ms = (time.perf_counter() - debut) / len(X_val) * 1000

        m = mesures(prix_val, prix_predit)
        m.update({"duree_entrainement_s": round(duree_fit, 1), "prediction_ms_par_annonce": round(duree_pred_ms, 4)})
        resultats.append({"modele": nom, "parametres": params, **m})
        with mlflow.start_run(run_name=nom):
            mlflow.log_params(params)
            mlflow.log_metrics({k.replace("%", "pct"): v for k, v in m.items()})
        print(f"{nom:<20} MAE {m['MAE_DH']:>9,.0f} DH | MAPE {m['MAPE_pct']:5.1f} % | R² {m['R2']:.3f} "
              f"| ±15 % : {m['part_a_moins_de_15pct']:4.1f} % | {duree_fit:6.1f} s")

    resultats.sort(key=lambda r: r["MAE_DH"])
    meilleur = resultats[0]["modele"]
    REPORT_PATH.write_text(json.dumps({
        "jeu_evaluation": "validation (15 %)",
        "tailles": {"train": len(train), "validation": len(val), "test": len(_test)},
        "critere_de_choix": "MAE_DH la plus basse sur la validation",
        "meilleur": meilleur,
        "resultats": resultats,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    tableau = pd.DataFrame(resultats).set_index("modele").iloc[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    couleurs = ["#4C72B0" if n != meilleur else "#55A868" for n in tableau.index]
    axes[0].barh(tableau.index, tableau["MAE_DH"], color=couleurs)
    axes[0].set_title("Erreur moyenne (MAE, DH) — plus bas = mieux")
    axes[1].barh(tableau.index, tableau["part_a_moins_de_15pct"], color=couleurs)
    axes[1].set_title("Annonces estimées à ±15 % près (%) — plus haut = mieux")
    for ax, col, fmt in [(axes[0], "MAE_DH", "{:,.0f}"), (axes[1], "part_a_moins_de_15pct", "{:.1f}")]:
        for y, v in enumerate(tableau[col]):
            ax.text(v, y, " " + fmt.format(v), va="center", fontsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG_PATH, dpi=110)
    print(f"\nMeilleur modèle (MAE validation) : {meilleur}")


if __name__ == "__main__":
    main()
