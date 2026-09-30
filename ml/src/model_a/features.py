"""
Modèle A — étape A.3 : découpage train / validation / test et préparation des variables.

Partagé par tous les modèles comparés (compare.py) et par le réglage final (tune.py),
pour garantir les mêmes conditions : mêmes annonces dans chaque jeu, mêmes variables.

Règle anti-fuite : tout ce qui s'apprend sur les données (catégories rares, médianes...)
est calculé sur le jeu d'entraînement uniquement, puis appliqué tel quel aux autres jeux.
"""

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd

ML_DIR = Path(__file__).resolve().parents[2]
CLEAN_PATH = ML_DIR / "data" / "processed" / "mucars_clean.parquet"

GRAINE = 42  # fixée pour que le découpage et les modèles soient reproductibles
PART_VALIDATION, PART_TEST = 0.15, 0.15
MIN_OCCURRENCES = 20  # une catégorie vue moins souvent dans le train est regroupée en "autre"

CIBLE = "prix"
CATEGORIELLES = ["marque", "modele", "boite", "carburant", "etat", "origine", "premiere_main", "ville"]
NUMERIQUES = ["age", "kilometrage", "puissance_fiscale", "nb_portes", "nb_equipements"]
BOOLEENNES = ["km_inconnu"]  # + les colonnes eq_* ajoutées dynamiquement
# Non utilisées : "annee" (redondante avec "age"), "secteur" (quartier : ~2 000 valeurs, trop fin)


def charger() -> pd.DataFrame:
    df = pd.read_parquet(CLEAN_PATH)
    # Un modèle n'a de sens qu'au sein de sa marque ("serie 3" n'existe que chez BMW)
    df["modele"] = df["marque"] + " | " + df["modele"]
    return df


def decouper(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """70 / 15 / 15, stratifié sur les déciles de prix pour que chaque jeu couvre toute la gamme.

    Pas de découpage temporel : toutes les annonces datent de 2024, sans date précise.
    """
    # Import local : le service de prédiction importe ce module sans avoir besoin de scikit-learn
    from sklearn.model_selection import train_test_split

    deciles = pd.qcut(df[CIBLE], 10, labels=False)
    train, reste = train_test_split(
        df, test_size=PART_VALIDATION + PART_TEST, stratify=deciles, random_state=GRAINE
    )
    val, test = train_test_split(
        reste, test_size=PART_TEST / (PART_VALIDATION + PART_TEST), stratify=deciles.loc[reste.index], random_state=GRAINE
    )
    return train.reset_index(drop=True), val.reset_index(drop=True), test.reset_index(drop=True)


def colonnes_variables(df: pd.DataFrame) -> list[str]:
    equipements = sorted(c for c in df.columns if c.startswith("eq_"))
    return CATEGORIELLES + NUMERIQUES + BOOLEENNES + equipements


class Preparateur:
    """Regroupe les catégories rares et fixe la liste des variables — appris sur le train seul."""

    def fit(self, train: pd.DataFrame) -> "Preparateur":
        self.variables = colonnes_variables(train)
        self.categories = {}
        for col in CATEGORIELLES:
            frequences = train[col].value_counts()
            self.categories[col] = sorted(frequences[frequences >= MIN_OCCURRENCES].index)
        return self

    def sauver(self, chemin: Path) -> None:
        """JSON plutôt que pickle : lisible, sans exécution de code au chargement,
        indépendant des versions de Python/pandas du service qui le relit."""
        chemin.write_text(json.dumps({"variables": self.variables, "categories": self.categories},
                                     ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def charger(cls, chemin: Path) -> "Preparateur":
        contenu = json.loads(chemin.read_text(encoding="utf-8"))
        prep = cls()
        prep.variables, prep.categories = contenu["variables"], contenu["categories"]
        return prep

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        X = df[self.variables].copy()
        for col in CATEGORIELLES:
            connues = self.categories[col]
            X[col] = pd.Categorical(X[col].where(X[col].isin(connues), "autre"), categories=connues + ["autre"])
        for col in BOOLEENNES + [c for c in self.variables if c.startswith("eq_")]:
            X[col] = X[col].astype(int)
        return X


NOM_FICHIER_MODELE = "xgboost.ubj.gz"


def sauver_modele(modele, dossier: Path) -> Path:
    """Format binaire UBJSON d'XGBoost + gzip : ~5x plus léger que le JSON (22 Mo au lieu de
    112 Mo pour ~1 000 arbres de profondeur 12), prédictions strictement identiques.
    Nécessaire pour rester sous la limite de 100 Mo par fichier de GitHub."""
    chemin = dossier / NOM_FICHIER_MODELE
    chemin.write_bytes(gzip.compress(bytes(modele.get_booster().save_raw("ubj")), compresslevel=6))
    return chemin


class ModeleCharge:
    """Modèle rechargé pour la prédiction, via le Booster natif d'XGBoost : contrairement à
    XGBRegressor, il ne dépend pas de scikit-learn (image Docker du service plus légère)."""

    def __init__(self, booster):
        self.booster = booster

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        import xgboost

        return self.booster.predict(xgboost.DMatrix(X, enable_categorical=True))


def charger_modele(dossier: Path) -> ModeleCharge:
    import xgboost

    booster = xgboost.Booster()
    booster.load_model(bytearray(gzip.decompress((dossier / NOM_FICHIER_MODELE).read_bytes())))
    return ModeleCharge(booster)


def cible(df: pd.DataFrame) -> np.ndarray:
    """Les modèles apprennent log(prix) : une erreur de 10 000 DH n'a pas le même poids
    sur une voiture à 40 000 DH que sur une à 600 000 DH ; l'erreur devient relative."""
    return np.log(df[CIBLE].to_numpy())


def mesures(prix_reel: np.ndarray, prix_predit: np.ndarray) -> dict:
    """Mesures calculées en dirhams (pas en log) pour être lisibles."""
    erreur = np.abs(prix_reel - prix_predit)
    return {
        "MAE_DH": float(erreur.mean()),
        "erreur_mediane_DH": float(np.median(erreur)),
        "MAPE_pct": float((erreur / prix_reel).mean() * 100),
        "R2": float(1 - ((prix_reel - prix_predit) ** 2).sum() / ((prix_reel - prix_reel.mean()) ** 2).sum()),
        "part_a_moins_de_15pct": float(((erreur / prix_reel) <= 0.15).mean() * 100),
    }
