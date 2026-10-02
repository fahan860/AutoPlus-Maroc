"""
Modèle C dans le service ML : vérification d'un avis au moment de sa publication.

Le service relit en base l'avis et son contexte (historique du garage, avis des 30 derniers
jours, compte de l'auteur, RDV lié), calcule les signaux avec le même code qu'à
l'entraînement (ml/src/model_c/signaux.py) et décide :
  publier  : rien de suspect
  verifier : masquer en attendant un admin (gradient boosting au-dessus du seuil, ou avis
             sur un RDV annulé)
Les raisons renvoyées sont lisibles par l'admin qui tranche.
"""

import json
import sys
from pathlib import Path

import joblib
import pandas as pd
import psycopg2

ML_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ML_DIR / "src" / "model_c"))
import signaux  # noqa: E402

MODEL_DIR = ML_DIR / "models" / "model_c"

REQUETE_AVIS = """
    SELECT r.id, r.garage_id, r.note::float AS note, r.commentaire, r.created_at AS date,
           u.created_at AS compte_cree_le, i.statut AS intervention_statut
    FROM reviews r
    JOIN users u ON u.id = r.user_id
    LEFT JOIN interventions i ON i.id = r.intervention_id
"""


class ServiceModeration:
    def __init__(self, url_base: str, dossier: Path = MODEL_DIR):
        self.url_base = url_base
        self.modele = joblib.load(dossier / "gradient_boosting.joblib")
        self.vectoriseur = joblib.load(dossier / "vectoriseur.joblib")
        fiche = json.loads((dossier / "fiche_modele.json").read_text(encoding="utf-8"))
        self.seuil = fiche["seuil_gradient_boosting"]
        self.version = f"faux-avis-{fiche['version']}"

    def _contexte(self, review_id: int) -> pd.DataFrame:
        """L'avis + tout ce qui était connu au moment de sa publication."""
        with psycopg2.connect(self.url_base) as conn:
            cible = pd.read_sql(REQUETE_AVIS + " WHERE r.id = %(id)s", conn, params={"id": review_id})
            if cible.empty:
                raise LookupError(f"Avis {review_id} introuvable")
            contexte = pd.read_sql(
                REQUETE_AVIS + """
                WHERE r.id <> %(id)s AND r.created_at <= %(date)s
                  AND (r.garage_id = %(garage)s OR r.created_at >= %(date)s - interval '30 days')""",
                conn, params={"id": review_id, "date": cible.loc[0, "date"], "garage": int(cible.loc[0, "garage_id"])},
            )
        return pd.concat([contexte, cible], ignore_index=True)

    @staticmethod
    def _raisons(s: pd.Series) -> list[str]:
        raisons = []
        if s["rdv_annule"]:
            raisons.append("Avis sur un RDV annulé")
        elif not s["rdv_termine"]:
            raisons.append("Aucun RDV terminé avec ce garage")
        if s["anciennete_compte_h"] < 24:
            raisons.append("Compte créé il y a moins de 24 h")
        elif s["anciennete_compte_h"] < 24 * 7:
            raisons.append("Compte créé il y a moins d'une semaine")
        if s["avis_garage_48h"] >= 2:
            raisons.append(f"{int(s['avis_garage_48h'])} autres avis reçus par ce garage en 48 h")
        if abs(s["ecart_note"]) >= 2.5:
            raisons.append("Note très éloignée de la moyenne du garage")
        if s["similarite_max_30j"] >= 0.9:
            raisons.append("Texte quasi identique à un autre avis récent")
        if s["nb_superlatifs"] >= 2:
            raisons.append("Formulations excessives (superlatifs ou accusations)")
        if s["nb_mots"] >= 6 and s["nb_details_concrets"] == 0:
            raisons.append("Aucun détail concret sur la réparation")
        return raisons

    def evaluer(self, review_id: int) -> dict:
        avis = self._contexte(review_id)
        X, _ = signaux.calculer(avis, self.vectoriseur)
        ligne = X.loc[avis.index[avis["id"] == review_id]]
        score = float(self.modele.predict_proba(signaux.transformer(ligne))[0, 1])
        s = ligne.iloc[0]
        a_verifier = score >= self.seuil or bool(s["rdv_annule"])
        return {
            "review_id": review_id,
            "decision": "verifier" if a_verifier else "publier",
            "score": round(score, 3),
            "raisons": self._raisons(s) if a_verifier else [],
            "version_modele": self.version,
        }
