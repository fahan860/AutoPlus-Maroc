/**
 * Routes agent : assistant IA de diagnostic (RAG + LLM, voir ml/src/agent/agent.py).
 * L'app envoie l'historique complet de la conversation a chaque message ; le service ML
 * est sans etat. Chaque conversation est enregistree (migrations/009_agent_conversations.sql)
 * pour que l'utilisateur la retrouve dans son historique.
 */

const express = require('express');
const { z } = require('zod');
const { pool } = require('../db');
const { requireAuth } = require('../middleware/auth');
const { logEvent } = require('../events');

const router = express.Router();

const ML_API_URL = process.env.ML_API_URL || 'http://localhost:8000';
// Deux appels au LLM par message (reformulation puis reponse) : plusieurs secondes
const ML_API_TIMEOUT_MS = 45000;
const LONGUEUR_TITRE = 60;

const chatSchema = z.object({
  conversation_id: z.number().int().positive().optional(),
  messages: z
    .array(
      z.object({
        role: z.enum(['user', 'assistant']),
        content: z.string().min(1).max(1000),
        action: z.enum(['question', 'diagnostic', 'hors_sujet']).optional(),
      })
    )
    .min(1)
    .max(20),
  vehicule: z.record(z.any()).nullable().optional(),
  lat: z.number().optional(),
  lon: z.number().optional(),
});

function titreDe(messages) {
  const premier = messages.find((m) => m.role === 'user')?.content.trim() || 'Conversation';
  return premier.length > LONGUEUR_TITRE ? `${premier.slice(0, LONGUEUR_TITRE - 1)}…` : premier;
}

// Enregistre l'echange (messages envoyes + reponse de l'agent) ; retourne l'id de la conversation.
// L'analyse complete est gardee avec le message de l'assistant pour la reafficher a l'identique.
async function enregistrer(userId, conversationId, messages, reponse) {
  const echange = [
    ...messages,
    { role: 'assistant', content: reponse.message, action: reponse.action, reponse },
  ];
  const gravite = reponse.action === 'diagnostic' ? reponse.gravite : null;

  if (conversationId) {
    const { rows } = await pool.query(
      `UPDATE agent_conversations
       SET messages = $1, derniere_gravite = COALESCE($2, derniere_gravite), updated_at = now()
       WHERE id = $3 AND user_id = $4
       RETURNING id`,
      [JSON.stringify(echange), gravite, conversationId, userId]
    );
    if (rows[0]) return rows[0].id;
    // Conversation supprimee entre-temps ou d'un autre utilisateur : on en cree une nouvelle
  }
  const { rows } = await pool.query(
    `INSERT INTO agent_conversations (user_id, titre, messages, derniere_gravite)
     VALUES ($1, $2, $3, $4) RETURNING id`,
    [userId, titreDe(messages), JSON.stringify(echange), gravite]
  );
  return rows[0].id;
}

// POST /agent/chat : un tour de conversation avec l'assistant
router.post('/chat', requireAuth, async (req, res) => {
  const parsed = chatSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }
  const { conversation_id: conversationId, ...demande } = parsed.data;

  let reponse;
  try {
    reponse = await fetch(`${ML_API_URL}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(demande),
      signal: AbortSignal.timeout(ML_API_TIMEOUT_MS),
    });
  } catch (err) {
    console.error('Service ML injoignable :', err.message);
    return res.status(503).json({ status: 'error', message: "L'assistant est momentanement indisponible" });
  }

  const corps = await reponse.json().catch(() => ({}));

  if (reponse.status === 422) {
    const premiere = corps.detail?.[0];
    const champ = premiere?.loc?.slice(1).join('.') || 'requete';
    return res.status(400).json({ status: 'error', message: `${champ} : ${premiere?.msg || 'invalide'}` });
  }
  if (!reponse.ok) {
    return res.status(503).json({ status: 'error', message: "L'assistant est momentanement indisponible" });
  }

  let id = null;
  try {
    id = await enregistrer(req.user.id, conversationId, demande.messages, corps);
  } catch (err) {
    // L'historique ne doit pas empecher de repondre
    console.error('[agent] enregistrement de la conversation impossible :', err.message);
  }

  // Sans le texte de la conversation (donnees personnelles) : seulement ce qui sert a evaluer l'agent
  logEvent('agent_message', {
    action: corps.action,
    langue: corps.langue,
    gravite: corps.gravite,
    alerte_securite: corps.alerte_securite,
    nb_sources: corps.sources?.length ?? 0,
    nb_garages: corps.garages?.length ?? 0,
    nb_messages: demande.messages.length,
    duree_ms: corps.duree_ms,
    version_modele: corps.version_modele,
  }, req.user.id);

  res.json({ ...corps, conversation_id: id });
});

// GET /agent/conversations : historique de l'utilisateur connecte, les plus recentes d'abord
router.get('/conversations', requireAuth, async (req, res) => {
  try {
    const { rows } = await pool.query(
      `SELECT id, titre, derniere_gravite, jsonb_array_length(messages) AS nb_messages, created_at, updated_at
       FROM agent_conversations
       WHERE user_id = $1
       ORDER BY updated_at DESC
       LIMIT 100`,
      [req.user.id]
    );
    res.json({ count: rows.length, conversations: rows });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// GET /agent/conversations/:id : une conversation complete, pour la rouvrir
router.get('/conversations/:id', requireAuth, async (req, res) => {
  try {
    const { rows } = await pool.query(
      'SELECT id, titre, messages, derniere_gravite, created_at, updated_at FROM agent_conversations WHERE id = $1 AND user_id = $2',
      [req.params.id, req.user.id]
    );
    if (!rows[0]) return res.status(404).json({ status: 'error', message: 'Conversation introuvable' });
    res.json(rows[0]);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// DELETE /agent/conversations/:id : l'utilisateur supprime une de ses conversations
router.delete('/conversations/:id', requireAuth, async (req, res) => {
  try {
    const { rowCount } = await pool.query(
      'DELETE FROM agent_conversations WHERE id = $1 AND user_id = $2',
      [req.params.id, req.user.id]
    );
    if (!rowCount) return res.status(404).json({ status: 'error', message: 'Conversation introuvable' });
    logEvent('agent_conversation_supprimee', {}, req.user.id);
    res.status(204).end();
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

module.exports = router;
