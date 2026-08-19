"""
Charge ai/data/processed/kb_corpus_v1.csv dans kb_documents + kb_chunks
(Phase 3 : chunking, Phase 5 : embeddings). A executer apres ai/db/schema.sql.

Pour ce corpus V1 (entrees courtes et deja atomiques), le chunking se limite
a construire un chunk unique par document a partir de explication +
verification (le texte le plus utile pour repondre a une question utilisateur).
Un vrai decoupage multi-chunk sera a construire si des documents plus longs
(PDF constructeur, etc.) arrivent dans le corpus (Phase 3 complete).

Usage : python ai/scripts/load_kb_corpus.py
Necessite DATABASE_URL dans l'environnement (voir api/.env).
"""

import csv
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
CORPUS_PATH = ROOT / "ai" / "data" / "processed" / "kb_corpus_v1.csv"


def split_multi(value: str):
    return [v.strip() for v in value.split(";") if v.strip()]


def build_chunk_text(row: dict) -> str:
    # symptome en premier : c'est le champ redige dans les mots d'un
    # utilisateur reel, donc celui qui doit matcher une question posee en
    # langage naturel. explication/verification apportent le contexte
    # technique mais ne suffisent pas seuls a matcher la question.
    # Prefixe "passage: " requis par les modeles E5 (asymetrie
    # requete/document) -- voir query_kb.py qui prefixe la requete en "query: ".
    return (
        f"passage: {row['symptome'].strip()} {row['cause'].strip()} "
        f"{row['explication'].strip()} {row['verification'].strip()}"
    )


def to_vector_literal(embedding) -> str:
    return "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"


def main():
    import psycopg2
    from sentence_transformers import SentenceTransformer

    with open(CORPUS_PATH, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"{len(rows)} entrees chargees depuis {CORPUS_PATH.name}")

    print(f"Chargement du modele {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    chunk_texts = [build_chunk_text(row) for row in rows]
    print("Generation des embeddings...")
    embeddings = model.encode(chunk_texts, show_progress_bar=True, normalize_embeddings=True)

    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            for row, chunk_text, embedding in zip(rows, chunk_texts, embeddings):
                cur.execute(
                    """
                    INSERT INTO kb_documents (
                        id, symptome, vehicule, systeme, cause, explication,
                        verification, gravite, source, langue, date_maj,
                        dtc_code, page_source, tags, updated_at
                    )
                    VALUES (%(id)s, %(symptome)s, %(vehicule)s, %(systeme)s, %(cause)s,
                            %(explication)s, %(verification)s, %(gravite)s, %(source)s,
                            %(langue)s, %(date_maj)s, %(dtc_code)s, %(page_source)s,
                            %(tags)s, now())
                    ON CONFLICT (id) DO UPDATE SET
                        symptome = EXCLUDED.symptome,
                        vehicule = EXCLUDED.vehicule,
                        systeme = EXCLUDED.systeme,
                        cause = EXCLUDED.cause,
                        explication = EXCLUDED.explication,
                        verification = EXCLUDED.verification,
                        gravite = EXCLUDED.gravite,
                        source = EXCLUDED.source,
                        langue = EXCLUDED.langue,
                        date_maj = EXCLUDED.date_maj,
                        dtc_code = EXCLUDED.dtc_code,
                        page_source = EXCLUDED.page_source,
                        tags = EXCLUDED.tags,
                        updated_at = now()
                    """,
                    {
                        "id": row["id"].strip(),
                        "symptome": row["symptome"].strip(),
                        "vehicule": row["vehicule"].strip(),
                        "systeme": split_multi(row["systeme"]),
                        "cause": row["cause"].strip(),
                        "explication": row["explication"].strip(),
                        "verification": row["verification"].strip(),
                        "gravite": row["gravite"].strip(),
                        "source": row["source"].strip(),
                        "langue": row["langue"].strip(),
                        "date_maj": row["date_maj"].strip(),
                        "dtc_code": row.get("dtc_code", "").strip() or None,
                        "page_source": row.get("page_source", "").strip() or None,
                        "tags": split_multi(row.get("tags", "")) or None,
                    },
                )

                # Remplace le(s) chunk(s) existant(s) pour ce document (idempotent).
                cur.execute("DELETE FROM kb_chunks WHERE document_id = %s", (row["id"].strip(),))
                cur.execute(
                    """
                    INSERT INTO kb_chunks (document_id, chunk_text, embedding)
                    VALUES (%s, %s, %s::vector)
                    """,
                    (row["id"].strip(), chunk_text, to_vector_literal(embedding)),
                )
        conn.commit()
        print(f"{len(rows)} documents + chunks upsertes dans kb_documents / kb_chunks.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
