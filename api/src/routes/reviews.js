/**
 * Routes reviews : avis clients sur un garage.
 * Voir migrations/002_create_core_tables.sql (table reviews) — le flag
 * suspect_faux_avis est pose plus tard par le modele ML (Semaine 6),
 * jamais par le client.
 */

const express = require('express');
const { z } = require('zod');
const { pool } = require('../db');
const { requireAuth, requireRole } = require('../middleware/auth');
const { logEvent } = require('../events');

const router = express.Router();

const createReviewSchema = z.object({
  garage_id: z.number().int(),
  intervention_id: z.number().int().optional(),
  note: z.number().min(0).max(5),
  commentaire: z.string().optional(),
});

const ML_API_URL = process.env.ML_API_URL || 'http://localhost:8000';
const ML_API_TIMEOUT_MS = 5000;

// Avis visibles publiquement et comptes dans la note : ni en verification, ni rejetes
// (voir migrations/008_moderation_avis.sql)
const AVIS_VISIBLES = "moderation_statut IN ('publie', 'valide')";

// Modele C : le service ML dit si l'avis qui vient d'etre enregistre est suspect.
// En cas de panne du service, l'avis est publie (on prefere laisser passer un faux avis
// que bloquer un vrai client) : retourne null.
async function verifierAvis(reviewId) {
  try {
    const reponse = await fetch(`${ML_API_URL}/moderation/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ review_id: reviewId }),
      signal: AbortSignal.timeout(ML_API_TIMEOUT_MS),
    });
    if (!reponse.ok) throw new Error(`HTTP ${reponse.status}`);
    return await reponse.json();
  } catch (err) {
    console.error(`[reviews] verification ML impossible pour l'avis ${reviewId} :`, err.message);
    return null;
  }
}

// Recalcule la note du garage : moyenne ponderee des avis externes importes (Telecontact,
// colonnes note_externe / nb_avis_externe, migration 008) et des avis visibles de l'app.
// Avant, seuls les avis de l'app comptaient et la note importee etait effacee.
async function recomputeGarageNote(garageId) {
  await pool.query(
    `UPDATE garages g
     SET note = CASE WHEN stats.total = 0 THEN NULL
                     ELSE ROUND((stats.somme + COALESCE(g.note_externe, 0) * g.nb_avis_externe) / stats.total, 1) END,
         nb_avis = stats.total,
         updated_at = now()
     FROM (
       SELECT COALESCE(SUM(r.note), 0) AS somme,
              COUNT(r.id) + (SELECT nb_avis_externe FROM garages WHERE id = $1) AS total
       FROM reviews r
       WHERE r.garage_id = $1 AND r.${AVIS_VISIBLES}
     ) stats
     WHERE g.id = $1`,
    [garageId]
  );
}

// GET /reviews?garage_id= : avis recents d'un garage (public)
router.get('/', async (req, res) => {
  const garageId = Number(req.query.garage_id);
  if (!garageId) {
    return res.status(400).json({ status: 'error', message: 'garage_id est requis' });
  }

  try {
    const { rows } = await pool.query(
      `SELECT reviews.id, reviews.note, reviews.commentaire, reviews.created_at,
              users.nom AS auteur
       FROM reviews
       JOIN users ON users.id = reviews.user_id
       WHERE reviews.garage_id = $1 AND reviews.${AVIS_VISIBLES}
       ORDER BY reviews.created_at DESC
       LIMIT 50`,
      [garageId]
    );
    res.json({ count: rows.length, reviews: rows });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// POST /reviews : un automobiliste poste un avis sur un garage
router.post('/', requireAuth, requireRole('automobiliste'), async (req, res) => {
  const parsed = createReviewSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }

  const { garage_id: garageId, intervention_id: interventionId, note, commentaire } = parsed.data;

  try {
    const garage = await pool.query('SELECT id FROM garages WHERE id = $1', [garageId]);
    if (!garage.rows[0]) {
      return res.status(404).json({ status: 'error', message: 'Garage introuvable' });
    }

    if (interventionId) {
      const intervention = await pool.query(
        'SELECT id FROM interventions WHERE id = $1 AND user_id = $2 AND garage_id = $3',
        [interventionId, req.user.id, garageId]
      );
      if (!intervention.rows[0]) {
        return res.status(400).json({ status: 'error', message: "Cette intervention n'appartient pas a cet utilisateur/garage" });
      }
    }

    const { rows } = await pool.query(
      `INSERT INTO reviews (garage_id, user_id, intervention_id, note, commentaire)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING *`,
      [garageId, req.user.id, interventionId || null, note, commentaire || null]
    );

    let avis = rows[0];
    const verification = await verifierAvis(avis.id);
    if (verification) {
      const aVerifier = verification.decision === 'verifier';
      const { rows: maj } = await pool.query(
        `UPDATE reviews
         SET moderation_statut = $1, suspect_faux_avis = $2, score_faux_avis = $3, raisons_moderation = $4
         WHERE id = $5
         RETURNING *`,
        [aVerifier ? 'en_verification' : 'publie', aVerifier, verification.score, verification.raisons, avis.id]
      );
      avis = maj[0];
    }

    await recomputeGarageNote(garageId);

    logEvent('avis_poste', {
      garage_id: garageId,
      note,
      moderation_statut: avis.moderation_statut,
      score_faux_avis: verification?.score ?? null,
    }, req.user.id);

    // Les raisons sont reservees a l'admin : l'auteur sait seulement que son avis est verifie
    const {
      raisons_moderation: _raisons, score_faux_avis: _score, suspect_faux_avis: _suspect, ...publicAvis
    } = avis;
    res.status(201).json({
      ...publicAvis,
      message: avis.moderation_statut === 'en_verification'
        ? 'Merci ! Votre avis sera publié après une vérification rapide.'
        : 'Merci, votre avis est publié.',
    });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

module.exports = router;
// Utilise aussi par la moderation admin (routes/admin.js)
module.exports.recomputeGarageNote = recomputeGarageNote;
