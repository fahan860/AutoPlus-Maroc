"""
Retrieval de la Knowledge Base (Phase 6) : recherche vectorielle (pgvector)
combinee a des filtres structures sur les metadonnees (systeme, vehicule,
langue, gravite), comme prevu dans ai/docs/KB_SCHEMA.md.

Utilisable en script de demo/test (CLI) ou importable comme fonction
`search_kb(...)` depuis le futur service agent (Phase 8+).

Usage CLI :
    python ai/scripts/query_kb.py "ma voiture cale au demarrage" --systeme moteur --top-k 3
"""

import argparse
import os
import sys
from pathlib import Path

import truststore

truststore.inject_into_ssl()

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

load_dotenv(ROOT / "api" / ".env")

DATABASE_URL = os.environ.get("DATABASE_URL")
MODEL_NAME = "intfloat/multilingual-e5-large"

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(MODEL_NAME)
    return _model


def to_vector_literal(embedding) -> str:
    return "[" + ",".join(f"{x:.8f}" for x in embedding) + "]"


def search_kb(query: str, systeme: str = None, vehicule: str = None, langue: str = None,
              gravite: str = None, top_k: int = 5, database_url: str = None):
    """Retourne les top_k chunks les plus pertinents pour `query`, avec filtres
    optionnels sur les metadonnees du document parent. Chaque resultat :
    {document_id, symptome, cause, verification, gravite, similarite}."""
    import psycopg2

    database_url = database_url or DATABASE_URL
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL introuvable (attendu dans api/.env). "
            "Je ne devine jamais des identifiants : merci de le renseigner puis relancer."
        )

    # Prefixe "query: " requis par les modeles E5 (asymetrie requete/document,
    # cf. build_chunk_text dans load_kb_corpus.py qui prefixe en "passage: ").
    embedding = get_model().encode(f"query: {query}", normalize_embeddings=True)
    vec = to_vector_literal(embedding)

    where_clauses = []
    params = {"vec": vec, "top_k": top_k}
    if systeme:
        where_clauses.append("%(systeme)s = ANY(d.systeme)")
        params["systeme"] = systeme
    if vehicule:
        where_clauses.append("(d.vehicule = %(vehicule)s OR d.vehicule = '*')")
        params["vehicule"] = vehicule
    if langue:
        where_clauses.append("d.langue = %(langue)s")
        params["langue"] = langue
    if gravite:
        where_clauses.append("d.gravite = %(gravite)s")
        params["gravite"] = gravite

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT d.id, d.symptome, d.cause, d.verification, d.gravite, d.systeme,
                       1 - (c.embedding <=> %(vec)s::vector) AS similarite
                FROM kb_chunks c
                JOIN kb_documents d ON d.id = c.document_id
                {where_sql}
                ORDER BY c.embedding <=> %(vec)s::vector
                LIMIT %(top_k)s
                """,
                params,
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    return [
        {
            "document_id": r[0],
            "symptome": r[1],
            "cause": r[2],
            "verification": r[3],
            "gravite": r[4],
            "systeme": r[5],
            "similarite": round(float(r[6]), 4),
        }
        for r in rows
    ]


def main():
    parser = argparse.ArgumentParser(description="Retrieval Knowledge Base AUTO+ (demo Phase 6)")
    parser.add_argument("query", help="Question/symptome utilisateur en langage naturel")
    parser.add_argument("--systeme", default=None, help="Filtrer par categorie (ex: moteur)")
    parser.add_argument("--vehicule", default=None, help="Filtrer par vehicule (ex: 'boîte automatique')")
    parser.add_argument("--langue", default=None, help="Filtrer par langue (fr/ar/darija)")
    parser.add_argument("--gravite", default=None, help="Filtrer par gravite")
    parser.add_argument("--top-k", type=int, default=5, dest="top_k")
    args = parser.parse_args()

    results = search_kb(
        args.query,
        systeme=args.systeme,
        vehicule=args.vehicule,
        langue=args.langue,
        gravite=args.gravite,
        top_k=args.top_k,
    )

    if not results:
        print("Aucun resultat (verifier les filtres).")
        return

    for r in results:
        print(f"\n[{r['document_id']}] similarite={r['similarite']} systeme={r['systeme']} gravite={r['gravite']}")
        print(f"  symptome    : {r['symptome']}")
        print(f"  cause       : {r['cause']}")
        print(f"  verification: {r['verification']}")


if __name__ == "__main__":
    main()
