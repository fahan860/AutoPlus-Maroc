/**
 * Routes agent : assistant IA de diagnostic (RAG + LLM, voir ml/src/agent/agent.py).
 * L'app envoie l'historique complet de la conversation a chaque message ; le service ML
 * est sans etat.
 */

const express = require('express');
const { requireAuth } = require('../middleware/auth');
const { logEvent } = require('../events');

const router = express.Router();

const ML_API_URL = process.env.ML_API_URL || 'http://localhost:8000';
// Deux appels au LLM par message (reformulation puis reponse) : plusieurs secondes
const ML_API_TIMEOUT_MS = 45000;

// POST /agent/chat : un tour de conversation avec l'assistant
router.post('/chat', requireAuth, async (req, res) => {
  let reponse;
  try {
    reponse = await fetch(`${ML_API_URL}/agent/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
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

  // Sans le texte de la conversation (donnees personnelles) : seulement ce qui sert a evaluer l'agent
  logEvent('agent_message', {
    action: corps.action,
    langue: corps.langue,
    gravite: corps.gravite,
    alerte_securite: corps.alerte_securite,
    nb_sources: corps.sources?.length ?? 0,
    nb_garages: corps.garages?.length ?? 0,
    nb_messages: Array.isArray(req.body.messages) ? req.body.messages.length : 0,
    duree_ms: corps.duree_ms,
    version_modele: corps.version_modele,
  }, req.user.id);

  res.json(corps);
});

module.exports = router;
