-- Agent IA : historique des conversations de chaque utilisateur.
-- A executer apres 001..008.
--
-- Une ligne par conversation. `messages` = l'echange complet tel qu'affiche dans l'app
-- ([{role, content, action?, reponse?}] ; `reponse` garde l'analyse de l'agent : causes,
-- gravite, garages...) pour pouvoir rouvrir une conversation exactement comme elle etait.
-- Donnees personnelles : visibles uniquement par leur auteur, qui peut les supprimer.

CREATE TABLE IF NOT EXISTS agent_conversations (
  id               SERIAL PRIMARY KEY,
  user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  titre            TEXT NOT NULL,
  messages         JSONB NOT NULL DEFAULT '[]'::jsonb,
  derniere_gravite TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_conversations_user ON agent_conversations (user_id, updated_at DESC);
