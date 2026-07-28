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

// Recalcule note moyenne + nb_avis du garage a partir des reviews existantes.
async function recomputeGarageNote(garageId) {
  await pool.query(
    `UPDATE garages
     SET note = (SELECT ROUND(AVG(note)::numeric, 1) FROM reviews WHERE garage_id = $1),
         nb_avis = (SELECT COUNT(*) FROM reviews WHERE garage_id = $1),
         updated_at = now()
     WHERE id = $1`,
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
       WHERE reviews.garage_id = $1
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

    await recomputeGarageNote(garageId);

    logEvent('avis_poste', { garage_id: garageId, note }, req.user.id);

    res.status(201).json(rows[0]);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

module.exports = router;
