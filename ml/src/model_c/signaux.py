"""
Modèle C — étape C.2 : signaux (variables) calculés pour chaque avis.

Règle : uniquement l'information disponible AU MOMENT où l'avis est publié (avis
précédents, compte de l'auteur, RDV) — jamais d'information future. Ce même code servira
au service ML, qui note chaque nouvel avis à sa publication.

Signaux comportementaux :
  anciennete_compte_h   âge du compte de l'auteur au moment de l'avis (heures)
  rdv_termine           l'avis suit un RDV terminé via l'app
  rdv_annule            l'avis porte sur un RDV annulé
  avis_garage_48h       avis reçus par le même garage dans les 48 h précédentes (rafales)
  ecart_note            note - moyenne des avis précédents du garage
  note_extreme          note de 1 ou 5
Signaux du texte :
  nb_mots, nb_exclamations, part_majuscules
  nb_superlatifs        « meilleur », « parfait », « wa3er »... ou accusations « arnaque », « voleurs »...
  nb_details_concrets   chiffres, prix, pièces, délais : ce qu'un vrai client raconte
  similarite_max_30j    ressemblance avec le plus proche des avis des 30 derniers jours
                        (n-grammes de caractères, robustes à la darija et aux fautes) ;
                        0 pour les textes de moins de 6 mots (deux « Très bien » ne sont pas suspects)
"""

import re
import unicodedata
from datetime import timedelta

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

MOTS_MIN_SIMILARITE = 6
FENETRE_RAFALE = timedelta(hours=48)
FENETRE_SIMILARITE = timedelta(days=30)
NOTE_A_PRIORI = 4.0  # moyenne supposée d'un garage sans avis précédent

SUPERLATIFS = ["meilleur", "parfait", "incroyable", "excellent", "top", "jamais vu", "les yeux fermes", "100 %",
               "100%", "wa3er", "ahsan", "fonce", "arnaque", "voleur", "fuir", "fuyez", "pire", "nul",
               "chfara", "malhonnete", "incompetent", "evitez"]
DETAILS = ["dh", "dirham", "devis", "frein", "plaquette", "embrayage", "clim", "batterie", "amortisseur",
           "courroie", "diagnostic", "carrosserie", "pneu", "alternateur", "echappement", "direction",
           "disque", "vidange", "revision", "logan", "clio", "208", "duster", "golf", "tucson", "sandero",
           "kangoo", "polo", "corolla", "picanto", "partner", "jour", "heure", "semaine", "rdv", "attente",
           "accueil", "telephone"]

COLONNES = ["anciennete_compte_h", "rdv_termine", "rdv_annule", "avis_garage_48h", "ecart_note", "note_extreme",
            "nb_mots", "nb_exclamations", "part_majuscules", "nb_superlatifs", "nb_details_concrets",
            "similarite_max_30j"]


def normaliser(texte: str) -> str:
    return unicodedata.normalize("NFKD", texte or "").encode("ascii", "ignore").decode().lower()


def compter(texte_norm: str, lexique: list[str]) -> int:
    return sum(len(re.findall(rf"\b{re.escape(m)}", texte_norm)) for m in lexique)


def signaux_texte(texte: str) -> dict:
    texte = texte or ""
    norm = normaliser(texte)
    lettres = [c for c in texte if c.isalpha()]
    return {
        "nb_mots": len(texte.split()),
        "nb_exclamations": texte.count("!"),
        "part_majuscules": sum(c.isupper() for c in lettres) / len(lettres) if lettres else 0.0,
        "nb_superlatifs": compter(norm, SUPERLATIFS),
        "nb_details_concrets": compter(norm, DETAILS) + len(re.findall(r"\d", norm)) // 2,
    }


def calculer(avis: pd.DataFrame, vectoriseur: TfidfVectorizer | None = None) -> tuple[pd.DataFrame, TfidfVectorizer]:
    """avis : colonnes garage_id, compte_cree_le, date, note, commentaire, intervention_statut.
    Retourne les signaux (même index) et le vectoriseur de texte (appris ici si absent)."""
    avis = avis.sort_values("date")
    textes = avis["commentaire"].fillna("").map(normaliser)
    if vectoriseur is None:
        vectoriseur = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=2).fit(textes)
    matrice = vectoriseur.transform(textes)
    dates = avis["date"].to_numpy()
    garages = avis["garage_id"].to_numpy()
    notes = avis["note"].to_numpy(dtype=float)
    nb_mots = textes.str.split().str.len().to_numpy()

    lignes = []
    for i, ligne in enumerate(avis.itertuples()):
        avant = dates < dates[i]
        meme_garage = avant & (garages == garages[i])
        notes_garage = notes[meme_garage]
        recents = np.where(avant & (dates >= dates[i] - np.timedelta64(FENETRE_SIMILARITE)))[0]
        similarite = 0.0
        if nb_mots[i] >= MOTS_MIN_SIMILARITE and len(recents):
            similarite = float((matrice[recents] @ matrice[i].T).max())
        lignes.append({
            "anciennete_compte_h": (ligne.date - ligne.compte_cree_le).total_seconds() / 3600,
            "rdv_termine": int(ligne.intervention_statut == "termine"),
            "rdv_annule": int(ligne.intervention_statut == "annule"),
            "avis_garage_48h": int((meme_garage & (dates >= dates[i] - np.timedelta64(FENETRE_RAFALE))).sum()),
            "ecart_note": notes[i] - (notes_garage.mean() if len(notes_garage) else NOTE_A_PRIORI),
            "note_extreme": int(notes[i] in (1, 5)),
            **signaux_texte(ligne.commentaire),
            "similarite_max_30j": similarite,
        })
    return pd.DataFrame(lignes, index=avis.index)[COLONNES], vectoriseur
