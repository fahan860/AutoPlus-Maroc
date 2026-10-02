-- Modele C (detection de faux avis) : moderation des avis.
-- A executer apres 001..007.
--
-- Cycle de vie d'un avis :
--   publie          : visible, compte dans la note du garage (cas normal)
--   en_verification : signale par le modele ML, masque en attendant un admin
--   valide          : verifie par un admin, visible
--   rejete          : faux avis confirme par un admin, jamais visible
-- suspect_faux_avis (002) reste vrai pour tout avis signale par le modele, meme valide
-- ensuite : c'est l'historique des alertes, utile pour mesurer le modele sur de vrais avis.

ALTER TABLE reviews ADD COLUMN IF NOT EXISTS moderation_statut TEXT NOT NULL DEFAULT 'publie';
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS score_faux_avis NUMERIC(4,3);
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS raisons_moderation TEXT[];
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS modere_le TIMESTAMPTZ;
ALTER TABLE reviews ADD COLUMN IF NOT EXISTS modere_par INTEGER REFERENCES users(id);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'reviews_moderation_statut_check') THEN
    ALTER TABLE reviews ADD CONSTRAINT reviews_moderation_statut_check
      CHECK (moderation_statut IN ('publie', 'en_verification', 'valide', 'rejete'));
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_reviews_moderation ON reviews (moderation_statut) WHERE moderation_statut = 'en_verification';

-- ────────────────────────────────────────────────────────────
-- Note des garages : conserver les avis externes (Telecontact...)
-- ────────────────────────────────────────────────────────────
-- Avant, chaque nouvel avis dans l'app recalculait la note a partir des seuls avis de
-- l'app, ce qui effacait la note importee (ex : M.I.A, 4,7/5 sur 3 avis Telecontact).
-- La note affichee devient la moyenne ponderee : avis externes + avis visibles de l'app.
ALTER TABLE garages ADD COLUMN IF NOT EXISTS note_externe NUMERIC(2,1);
ALTER TABLE garages ADD COLUMN IF NOT EXISTS nb_avis_externe INTEGER NOT NULL DEFAULT 0;

-- Initialisation : tant qu'aucun avis de l'app n'existe pour un garage, sa note actuelle
-- est entierement externe (import du scraping).
UPDATE garages g
SET note_externe = g.note, nb_avis_externe = g.nb_avis
WHERE g.note IS NOT NULL AND g.nb_avis_externe = 0
  AND NOT EXISTS (SELECT 1 FROM reviews r WHERE r.garage_id = g.id);
