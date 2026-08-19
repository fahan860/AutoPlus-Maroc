-- Schema pgvector de la Knowledge Base Agent IA (voir ai/docs/KB_SCHEMA.md,
-- Phase 1 et Phase 4 du plan V1). Reprend exactement les champs documentes
-- dans KB_SCHEMA.md. Independant de data/pannes/base_pannes (Semaine 4
-- stage, RAG pannes/OBD separe non fusionne pour l'instant).

CREATE EXTENSION IF NOT EXISTS vector;

-- 1 ligne = 1 entree de connaissance (voir ai/data/processed/kb_corpus_v1.csv).
-- id conserve au format string existant du corpus ('kb-v1-0001', ...) plutot
-- qu'un UUID genere, pour rester traçable 1:1 avec le CSV source.
CREATE TABLE IF NOT EXISTS kb_documents (
    id              TEXT PRIMARY KEY,
    symptome        TEXT NOT NULL,
    vehicule        TEXT NOT NULL,               -- '*' si generique toutes marques
    systeme         TEXT[] NOT NULL,              -- multi-valeurs (KB_SCHEMA.md : liste fermee)
    cause           TEXT NOT NULL,
    explication     TEXT NOT NULL,
    verification    TEXT NOT NULL,
    gravite         TEXT NOT NULL
                        CHECK (gravite IN ('faible', 'moyenne', 'elevee', 'critique')),
    source          TEXT NOT NULL,
    langue          TEXT NOT NULL
                        CHECK (langue IN ('fr', 'ar', 'darija')),
    date_maj        DATE NOT NULL,
    dtc_code        TEXT,                         -- nullable, ex: 'P0301'
    page_source     TEXT,                         -- nullable
    tags            TEXT[],                       -- nullable, multi-valeurs
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_kb_documents_systeme ON kb_documents USING GIN (systeme);
CREATE INDEX IF NOT EXISTS idx_kb_documents_langue ON kb_documents (langue);
CREATE INDEX IF NOT EXISTS idx_kb_documents_gravite ON kb_documents (gravite);
CREATE INDEX IF NOT EXISTS idx_kb_documents_vehicule ON kb_documents (vehicule);

-- N chunks par document (KB_SCHEMA.md : fragments issus de explication +
-- verification). Pour le corpus V1 (entrees courtes, deja atomiques), 1
-- document -> 1 chunk suffit (pas de decoupage supplementaire necessaire) ;
-- la table reste prete pour du multi-chunk si des documents plus longs
-- arrivent (Phase 3 : vrai chunking a revoir a ce moment-la).
CREATE TABLE IF NOT EXISTS kb_chunks (
    id              SERIAL PRIMARY KEY,
    document_id     TEXT NOT NULL REFERENCES kb_documents(id) ON DELETE CASCADE,
    chunk_text      TEXT NOT NULL,
    embedding       vector(1024),                 -- intfloat/multilingual-e5-large (prefixe "passage: ")
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_kb_chunks_document ON kb_chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_kb_chunks_embedding
    ON kb_chunks USING hnsw (embedding vector_cosine_ops);
