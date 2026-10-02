"""
Modèle B — étape B.2 : évaluation de la recommandation par contenu.

1. Classification de la panne (40 requêtes écrites à la main, requetes_evaluation.json) :
   e5-large (modèle retenu pour l'Agent IA) vs MiniLM multilingue (modèle précédent)
   vs recherche par mots-clés. Mesures : top-1, top-3, MRR.
2. Classement des garages, pour chaque requête depuis 5 quartiers de Casablanca :
   recommandation hybride vs « garage le plus proche » vs « spécialité seule ».
   Mesures : part du top 5 qui traite la bonne catégorie, spécialiste confirmé en
   1re position, distance moyenne du top 5.

Limite : la pertinence d'un garage est jugée avec les spécialités en base, qui sont pour
la plupart une hypothèse (« mécanique générale ») — la partie 2 mesure surtout le compromis
pertinence / distance, pas la qualité réelle des garages.

Sorties : ml/reports/model_b_evaluation.json, ml/reports/figures/b2_*.png
Usage : ml/venv/Scripts/python ml/src/model_b/evaluate.py
"""

import json
import re
import sys
import unicodedata

import truststore

truststore.inject_into_ssl()

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from recommandeur import (
    MODELE_E5, POIDS, ClassifieurPannes, EncodeurTexte, ML_DIR, ROOT, charger_depuis_base, distance_km, recommander,
)

sys.path.insert(0, str(ROOT / "data" / "scraping"))
from enrich_garages import MOTS_CLES  # noqa: E402  mêmes mots-clés que pour les spécialités des garages

MODELE_MINILM = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
REQUETES = json.loads((ML_DIR / "src" / "model_b" / "requetes_evaluation.json").read_text(encoding="utf-8"))["requetes"]
REPORT_PATH = ML_DIR / "reports" / "model_b_evaluation.json"
FIG_DIR = ML_DIR / "reports" / "figures"

# Points de départ réels (centre approximatif de quartiers de Casablanca)
POSITIONS = {
    "Maârif": (33.5822, -7.6327),
    "Aïn Sebaâ": (33.6050, -7.5330),
    "Hay Hassani": (33.5560, -7.6750),
    "Sidi Maârouf": (33.5330, -7.6450),
    "Centre (Mers Sultan)": (33.5870, -7.6110),
}


def normaliser(texte):
    return " ".join(unicodedata.normalize("NFKD", texte).encode("ascii", "ignore").decode().lower().split())


def classement_mots_cles(texte: str, categories: list[str]) -> list[str]:
    """Référence naïve : catégories triées par nombre de mots-clés trouvés dans la requête."""
    t = normaliser(texte)
    compte = {c: sum(bool(re.search(rf"\b{re.escape(m)}", t)) for m in MOTS_CLES.get(c, [])) for c in categories}
    return [c for c, n in sorted(compte.items(), key=lambda kv: -kv[1]) if n > 0]


def mesures_classification(classements: list[list[str]], attendues: list[str]) -> dict:
    rangs = [cl.index(a) + 1 if a in cl else None for cl, a in zip(classements, attendues)]
    return {
        "top1_pct": 100 * np.mean([r == 1 for r in rangs]),
        "top3_pct": 100 * np.mean([r is not None and r <= 3 for r in rangs]),
        "MRR": float(np.mean([1 / r if r else 0 for r in rangs])),
    }


def evaluer_classification(pannes):
    attendues = [r["categorie"] for r in REQUETES]
    textes = [r["texte"] for r in REQUETES]
    resultats, classifieurs = {}, {}
    for nom, modele in [("e5-large (retenu)", MODELE_E5), ("MiniLM multilingue", MODELE_MINILM)]:
        clf = ClassifieurPannes(EncodeurTexte(modele), pannes)
        vecteurs = clf.encodeur.requetes(textes)
        classements = [list(clf.probabilites(v)) for v in vecteurs]
        resultats[nom] = {**mesures_classification(classements, attendues), "classements": classements}
        classifieurs[nom] = clf
    categories = classifieurs["e5-large (retenu)"].categories
    resultats["Mots-clés"] = {
        **mesures_classification([classement_mots_cles(t, categories) for t in textes], attendues),
        "classements": [classement_mots_cles(t, categories) for t in textes],
    }
    return resultats, classifieurs["e5-large (retenu)"]


