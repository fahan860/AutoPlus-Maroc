"""
Semaine 4 du stage — charge pannes_seed.json, genere les embeddings
(sentence-transformers, intfloat/multilingual-e5-large, 1024 dims) et
upsert dans base_pannes (par code). A executer apres schema.sql.

Usage : python data/pannes/load_embeddings.py
Necessite DATABASE_URL dans l'environnement (voir api/.env).
"""

import json
import os
import sys
from pathlib import Path

import truststore

truststore.inject_into_ssl()  # utilise le magasin de certificats Windows (contourne
# l'interception TLS d'Avast, cf. ml/README.md) au lieu du bundle certifi statique.

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

load_dotenv(ROOT / "api" / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    print(
        "DATABASE_URL introuvable (attendu dans api/.env). "
        "Je ne devine jamais des identifiants : merci de le renseigner puis relancer.",
        file=sys.stderr,
    )
    sys.exit(1)

MODEL_NAME = "intfloat/multilingual-e5-large"
SEED_PATH = HERE / "pannes_seed.json"


def build_text(panne: dict) -> str:
    """Texte source de l'embedding : titre + toutes les formulations symptomes,
    pour maximiser le rappel sur des requetes utilisateur variees. Prefixe
    "passage: " requis par les modeles E5 (asymetrie requete/document)."""
    parts = [panne["titre"], *panne["symptomes"]]
    return "passage: " + ". ".join(parts)


def to_vector_literal(embedding) -> str:
    return "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"


def main():
    import psycopg2
    from sentence_transformers import SentenceTransformer

    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)
    pannes = data["pannes"]
    print(f"{len(pannes)} pannes chargees depuis {SEED_PATH.name}")

    print(f"Chargement du modele {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    texts = [build_text(p) for p in pannes]
    print("Generation des embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            for panne, embedding in zip(pannes, embeddings):
                cur.execute(
                    """
                    INSERT INTO base_pannes (
                        code, categorie, sous_categorie, titre, symptomes,
                        causes_possibles, diagnostic_conseil, urgence,
                        cout_min_dh, cout_max_dh, duree_reparation,
                        pieces_concernees, marque_specifique, embedding, updated_at
                    )
                    VALUES (
                        %(code)s, %(categorie)s, %(sous_categorie)s, %(titre)s, %(symptomes)s,
                        %(causes_possibles)s, %(diagnostic_conseil)s, %(urgence)s,
                        %(cout_min_dh)s, %(cout_max_dh)s, %(duree_reparation)s,
                        %(pieces_concernees)s, %(marque_specifique)s, %(embedding)s::vector, now()
                    )
                    ON CONFLICT (code) DO UPDATE SET
                        categorie = EXCLUDED.categorie,
                        sous_categorie = EXCLUDED.sous_categorie,
                        titre = EXCLUDED.titre,
                        symptomes = EXCLUDED.symptomes,
                        causes_possibles = EXCLUDED.causes_possibles,
                        diagnostic_conseil = EXCLUDED.diagnostic_conseil,
                        urgence = EXCLUDED.urgence,
                        cout_min_dh = EXCLUDED.cout_min_dh,
                        cout_max_dh = EXCLUDED.cout_max_dh,
                        duree_reparation = EXCLUDED.duree_reparation,
                        pieces_concernees = EXCLUDED.pieces_concernees,
                        marque_specifique = EXCLUDED.marque_specifique,
                        embedding = EXCLUDED.embedding,
                        updated_at = now()
                    """,
                    {
                        "code": panne["code"],
                        "categorie": panne["categorie"],
                        "sous_categorie": panne.get("sous_categorie"),
                        "titre": panne["titre"],
                        "symptomes": panne["symptomes"],
                        "causes_possibles": panne["causes_possibles"],
                        "diagnostic_conseil": panne["diagnostic_conseil"],
                        "urgence": panne["urgence"],
                        "cout_min_dh": panne.get("cout_min_dh"),
                        "cout_max_dh": panne.get("cout_max_dh"),
                        "duree_reparation": panne.get("duree_reparation"),
                        "pieces_concernees": panne.get("pieces_concernees"),
                        "marque_specifique": panne.get("marque_specifique"),
                        "embedding": to_vector_literal(embedding),
                    },
                )
        conn.commit()
        print(f"{len(pannes)} pannes upsertees dans base_pannes.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
