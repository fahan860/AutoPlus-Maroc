-- Modele B (recommandation de garages) : specialites de chaque garage.
-- A executer apres 001..006.
--
-- Les valeurs de `specialites` reprennent exactement les categories de
-- base_pannes (moteur, freins, climatisation...) : une panne diagnostiquee se
-- relie ainsi directement aux garages capables de la traiter.
--
-- `specialites_source` dit d'ou vient l'information, pour savoir quoi
-- verifier en priorite sur le terrain :
--   fiche_telecontact     : description detaillee publiee sur la fiche du garage
--   nom                   : deduite du nom (ex : "Carrosserie Maarif")
--   hypothese_generaliste : aucune information, garage suppose de mecanique generale
--   declaree              : saisie par le garage lui-meme (futur formulaire mecanicien)

ALTER TABLE garages ADD COLUMN IF NOT EXISTS specialites TEXT[];
ALTER TABLE garages ADD COLUMN IF NOT EXISTS specialites_source TEXT;

CREATE INDEX IF NOT EXISTS idx_garages_specialites ON garages USING GIN (specialites);
