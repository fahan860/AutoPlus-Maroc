-- Table des codes OBD-II (DTC), independante de base_pannes (n'altere pas
-- son schema). Semaine 4 du stage.

CREATE TABLE IF NOT EXISTS codes_obd (
    id                   SERIAL PRIMARY KEY,
    code                 TEXT NOT NULL UNIQUE,      -- ex: 'P0300'
    description_en       TEXT NOT NULL,
    famille              TEXT NOT NULL
                            CHECK (famille IN ('P', 'B', 'C', 'U')),  -- Powertrain/Body/Chassis/Network
    type_code            TEXT,                       -- ex: generique / constructeur, si dispo dans la source
    categorie_probable   TEXT,                        -- mappee vers les categories de base_pannes ;
                                                        -- NULL si aucun mot-cle de description ne matche
    panne_code_lie       TEXT REFERENCES base_pannes(code),  -- vide pour l'instant, a lier manuellement
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_codes_obd_famille ON codes_obd (famille);
CREATE INDEX IF NOT EXISTS idx_codes_obd_categorie_probable ON codes_obd (categorie_probable);
