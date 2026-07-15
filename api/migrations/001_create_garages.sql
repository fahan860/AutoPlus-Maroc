-- Table de base pour la vitrine des mecaniciens/ateliers (annuaire garages)
-- A executer une seule fois sur la base autoplus (via docker exec ou un client psql).

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS garages (
    id            SERIAL PRIMARY KEY,
    nom           TEXT NOT NULL,
    categorie     TEXT,
    adresse       TEXT,
    ville         TEXT NOT NULL DEFAULT 'Casablanca',
    telephone     TEXT,
    note          NUMERIC(2,1),
    nb_avis       INTEGER DEFAULT 0,
    lien_fiche    TEXT UNIQUE,          -- sert de cle de dedup entre imports
    source        TEXT NOT NULL,        -- ex: 'telecontact.ma', 'google_maps'
    a_completer   BOOLEAN NOT NULL DEFAULT false, -- true si telephone manquant a la source (a enrichir)
    geom          GEOGRAPHY(POINT, 4326), -- rempli plus tard par geocoding (adresse -> lat/lng)
    scraped_at    TIMESTAMPTZ,          -- date du scraping (donnee source)
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_garages_ville ON garages (ville);
CREATE INDEX IF NOT EXISTS idx_garages_geom ON garages USING GIST (geom);
