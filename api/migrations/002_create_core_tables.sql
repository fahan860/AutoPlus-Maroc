-- Tables manquantes du schema Semaine 2 (users, vehicles, interventions, reviews, events)
-- A executer apres 001_create_garages.sql, sur la meme base autoplus.

-- ────────────────────────────────────────────────────────────
-- USERS : automobilistes, mecaniciens (garages), admins
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    nom             TEXT NOT NULL,
    telephone       TEXT NOT NULL UNIQUE,   -- identifiant principal (OTP SMS prevu Semaine 3)
    email           TEXT UNIQUE,
    mot_de_passe_hash TEXT,                 -- bcrypt ; nullable en attendant le passage a l'OTP
    role            TEXT NOT NULL DEFAULT 'automobiliste'
                        CHECK (role IN ('automobiliste', 'mecanicien', 'admin')),
    garage_id       INTEGER REFERENCES garages(id), -- rempli si role = 'mecanicien'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);

-- ────────────────────────────────────────────────────────────
-- VEHICLES : un vehicule appartient a un automobiliste
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vehicles (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plaque          TEXT NOT NULL UNIQUE,   -- cle de recherche "historique par plaque" (Semaine 4)
    marque          TEXT,
    modele          TEXT,
    annee           INTEGER,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_vehicles_user ON vehicles (user_id);
CREATE INDEX IF NOT EXISTS idx_vehicles_plaque ON vehicles (plaque);

-- ────────────────────────────────────────────────────────────
-- INTERVENTIONS : cycle de vie d'une demande de RDV / reparation
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS interventions (
    id              SERIAL PRIMARY KEY,
    vehicle_id      INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    garage_id       INTEGER NOT NULL REFERENCES garages(id),
    user_id         INTEGER NOT NULL REFERENCES users(id),
    type_panne      TEXT,                   -- ex: 'vidange', 'freins', 'climatisation'
    description     TEXT,                   -- description libre du client
    statut          TEXT NOT NULL DEFAULT 'demande'
                        CHECK (statut IN ('demande', 'confirme', 'en_cours', 'termine', 'annule')),
    prix_estime     NUMERIC(10, 2),
    prix_final      NUMERIC(10, 2),
    date_rdv        TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_interventions_vehicle ON interventions (vehicle_id);
CREATE INDEX IF NOT EXISTS idx_interventions_garage ON interventions (garage_id);
CREATE INDEX IF NOT EXISTS idx_interventions_statut ON interventions (statut);

-- ────────────────────────────────────────────────────────────
-- REVIEWS : avis client sur un garage (base du modele "detection faux avis")
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS reviews (
    id                  SERIAL PRIMARY KEY,
    garage_id           INTEGER NOT NULL REFERENCES garages(id) ON DELETE CASCADE,
    user_id             INTEGER NOT NULL REFERENCES users(id),
    intervention_id     INTEGER REFERENCES interventions(id), -- null si avis sans RDV verifie
    note                NUMERIC(2, 1) NOT NULL CHECK (note BETWEEN 0 AND 5),
    commentaire         TEXT,
    suspect_faux_avis   BOOLEAN NOT NULL DEFAULT false, -- flag pose par le modele ML (Semaine 6)
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_reviews_garage ON reviews (garage_id);

-- ────────────────────────────────────────────────────────────
-- EVENTS : log brut de toute action utilisateur, avant vidage vers le Data Lake (Parquet)
-- Voir data/README.md : Redis (buffer) -> flush periodique -> data/events/year=/month=/day=/*.parquet
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS events (
    id              BIGSERIAL PRIMARY KEY,
    user_id         INTEGER REFERENCES users(id),  -- null si utilisateur non authentifie
    type_event      TEXT NOT NULL,                 -- ex: 'recherche_garage', 'rdv_demande', 'avis_poste'
    payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_events_type ON events (type_event);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON events (created_at);
