-- Chiffrement des donnees personnelles (telephone, email) : ces colonnes
-- stockent desormais une valeur chiffree (AES-256-GCM, cote application dans
-- api/src/crypto.js) au lieu du texte en clair. Le chiffrement etant non
-- deterministe (IV aleatoire), la contrainte UNIQUE directe sur ces colonnes
-- n'a plus de sens : on la remplace par un hash HMAC-SHA256 deterministe,
-- stocke a cote, qui sert a la recherche (login) et a la detection de
-- doublons sans jamais exposer la valeur en clair en base.
-- A executer apres 001, 002, 003, 004.
-- Les donnees existantes (encore en clair) doivent ensuite etre chiffrees
-- via `node api/scripts/backfill-pii-encryption.js`.

ALTER TABLE users DROP CONSTRAINT IF EXISTS users_telephone_key;
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_email_key;

ALTER TABLE users ADD COLUMN IF NOT EXISTS telephone_hash TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS email_hash TEXT;

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_telephone_hash ON users (telephone_hash);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_hash ON users (email_hash);
