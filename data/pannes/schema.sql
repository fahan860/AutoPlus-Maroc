-- Base de connaissance pannes automobiles pour le RAG de l'Agent IA (pgvector).
-- Semaine 4 du stage. A executer sur la base AUTO+ (voir DATABASE_URL dans api/.env).

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS base_pannes (
    id                  SERIAL PRIMARY KEY,
    code                TEXT NOT NULL UNIQUE,      -- ex: 'MOT-01'
    categorie           TEXT NOT NULL,              -- moteur, freins, climatisation, transmission,
                                                      -- electrique, pneus_suspension, direction,
                                                      -- echappement, entretien_courant, carrosserie
    sous_categorie      TEXT,
    titre               TEXT NOT NULL,
    symptomes           TEXT[] NOT NULL,             -- plusieurs formulations client
    causes_possibles    TEXT[] NOT NULL,
    diagnostic_conseil  TEXT NOT NULL,
    urgence             TEXT NOT NULL
                            CHECK (urgence IN ('faible', 'moyenne', 'elevee', 'critique')),
    cout_min_dh         NUMERIC(10, 2),
    cout_max_dh         NUMERIC(10, 2),
    duree_reparation     TEXT,                       -- ex: '30 min', '1-2 jours'
    pieces_concernees   TEXT[],
    marque_specifique   TEXT,                        -- NULL si generique toutes marques
    embedding           vector(1024),                -- intfloat/multilingual-e5-large (prefixe "passage: ")
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_base_pannes_categorie ON base_pannes (categorie);

-- Index HNSW pour la recherche vectorielle (similarite cosinus, adapte aux
-- embeddings de sentence-transformers).
CREATE INDEX IF NOT EXISTS idx_base_pannes_embedding
    ON base_pannes USING hnsw (embedding vector_cosine_ops);
