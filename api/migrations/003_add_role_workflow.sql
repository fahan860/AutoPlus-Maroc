-- Semaine suivante : inscription avec choix de role (automobiliste / mecanicien / admin)
-- + workflow de revendication d'un garage existant par un mecanicien (validation admin)
-- + activation/desactivation des comptes par l'admin.
-- A executer apres 001_create_garages.sql et 002_create_core_tables.sql.

-- Statut de la revendication d'un garage par un compte mecanicien.
-- NULL tant que le compte n'est pas mecanicien / n'a pas encore choisi de garage.
ALTER TABLE users ADD COLUMN IF NOT EXISTS garage_statut TEXT
    CHECK (garage_statut IN ('en_attente', 'valide', 'refuse'));

-- Permet a l'admin de desactiver un compte sans le supprimer.
ALTER TABLE users ADD COLUMN IF NOT EXISTS actif BOOLEAN NOT NULL DEFAULT true;

CREATE INDEX IF NOT EXISTS idx_users_garage_statut ON users (garage_statut);
CREATE INDEX IF NOT EXISTS idx_users_actif ON users (actif);
