"""
Modèle C (détection de faux avis) — étape C.1 : simulation d'avis sur les garages.

L'app n'a encore aucun avis : on simule 12 mois d'avis sur les 123 vrais garages, en
français et en darija (écrite en lettres latines, comme sur WhatsApp). Les DONNÉES SONT
SIMULÉES : elles servent à construire et comparer les méthodes, pas à mesurer une
performance réelle. Toutes les règles sont ci-dessous, pour être citées dans le rapport.

Avis authentiques (~85 %) :
  - laissés par des clients aux comptes d'âge varié, 75 % après un RDV terminé via l'app
    (25 % sans RDV : clients venus directement au garage) ;
  - notes réalistes (surtout 4-5, mais aussi des avis négatifs argumentés) ;
  - textes souvent concrets (réparation, prix, délai), mais 20 % sont courts et
    génériques (« Très bien », « mzyan ») — ils ressemblent à des faux.

Faux avis (~15 %), 4 types :
  - auto_promotion : le garage se fait mettre 5★ par des proches ; comptes récents, pas de
    RDV, superlatifs, souvent plusieurs avis en quelques jours.
  - denigrement : un concurrent met 1★ ; accusations vagues, comptes récents, pas de RDV.
  - ferme_avis : « ferme » d'avis payés ; rafale de 4 à 8 avis 5★ en moins de 48 h sur le
    même garage, textes quasi identiques (même modèle légèrement modifié).
  - sophistique : faux avis soignés (texte concret, note 4★, compte ancien, parfois un RDV
    annulé) — présent UNIQUEMENT dans les 3 derniers mois (jeu de test) pour mesurer la
    détection d'une fraude jamais vue à l'entraînement.
  Bruit : 20 % des faux avis (hors ferme) viennent de comptes anciens.

Sortie : ml/data/simulated/avis.parquet (local, non versionné)
Usage  : ml/venv/Scripts/python ml/src/model_c/simulate_avis.py
"""

import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

ML_DIR = Path(__file__).resolve().parents[2]
SORTIE = ML_DIR / "data" / "simulated" / "avis.parquet"

GRAINE = 42
DEBUT = datetime(2025, 10, 1)
NB_JOURS = 365
DEBUT_TEST = DEBUT + timedelta(days=NB_JOURS - 91)  # 3 derniers mois
NB_AVIS_AUTHENTIQUES = 2600

# ─── Fragments de texte ──────────────────────────────────────────────────────

REPARATIONS = ["la vidange", "les plaquettes de frein", "l'embrayage", "la clim", "la batterie", "les amortisseurs",
               "la courroie de distribution", "le diagnostic", "la carrosserie de la portière", "les pneus",
               "l'alternateur", "le pot d'échappement", "la direction", "les disques de frein", "la révision"]
VOITURES = ["ma Logan", "ma Clio", "ma 208", "mon Duster", "ma Golf", "mon Tucson", "ma Sandero", "mon Kangoo",
            "ma Polo", "ma Corolla", "ma Picanto", "mon Partner"]
PRENOMS = ["Hassan", "Youssef", "Mustapha", "Rachid", "Karim", "Abdellah", "Said", "Omar"]

AUTHENTIQUE_POSITIF = [
    "J'ai fait {rep} sur {voit}, travail propre et rapide. {prix} DH, prix correct.",
    "{prenom} a bien expliqué le problème avant de toucher à {rep}. Voiture prête le jour même.",
    "Bon garage, {rep} changé en {delai}. Un peu d'attente mais résultat sérieux.",
    "Khdma mzyana f {rep}, {prix} DH. Tbarkellah 3la {prenom}, nsse7kom bih.",
    "Ils ont réglé {rep} de {voit} alors qu'un autre garage n'avait pas trouvé. Je reviendrai.",
    "Prix annoncé = prix payé ({prix} DH) pour {rep}. Rare, merci.",
    "Accueil correct, {rep} fait en {delai}. Je conseille de prendre RDV avant.",
    "Lmo3allim {prenom} m3ellem f {rep}, {voit} wllat mzyana. Ghir chwiya ghali.",
]
AUTHENTIQUE_NEGATIF = [
    "Trois jours pour {rep} alors qu'on m'avait dit une journée. Et {prix} DH au lieu du devis.",
    "{rep} mal faite, le bruit est revenu après une semaine. J'ai dû y retourner.",
    "Personne ne répond au téléphone et {rep} n'était pas prête au rendez-vous.",
    "Twal bzaf f {rep}, w zadou f lprix. Ma3jbnich.",
    "Le travail sur {rep} est correct mais l'accueil laisse à désirer, on m'a fait attendre 2 h.",
]
AUTHENTIQUE_COURT = ["Très bien", "Bon service", "Mzyan", "Correct", "Rapide et efficace", "Je recommande",
                     "Pas mal", "Top", "Service moyen", "Bien"]

