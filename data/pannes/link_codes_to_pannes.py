"""
Semaine 4 du stage — relie codes_obd.panne_code_lie a base_pannes.code.

Methode : pour chaque code OBD dont categorie_probable a ete determinee (par
mots-cles, voir import_codes_obd.py), on cherche par similarite d'embedding
(meme modele que base_pannes) la panne la plus proche PARMI CELLES DE LA MEME
CATEGORIE. On ne lie jamais un code dont categorie_probable est NULL (aucun
signal fiable) : mieux vaut laisser panne_code_lie vide qu'un lien invente
par similarite pure sur l'ensemble des 50 pannes, qui produirait trop de faux
positifs (descriptions techniques EN vs symptomes client FR).

Usage : python data/pannes/link_codes_to_pannes.py
Necessite DATABASE_URL dans l'environnement (voir api/.env).
"""

import os
import sys
from pathlib import Path

import truststore

truststore.inject_into_ssl()  # magasin de certificats Windows (contourne
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


def to_vector_literal(embedding) -> str:
    return "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"


def main():
    import psycopg2
    from sentence_transformers import SentenceTransformer

    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT code, description_en, categorie_probable
                FROM codes_obd
                WHERE categorie_probable IS NOT NULL AND panne_code_lie IS NULL
                ORDER BY code
                """
            )
            candidates = cur.fetchall()

        print(f"{len(candidates)} codes OBD categorises a relier.")
        if not candidates:
            return

        print(f"Chargement du modele {MODEL_NAME}...")
        model = SentenceTransformer(MODEL_NAME)

        # Prefixe "query: " : la description OBD joue le role de requete face
        # aux pannes (prefixees "passage: " dans load_embeddings.py) --
        # convention requise par les modeles E5.
        descriptions = [f"query: {row[1]}" for row in candidates]
        print("Generation des embeddings des descriptions OBD...")
        embeddings = model.encode(descriptions, show_progress_bar=True, normalize_embeddings=True)

        linked = 0
        with conn.cursor() as cur:
            for (code, _description, categorie), embedding in zip(candidates, embeddings):
                vec = to_vector_literal(embedding)
                cur.execute(
                    """
                    SELECT code, 1 - (embedding <=> %s::vector) AS similarite
                    FROM base_pannes
                    WHERE categorie = %s
                    ORDER BY embedding <=> %s::vector
                    LIMIT 1
                    """,
                    (vec, categorie, vec),
                )
                match = cur.fetchone()
                if not match:
                    continue
                panne_code, _similarite = match
                cur.execute(
                    "UPDATE codes_obd SET panne_code_lie = %s WHERE code = %s",
                    (panne_code, code),
                )
                linked += 1
        conn.commit()
        print(f"{linked} codes OBD relies a une panne (meme categorie, plus proche par embedding).")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
