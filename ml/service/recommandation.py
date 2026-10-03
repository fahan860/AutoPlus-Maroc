"""
Modèle B dans le service ML : recommandation de garages à partir d'une description de panne.

Réutilise ml/src/model_b/recommandeur.py, le code évalué à l'étape B.2 (même classification
de la panne, mêmes poids). En production, seule la partie « contenu » est utilisée : le
filtrage collaboratif (SVD, étape B.3) a besoin de vrais historiques de RDV, que l'app
n'a pas encore.
"""

import sys
import threading
import time
from datetime import date
from pathlib import Path

ML_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML_DIR / "src" / "model_b"))
from recommandeur import (  # noqa: E402
    MODELE_E5, ClassifieurPannes, EncodeurTexte, charger_depuis_base, recommander,
)

from schemas import (  # noqa: E402
    CategorieProbable, DemandeRecommandation, GarageRecommande, PanneProche, Recommandation,
)

RAFRAICHISSEMENT_GARAGES_S = 600  # nouveaux garages créés par les mécaniciens pris en compte sous 10 min
# En dessous, la catégorie la plus probable n'est pas assez sûre. Mesuré sur les 40 requêtes
# d'évaluation : à 0,5 l'avertissement s'affichait pour 63 % des requêtes (dont « voyant moteur
# allumé », bien classée) ; à 0,35 il garde 4 des 5 erreurs pour 37 % des requêtes.
SEUIL_AMBIGUITE = 0.35
SEUIL_CATEGORIES_AFFICHEES = 0.1

LIBELLES = {
    "moteur": "moteur", "entretien_courant": "entretien", "freins": "freinage", "electrique": "électricité",
    "climatisation": "climatisation", "carrosserie": "carrosserie", "pneus_suspension": "pneus et suspension",
    "transmission": "boîte et embrayage", "direction": "direction", "echappement": "échappement",
}


class ServiceRecommandation:
    def __init__(self, url_base: str):
        self.url_base = url_base
        pannes, self.garages = charger_depuis_base(url_base)
        self.classifieur = ClassifieurPannes(EncodeurTexte(MODELE_E5), pannes)
        self.charge_le = time.monotonic()
        self.verrou = threading.Lock()
        self.version = f"contenu-e5-{date.today().isoformat()}"

    def _garages_a_jour(self):
        if time.monotonic() - self.charge_le > RAFRAICHISSEMENT_GARAGES_S and self.verrou.acquire(blocking=False):
            try:
                _pannes, self.garages = charger_depuis_base(self.url_base)
                self.charge_le = time.monotonic()
            except Exception as err:  # base indisponible : on garde la liste en mémoire
                print(f"Rafraîchissement des garages impossible : {err}")
            finally:
                self.verrou.release()
        return self.garages

    @staticmethod
    def _raisons(reco, probas) -> list[str]:
        g, detail = reco.garage, reco.detail
        couvertes = [c for c, p in probas.items() if p >= SEUIL_CATEGORIES_AFFICHEES and c in g.specialites]
        raisons = []
        if couvertes:
            libelles = ", ".join(LIBELLES.get(c, c) for c in couvertes)
            if g.specialites_source == "hypothese_generaliste":
                raisons.append(f"Mécanique générale ({libelles})")
            else:
                raisons.append(f"Spécialiste {libelles}")
        if detail["distance_km"] is not None:
            raisons.append(f"À {detail['distance_km']:.1f} km".replace(".", ","))
        if g.note is not None and g.nb_avis:
            raisons.append(f"Noté {g.note:.1f}/5 ({g.nb_avis} avis)".replace(".", ",", 1))
        return raisons

    def _garage(self, r, probas) -> GarageRecommande:
        return GarageRecommande(
            id=r.garage.id, nom=r.garage.nom, adresse=r.garage.adresse, telephone=r.garage.telephone,
            distance_km=r.detail["distance_km"], note=r.garage.note, nb_avis=r.garage.nb_avis,
            specialites=r.garage.specialites,
            specialites_confirmees=r.garage.specialites_source != "hypothese_generaliste",
            score=round(r.score, 3), raisons=self._raisons(r, probas),
        )

    def garages_pour(self, probas: dict, lat: float | None, lon: float | None, k: int = 3) -> list[GarageRecommande]:
        """Garages pour des probabilités de catégories déjà calculées (utilisé par l'agent IA)."""
        return [self._garage(r, probas) for r in recommander(probas, self._garages_a_jour(), lat, lon, k=k)]

    def recommander(self, demande: DemandeRecommandation) -> Recommandation:
        probas = self.classifieur.classer(demande.description)
        garages = self._garages_a_jour()
        recos = recommander(probas, garages, demande.lat, demande.lon, k=demande.nb_garages)

        avertissements = []
        meilleure = next(iter(probas.values()))
        if meilleure < SEUIL_AMBIGUITE:
            avertissements.append("Description peu précise : plusieurs types de panne sont possibles. "
                                  "Ajoutez des détails (bruit, voyant, moment où ça arrive) pour affiner.")
        if demande.lat is None:
            avertissements.append("Position inconnue : garages classés sans tenir compte de la distance.")
        if len(recos) < demande.nb_garages:
            # Pas de remplissage avec des garages incapables de traiter la panne
            avertissements.append(f"Seulement {len(recos)} garage{'s' if len(recos) > 1 else ''} référencé"
                                  f"{'s' if len(recos) > 1 else ''} pour ce type de panne pour l'instant.")

        return Recommandation(
            categories_probables=[CategorieProbable(categorie=c, probabilite=round(p, 3))
                                  for c, p in probas.items() if p >= SEUIL_CATEGORIES_AFFICHEES][:3],
            pannes_proches=[
                PanneProche(code=p.code, titre=p.titre, categorie=p.categorie, urgence=p.urgence,
                            cout_min_dh=p.cout_min_dh, cout_max_dh=p.cout_max_dh)
                for p, _sim in self.classifieur.pannes_proches(demande.description, k=2)
            ],
            garages=[self._garage(r, probas) for r in recos],
            avertissements=avertissements,
            version_modele=self.version,
        )
