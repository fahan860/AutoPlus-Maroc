-- L'email devient obligatoire a l'inscription, au meme titre que le telephone.
-- A executer apres 001, 002, 003.

-- Si des comptes existants ont ete crees quand l'email etait optionnel, cette
-- migration echoue tant qu'ils n'ont pas ete completes (aucun email invente
-- automatiquement). Verifier avec :
--   SELECT id, nom, telephone FROM users WHERE email IS NULL;

ALTER TABLE users ALTER COLUMN email SET NOT NULL;