PROMOTION = [
    "Le meilleur garage de Casablanca !!! Je recommande à 100 % !!!",
    "Excellent excellent excellent, des professionnels au top, allez-y les yeux fermés !",
    "Wa3er bzaf, ahsan garage f Casa !!! Nsse7kom bih 100 %",
    "Service parfait, équipe parfaite, prix parfaits. 5 étoiles méritées !!!",
    "Incroyable, je n'ai jamais vu un garage aussi professionnel. Bravo à toute l'équipe !!",
    "Top top top, le meilleur, rien à dire, foncez !!!",
]
DENIGREMENT = [
    "Arnaque totale, à fuir absolument !!!",
    "Des voleurs, ne mettez jamais votre voiture chez eux.",
    "Chfara, ma tmchiwch 3ndhom !!!",
    "Pire garage de Casablanca, incompétents et malhonnêtes.",
    "Fuyez !!! Ils cassent plus qu'ils ne réparent.",
    "Nul nul nul, aucune confiance, évitez ce garage.",
]
FERME_MODELES = [
    "Très bon garage, service rapide et personnel accueillant, je recommande vivement",
    "Garage sérieux et professionnel, travail de qualité, prix raisonnables, je recommande",
]
SOPHISTIQUE = [
    "J'ai fait {rep} sur {voit} le mois dernier, {prenom} a été clair sur le devis ({prix} DH). Délai respecté, je reviendrai pour la révision.",
    "Bonne expérience pour {rep} : diagnostic expliqué, {prix} DH, voiture rendue lavée. Petit bémol sur l'attente à l'accueil.",
    "Deuxième fois que je viens pour {voit}, cette fois pour {rep}. Toujours sérieux, {prix} DH, rien à redire.",
]


def remplir(modele: str, rng) -> str:
    return modele.format(
        rep=rng.choice(REPARATIONS), voit=rng.choice(VOITURES), prenom=rng.choice(PRENOMS),
        prix=int(rng.choice([250, 300, 450, 600, 800, 1200, 1500, 2200])), delai=rng.choice(["2 h", "une demi-journée", "un jour"]),
    )


def variante(texte: str, rng) -> str:
    """Petites modifications d'un texte de ferme d'avis (pour éviter le copier-coller exact)."""
    mots = texte.split()
    if rng.random() < 0.5:
        i = rng.integers(len(mots))
        mots[i] = rng.choice(["vraiment", "très", "super", "bon", "top"])
    fin = rng.choice(["", " !", " !!", ".", " 👍"])
    return " ".join(mots) + fin


# ─── Simulation ──────────────────────────────────────────────────────────────