def evaluer_classement(clf, garages):
    vecteurs = clf.encodeur.requetes([r["texte"] for r in REQUETES])
    strategies = {
        "Hybride (Modèle B)": POIDS,
        "Spécialité seule": {"specialite": 1.0, "distance": 0.0, "note": 0.0},
    }
    # Catégories pour lesquelles au moins un spécialiste confirmé (non hypothétique) existe
    confirmees = {c for g in garages if g.specialites_source != "hypothese_generaliste" for c in g.specialites}
    lignes = {nom: {"pertinence_top5": [], "specialiste_top1": [], "distance_top5": [], "premiers": []}
              for nom in [*strategies, "Plus proche"]}

    for requete, vecteur in zip(REQUETES, vecteurs):
        attendue = requete["categorie"]
        probas = clf.probabilites(vecteur)
        for lat, lon in POSITIONS.values():
            tops = {nom: [r.garage for r in recommander(probas, garages, lat, lon, k=5, poids=p)]
                    for nom, p in strategies.items()}
            localises = [g for g in garages if g.lat is not None]
            tops["Plus proche"] = sorted(localises, key=lambda g: distance_km(lat, lon, g.lat, g.lon))[:5]
            for nom, top in tops.items():
                lignes[nom]["premiers"].append(top[0].id)
                lignes[nom]["pertinence_top5"].append(np.mean([attendue in g.specialites for g in top]))
                if attendue in confirmees:
                    premier = top[0]
                    lignes[nom]["specialiste_top1"].append(
                        attendue in premier.specialites and premier.specialites_source != "hypothese_generaliste")
                distances = [distance_km(lat, lon, g.lat, g.lon) for g in top if g.lat is not None]
                if distances:
                    lignes[nom]["distance_top5"].append(np.mean(distances))

    return {nom: {
        "pertinence_top5_pct": 100 * float(np.mean(v["pertinence_top5"])),
        "specialiste_confirme_top1_pct": 100 * float(np.mean(v["specialiste_top1"])),
        "distance_moyenne_top5_km": float(np.mean(v["distance_top5"])),
        # Garde-fou : un recommandeur qui envoie tout le monde au même garage est inutile
        "garages_differents_en_1er": len(set(v["premiers"])),
        "part_du_garage_le_plus_recommande_pct": 100 * max(np.unique(v["premiers"], return_counts=True)[1]) / len(v["premiers"]),
    } for nom, v in lignes.items()}, sorted(confirmees)


def figure_classification(resultats):
    noms = list(resultats)
    x = np.arange(len(noms))
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, (mesure, libelle) in enumerate([("top1_pct", "Bonne catégorie en 1er"), ("top3_pct", "Bonne catégorie dans le top 3")]):
        valeurs = [resultats[n][mesure] for n in noms]
        barres = ax.bar(x + (i - 0.5) * 0.38, valeurs, 0.38, label=libelle, color=["#4C72B0", "#9DB4D6"][i])
        ax.bar_label(barres, fmt="%.0f %%", fontsize=8)
    ax.set_xticks(x, noms)
    ax.set_ylim(0, 110)
    ax.set_ylabel("% des 40 requêtes")
    ax.set_title("Classification de la panne à partir de la description de l'utilisateur")
    ax.legend(loc="upper right", fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "b2_classification_pannes.png", dpi=110)


def main():
    pannes, garages = charger_depuis_base()
    print(f"{len(pannes)} pannes, {len(garages)} garages, {len(REQUETES)} requêtes d'évaluation\n")

    classification, clf = evaluer_classification(pannes)
    print("1. Classification de la panne")
    for nom, m in classification.items():
        print(f"   {nom:<22} top-1 {m['top1_pct']:5.1f} % | top-3 {m['top3_pct']:5.1f} % | MRR {m['MRR']:.3f}")

    erreurs = [
        {"texte": r["texte"], "attendue": r["categorie"], "predite": cl[0] if cl else None}
        for r, cl in zip(REQUETES, classification["e5-large (retenu)"]["classements"]) if not cl or cl[0] != r["categorie"]
    ]
    print(f"\n   Erreurs top-1 d'e5-large ({len(erreurs)}) :")
    for e in erreurs:
        print(f"   - « {e['texte']} » : attendu {e['attendue']}, prédit {e['predite']}")

    classement, confirmees = evaluer_classement(clf, garages)
    print(f"\n2. Classement des garages ({len(REQUETES)} requêtes × {len(POSITIONS)} quartiers)")
    for nom, m in classement.items():
        print(f"   {nom:<20} pertinents dans le top 5 {m['pertinence_top5_pct']:5.1f} % | "
              f"spécialiste confirmé en 1er {m['specialiste_confirme_top1_pct']:5.1f} % | "
              f"distance moyenne {m['distance_moyenne_top5_km']:.1f} km | "
              f"{m['garages_differents_en_1er']} garages différents en 1er "
              f"(le plus fréquent : {m['part_du_garage_le_plus_recommande_pct']:.0f} %)")

    figure_classification(classification)
    for m in classification.values():
        m.pop("classements")
    REPORT_PATH.write_text(json.dumps({
        "requetes": len(REQUETES), "positions": POSITIONS, "poids": POIDS,
        "classification_pannes": classification, "erreurs_e5": erreurs,
        "classement_garages": classement, "categories_avec_specialiste_confirme": confirmees,
    }, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
