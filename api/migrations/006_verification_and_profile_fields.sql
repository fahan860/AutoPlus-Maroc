-- Verification d'email a l'inscription + champs de profil complementaires.
-- A executer apres 001..005.

-- ────────────────────────────────────────────────────────────
-- USERS : verification email + profil (adresse/ville)
-- ────────────────────────────────────────────────────────────
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verifie BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code_hash TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code_expires_at TIMESTAMPTZ;
ALTER TABLE users ADD COLUMN IF NOT EXISTS adresse TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS ville TEXT;

-- Les comptes crees avant cette migration n'ont jamais recu de code : on ne
-- veut pas les bloquer retroactivement a la prochaine connexion.
UPDATE users SET email_verifie = true WHERE email_verifie = false;

-- ────────────────────────────────────────────────────────────
-- GARAGES : details complementaires saisis par le mecanicien
-- (services proposes, horaires) quand il cree son garage lui-meme
-- au lieu de revendiquer une fiche scrapee existante.
-- ────────────────────────────────────────────────────────────
ALTER TABLE garages ADD COLUMN IF NOT EXISTS services TEXT;
ALTER TABLE garages ADD COLUMN IF NOT EXISTS horaires TEXT;