class Simulateur:
    def __init__(self, garage_ids: list[int], rng):
        self.rng = rng
        self.garages = garage_ids
        self.lignes = []
        self.prochain_user = 1
        # Les meilleurs garages reçoivent plus d'avis (popularité variable)
        self.popularite = rng.pareto(1.5, len(garage_ids)) + 0.2
        self.qualite = rng.normal(0, 0.6, len(garage_ids))

    def nouveau_compte(self, date_avis: datetime, recent: bool) -> tuple[int, datetime]:
        uid = self.prochain_user
        self.prochain_user += 1
        if recent:
            age = timedelta(hours=float(self.rng.uniform(0.2, 96)))
        else:
            age = timedelta(days=float(self.rng.uniform(10, 700)))
        return uid, date_avis - age

    def ajouter(self, **ligne):
        self.lignes.append(ligne)

    def date_aleatoire(self, debut=DEBUT, jours=NB_JOURS) -> datetime:
        return debut + timedelta(seconds=float(self.rng.uniform(0, jours * 86400)))

    def authentiques(self):
        p = self.popularite / self.popularite.sum()
        for _ in range(NB_AVIS_AUTHENTIQUES):
            g = self.rng.choice(len(self.garages), p=p)
            date = self.date_aleatoire()
            uid, cree = self.nouveau_compte(date, recent=self.rng.random() < 0.08)
            note = int(np.clip(np.round(4.1 + self.qualite[g] + self.rng.normal(0, 0.9)), 1, 5))
            u = self.rng.random()
            if u < 0.20:
                texte = self.rng.choice(AUTHENTIQUE_COURT)
            elif note <= 2:
                texte = remplir(self.rng.choice(AUTHENTIQUE_NEGATIF), self.rng)
            else:
                texte = remplir(self.rng.choice(AUTHENTIQUE_POSITIF), self.rng)
            rdv = self.rng.random() < 0.75
            self.ajouter(garage_id=self.garages[g], user_id=uid, compte_cree_le=cree, date=date, note=note,
                         commentaire=texte, intervention_statut="termine" if rdv else None,
                         faux=False, type_fraude="authentique")

    def auto_promotion(self, nb_campagnes=60):
        for _ in range(nb_campagnes):
            g = self.rng.integers(len(self.garages))
            debut = self.date_aleatoire(jours=NB_JOURS - 5)
            for _ in range(self.rng.integers(1, 4)):
                date = debut + timedelta(hours=float(self.rng.uniform(0, 96)))
                uid, cree = self.nouveau_compte(date, recent=self.rng.random() > 0.2)
                self.ajouter(garage_id=self.garages[g], user_id=uid, compte_cree_le=cree, date=date,
                             note=5 if self.rng.random() < 0.9 else 4, commentaire=self.rng.choice(PROMOTION),
                             intervention_statut=None, faux=True, type_fraude="auto_promotion")

    def denigrement(self, nb=110):
        for _ in range(nb):
            g = self.rng.integers(len(self.garages))
            date = self.date_aleatoire()
            uid, cree = self.nouveau_compte(date, recent=self.rng.random() > 0.2)
            self.ajouter(garage_id=self.garages[g], user_id=uid, compte_cree_le=cree, date=date,
                         note=1 if self.rng.random() < 0.85 else 2, commentaire=self.rng.choice(DENIGREMENT),
                         intervention_statut=None, faux=True, type_fraude="denigrement")

    def ferme_avis(self, nb_rafales=20, jusqu_a=NB_JOURS):
        for _ in range(nb_rafales):
            g = self.rng.integers(len(self.garages))
            debut = self.date_aleatoire(jours=jusqu_a - 3)
            modele = self.rng.choice(FERME_MODELES)
            for _ in range(self.rng.integers(4, 9)):
                date = debut + timedelta(hours=float(self.rng.uniform(0, 48)))
                uid, cree = self.nouveau_compte(date, recent=True)
                self.ajouter(garage_id=self.garages[g], user_id=uid, compte_cree_le=cree, date=date, note=5,
                             commentaire=variante(modele, self.rng), intervention_statut=None,
                             faux=True, type_fraude="ferme_avis")

    def sophistique(self, nb=45):
        for _ in range(nb):
            g = self.rng.integers(len(self.garages))
            date = self.date_aleatoire(debut=DEBUT_TEST, jours=91)
            uid, cree = self.nouveau_compte(date, recent=False)
            self.ajouter(garage_id=self.garages[g], user_id=uid, compte_cree_le=cree, date=date,
                         note=4 if self.rng.random() < 0.7 else 5, commentaire=remplir(self.rng.choice(SOPHISTIQUE), self.rng),
                         intervention_statut="annule" if self.rng.random() < 0.4 else None,
                         faux=True, type_fraude="sophistique")


def garages_reels() -> list[int]:
    import psycopg2
    from dotenv import load_dotenv

    load_dotenv(ML_DIR.parent / "api" / ".env")
    with psycopg2.connect(os.environ["DATABASE_URL"]) as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM garages ORDER BY id")
        return [r[0] for r in cur.fetchall()]


def main():
    sim = Simulateur(garages_reels(), np.random.default_rng(GRAINE))
    sim.authentiques()
    sim.auto_promotion()
    sim.denigrement()
    sim.ferme_avis()
    sim.sophistique()
    avis = pd.DataFrame(sim.lignes).sort_values("date").reset_index(drop=True)
    avis.insert(0, "avis_id", range(1, len(avis) + 1))
    avis["jeu"] = np.where(avis["date"] >= DEBUT_TEST, "test", "entrainement")

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    avis.to_parquet(SORTIE, index=False)
    print(f"{len(avis)} avis simulés sur {avis.garage_id.nunique()} garages, {avis.faux.mean():.1%} de faux")
    print(pd.crosstab(avis.type_fraude, avis.jeu, margins=True).to_string())


if __name__ == "__main__":
    main()
