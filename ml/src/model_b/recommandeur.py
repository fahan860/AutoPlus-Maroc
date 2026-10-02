"""
Modèle B — recommandation de garages, partie « contenu » (étape B.2).

Pour une description de panne en langage naturel et une position :
  1. Classification de la panne : la requête est comparée (embeddings) aux 50 pannes de
     base_pannes ; on en déduit une probabilité par catégorie (moteur, freins...).
  2. Score de spécialité de chaque garage : somme des probabilités des catégories qu'il
     couvre, pondérée par la fiabilité de l'information (spécialité confirmée ou simple
     hypothèse « mécanique générale »).
  3. Score final = spécialité, distance et note, pondérées (POIDS).

Partagé par evaluate.py (mesures) et, plus tard, par le service ML.
"""

import math
import os
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ML_DIR = Path(__file__).resolve().parents[2]
ROOT = ML_DIR.parent

MODELE_E5 = "intfloat/multilingual-e5-large"

# Avec 0,6 / 0,3 / 0,1 et une confiance de 0,6 pour les généralistes, le seul garage dont la
# fiche liste les 10 spécialités (M.I.A) sortait 1er dans 100 % des cas, même à 10 km.
# Choix après une grille de 9 réglages (evaluate.py) : 0,4 / 0,5 / 0,1 garde 67 % de garages
# pertinents dans le top 5 (-3 points vs 0,5 / 0,4), à 1,3 km en moyenne, et aucun garage ne
# capte plus de 20 % des 1res places (contre 52 %).
POIDS = {"specialite": 0.4, "distance": 0.5, "note": 0.1}
# Fiabilité de l'information « ce garage traite cette catégorie », selon sa source.
# Un garage de mécanique générale est réellement compétent pour l'entretien, les freins,
# le moteur... : l'hypothèse est peu pénalisée.
CONFIANCE_SOURCE = {"declaree": 1.0, "fiche_telecontact": 1.0, "nom": 1.0, "hypothese_generaliste": 0.8}
# Score de distance = exp(-d / DISTANCE_CARACTERISTIQUE_KM) : 1 sur place, ~0,37 à 5 km, ~0,14 à 10 km
DISTANCE_CARACTERISTIQUE_KM = 5.0
SCORE_DISTANCE_INCONNUE = 0.2  # garage sans GPS : ni favorisé, ni exclu
# Note bayésienne : moyenne tirée vers NOTE_A_PRIORI tant qu'il y a peu d'avis
NOTE_A_PRIORI, POIDS_A_PRIORI = 3.5, 5
# Température du softmax qui transforme les similarités (très resserrées avec e5,
# ~0,75-0,90) en probabilités de catégories
TEMPERATURE = 0.02


def texte_panne(titre: str, symptomes: list[str]) -> str:
    """Même construction que data/pannes/load_embeddings.py (titre + symptômes)."""
    return ". ".join([titre, *symptomes])


@dataclass
class Panne:
    code: str
    categorie: str
    titre: str
    texte: str


@dataclass
class Garage:
    id: int
    nom: str
    adresse: str | None
    lat: float | None
    lon: float | None
    note: float | None
    nb_avis: int
    specialites: list[str]
    specialites_source: str
    telephone: str | None = None


@dataclass
class Recommandation:
    garage: Garage
    score: float
    detail: dict = field(default_factory=dict)


def charger_depuis_base() -> tuple[list[Panne], list[Garage]]:
    import psycopg2
    from dotenv import load_dotenv

    load_dotenv(ROOT / "api" / ".env")
    with psycopg2.connect(os.environ["DATABASE_URL"]) as conn, conn.cursor() as cur:
        cur.execute("SELECT code, categorie, titre, symptomes FROM base_pannes ORDER BY code")
        pannes = [Panne(c, cat, t, texte_panne(t, s)) for c, cat, t, s in cur.fetchall()]
        cur.execute("""
            SELECT id, nom, adresse, ST_Y(geom::geometry), ST_X(geom::geometry), note, nb_avis,
                   specialites, specialites_source, telephone
            FROM garages WHERE specialites IS NOT NULL ORDER BY id""")
        garages = [Garage(i, n, a, la, lo, float(no) if no is not None else None, nb or 0, sp, src, tel)
                   for i, n, a, la, lo, no, nb, sp, src, tel in cur.fetchall()]
    return pannes, garages


