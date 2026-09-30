"""
Chargement du Modèle A et transformation d'une demande en prédiction.

La demande est convertie exactement dans le format produit par clean.py (mêmes colonnes,
mêmes valeurs), puis passée au même Preparateur que celui de l'entraînement : le modèle
voit une voiture de l'app comme il a vu les annonces pendant l'entraînement.
"""

import json
import sys
import unicodedata
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from schemas import DemandeEstimation, Equipement, Estimation, Fourchette, Options

ML_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML_DIR / "src" / "model_a"))
from features import Preparateur, charger_modele  # noqa: E402

MODEL_DIR = ML_DIR / "models" / "model_a"
AUTRE = "autre"
PRIX_FAIBLE_FIABILITE = 50_000  # en dessous, erreur moyenne ~22 % sur le test (contre 8-12 % au-dessus)


def normaliser(texte: str) -> str:
    """'  Fès ' -> 'fes', 'Classe  C' -> 'classe c' : comparaison sans accents, casse ni espaces."""
    sans_accents = unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode()
    return " ".join(sans_accents.lower().split())


class PredicteurPrix:
    def __init__(self, dossier: Path = MODEL_DIR):
        self.modele = charger_modele(dossier)
        self.prep = Preparateur.charger(dossier / "preparateur.json")
        self.fiche = json.loads((dossier / "fiche_modele.json").read_text(encoding="utf-8"))
        self.version = self.fiche["version"]
        self.tranches = self.fiche["fourchettes"]["tranches"]
        # Index "forme normalisée -> valeur exacte vue à l'entraînement" pour tolérer
        # les différences de saisie (majuscules, accents) côté app
        self.index = {
            col: {normaliser(v): v for v in self.prep.categories[col]} for col in ("marque", "ville")
        }
        self.index_modeles = {}
        for valeur in self.prep.categories["modele"]:
            marque, modele = valeur.split(" | ", 1)
            self.index_modeles[(normaliser(marque), normaliser(modele))] = valeur

    def _retrouver(self, colonne: str, saisie: str | None) -> str | None:
        return None if saisie is None else self.index[colonne].get(normaliser(saisie))

    def _ligne(self, d: DemandeEstimation) -> tuple[pd.DataFrame, list[str], bool]:
        avertissements, fiable = [], True

        marque = self._retrouver("marque", d.marque)
        modele = self.index_modeles.get((normaliser(d.marque), normaliser(d.modele)))
        if marque is None:
            avertissements.append("Marque peu présente dans les annonces : estimation moins précise.")
            fiable = False
        elif modele is None:
            avertissements.append("Modèle peu présent dans les annonces : estimation basée sur la marque et les caractéristiques.")
            fiable = False
        ville = self._retrouver("ville", d.ville)

        # Âge par rapport à aujourd'hui : une voiture de 7 ans vaut, au niveau de prix 2024,
        # ce qu'une voiture de 7 ans valait dans les annonces 2024.
        age = max(0, date.today().year - d.annee)
        if d.kilometrage is None:
            avertissements.append("Kilométrage non renseigné : estimation moins précise.")

        ligne = {
            "marque": marque or AUTRE,
            "modele": modele or AUTRE,
            "age": age,
            "kilometrage": np.nan if d.kilometrage is None else float(d.kilometrage),
            "km_inconnu": d.kilometrage is None,
            "boite": d.boite.value,
            "puissance_fiscale": np.nan if d.puissance_fiscale is None else float(d.puissance_fiscale),
            "carburant": d.carburant.value,
            "etat": d.etat.value if d.etat else "inconnu",
            "nb_portes": np.nan if d.nb_portes is None else float(d.nb_portes),
            "origine": d.origine.value if d.origine else "inconnu",
            "premiere_main": {True: "oui", False: "non", None: "inconnu"}[d.premiere_main],
            "ville": ville or AUTRE,
            "nb_equipements": len(set(d.equipements)),
        }
        for equipement in Equipement:
            ligne[f"eq_{equipement.value}"] = equipement in d.equipements
        return pd.DataFrame([ligne]), avertissements, fiable

    def _fourchette(self, prix: float) -> Fourchette:
        tranche = next(t for t in reversed(self.tranches) if prix >= t["prix_predit_min"])
        return Fourchette(min=int(round(prix * tranche["facteur_bas"], -3)),
                          max=int(round(prix * tranche["facteur_haut"], -3)))

    def estimer(self, demande: DemandeEstimation) -> Estimation:
        ligne, avertissements, fiable = self._ligne(demande)
        prix = float(np.exp(self.modele.predict(self.prep.transform(ligne))[0]))
        if prix < PRIX_FAIBLE_FIABILITE:
            avertissements.append("Véhicule d'entrée de gamme : le prix dépend beaucoup de l'état réel, "
                                  "à vérifier sur place.")
            fiable = False
        return Estimation(
            prix_estime=int(round(prix, -3)),
            fourchette=self._fourchette(prix),
            fiabilite="normale" if fiable else "reduite",
            avertissements=avertissements,
            version_modele=self.version,
        )

    def options(self) -> Options:
        modeles: dict[str, list[str]] = {}
        for valeur in self.prep.categories["modele"]:
            marque, modele = valeur.split(" | ", 1)
            modeles.setdefault(marque, []).append(modele)
        return Options(
            marques=sorted(modeles),
            modeles_par_marque={m: sorted(v) for m, v in sorted(modeles.items())},
            villes=sorted(self.prep.categories["ville"]),
        )
