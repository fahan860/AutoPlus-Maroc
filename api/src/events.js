/**
 * Logging des events applicatifs : chaque action utilisateur (recherche,
 * RDV, avis...) est poussee en JSON dans une liste Redis ("events:queue"),
 * puis videe periodiquement vers le Data Lake Parquet par le script Python
 * data/pipeline/flush_events_to_parquet.py (voir data/README.md).
 *
 * On ne fait jamais planter une requete a cause d'un probleme de logging :
 * logEvent() avale ses propres erreurs (log en console seulement).
 */

const { redis } = require('./redis');

const EVENTS_QUEUE_KEY = 'events:queue';

async function logEvent(typeEvent, payload = {}, userId = null) {
  try {
    const event = {
      type_event: typeEvent,
      user_id: userId,
      payload,
      created_at: new Date().toISOString(),
    };
    await redis.lpush(EVENTS_QUEUE_KEY, JSON.stringify(event));
  } catch (err) {
    console.error(`Erreur logEvent(${typeEvent}) :`, err.message);
  }
}

module.exports = { logEvent, EVENTS_QUEUE_KEY };