class EncodeurTexte:
    """Encapsule un modèle sentence-transformers et ses conventions de préfixes
    (les modèles E5 attendent "query: " pour les requêtes et "passage: " pour les documents)."""

    def __init__(self, nom_modele: str):
        from sentence_transformers import SentenceTransformer

        self.nom = nom_modele
        self.modele = SentenceTransformer(nom_modele)
        self.e5 = "e5" in nom_modele.lower()

    def documents(self, textes: list[str]) -> np.ndarray:
        textes = [f"passage: {t}" for t in textes] if self.e5 else textes
        return self.modele.encode(textes, normalize_embeddings=True)

    def requetes(self, textes: list[str]) -> np.ndarray:
        textes = [f"query: {t}" for t in textes] if self.e5 else textes
        return self.modele.encode(textes, normalize_embeddings=True)


class ClassifieurPannes:
    def __init__(self, encodeur: EncodeurTexte, pannes: list[Panne]):
        self.encodeur = encodeur
        self.pannes = pannes
        self.vecteurs = encodeur.documents([p.texte for p in pannes])
        self.categories = sorted({p.categorie for p in pannes})
        self.index_cat = np.array([self.categories.index(p.categorie) for p in pannes])

    def probabilites(self, vecteur_requete: np.ndarray) -> dict[str, float]:
        """Probabilité de chaque catégorie : similarité de la panne la plus proche de la
        catégorie, passée dans un softmax."""
        similarites = self.vecteurs @ vecteur_requete
        meilleures = np.array([similarites[self.index_cat == i].max() for i in range(len(self.categories))])
        exp = np.exp((meilleures - meilleures.max()) / TEMPERATURE)
        probas = exp / exp.sum()
        return dict(sorted(zip(self.categories, probas.tolist()), key=lambda kv: -kv[1]))

    def classer(self, texte: str) -> dict[str, float]:
        return self.probabilites(self.encodeur.requetes([texte])[0])

    def pannes_proches(self, texte: str, k: int = 3) -> list[tuple[Panne, float]]:
        similarites = self.vecteurs @ self.encodeur.requetes([texte])[0]
        return [(self.pannes[i], float(similarites[i])) for i in np.argsort(-similarites)[:k]]


def distance_km(lat1, lon1, lat2, lon2) -> float:
    """Distance à vol d'oiseau (formule de haversine)."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def note_bayesienne(garage: Garage) -> float:
    n = garage.nb_avis if garage.note is not None else 0
    note = garage.note or 0.0
    return (n * note + POIDS_A_PRIORI * NOTE_A_PRIORI) / (n + POIDS_A_PRIORI)


def score_specialite(garage: Garage, probas: dict[str, float]) -> float:
    couverte = sum(p for cat, p in probas.items() if cat in garage.specialites)
    return couverte * CONFIANCE_SOURCE.get(garage.specialites_source, 0.6)


def recommander(probas: dict[str, float], garages: list[Garage], lat: float | None, lon: float | None,
                k: int = 5, poids: dict = POIDS) -> list[Recommandation]:
    resultats = [r for r in scorer(probas, garages, lat, lon, poids) if r.detail["specialite"] > 0]
    resultats.sort(key=lambda r: -r.score)
    return resultats[:k]


def scorer(probas: dict[str, float], garages: list[Garage], lat: float | None, lon: float | None,
           poids: dict = POIDS) -> list[Recommandation]:
    """Score de contenu de chaque garage (non trié, y compris ceux qui ne traitent aucune
    des catégories probables : leur score de spécialité vaut alors 0)."""
    resultats = []
    for g in garages:
        spec = score_specialite(g, probas)
        if lat is not None and g.lat is not None:
            d = distance_km(lat, lon, g.lat, g.lon)
            s_dist = math.exp(-d / DISTANCE_CARACTERISTIQUE_KM)
        else:
            d, s_dist = None, SCORE_DISTANCE_INCONNUE
        s_note = note_bayesienne(g) / 5
        score = poids["specialite"] * spec + poids["distance"] * s_dist + poids["note"] * s_note
        resultats.append(Recommandation(g, score, {
            "specialite": round(spec, 3), "distance_km": None if d is None else round(d, 1),
            "score_distance": round(s_dist, 3), "note": round(note_bayesienne(g), 2),
        }))
    return resultats
