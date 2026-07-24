/**
 * Routes interventions : cycle de vie d'une demande de RDV.
 *
 *   automobiliste -> POST /interventions (creation), GET /interventions (ses propres RDV)
 *   mecanicien    -> GET /interventions (RDV de son garage), PATCH /interventions/:id/statut
 */

const express = require('express');
const { z } = require('zod');
const { pool } = require('../db');
const { requireAuth, requireRole } = require('../middleware/auth');
const { logEvent } = require('../events');

const router = express.Router();

const STATUTS = ['demande', 'confirme', 'en_cours', 'termine', 'annule'];

const createInterventionSchema = z.object({
  vehicle_id: z.number().int(),
  garage_id: z.number().int(),
  type_panne: z.string().optional(),
  description: z.string().optional(),
  date_rdv: z.string().datetime().optional(),
});

const updateStatutSchema = z.object({
  statut: z.enum(STATUTS),
});

// POST /interventions : un automobiliste demande un RDV
router.post('/', requireAuth, requireRole('automobiliste'), async (req, res) => {
  const parsed = createInterventionSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }

  const { vehicle_id: vehicleId, garage_id: garageId, type_panne: typePanne, description, date_rdv: dateRdv } = parsed.data;

  try {
    // Le vehicule doit appartenir a l'utilisateur connecte
    const vehicle = await pool.query('SELECT id FROM vehicles WHERE id = $1 AND user_id = $2', [vehicleId, req.user.id]);
    if (!vehicle.rows[0]) {
      return res.status(404).json({ status: 'error', message: 'Vehicule introuvable pour cet utilisateur' });
    }

    const garage = await pool.query('SELECT id FROM garages WHERE id = $1', [garageId]);
    if (!garage.rows[0]) {
      return res.status(404).json({ status: 'error', message: 'Garage introuvable' });
    }

    const { rows } = await pool.query(
      `INSERT INTO interventions (vehicle_id, garage_id, user_id, type_panne, description, date_rdv)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING *`,
      [vehicleId, garageId, req.user.id, typePanne || null, description || null, dateRdv || null]
    );

    logEvent('rdv_demande', { intervention_id: rows[0].id, garage_id: garageId }, req.user.id);

    res.status(201).json(rows[0]);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// GET /interventions : selon le role
//   automobiliste -> ses propres demandes
//   mecanicien    -> les demandes de son garage (garage_id lie a son compte)
router.get('/', requireAuth, async (req, res) => {
  try {
    if (req.user.role === 'mecanicien') {
      const user = await pool.query('SELECT garage_id FROM users WHERE id = $1', [req.user.id]);
      const garageId = user.rows[0]?.garage_id;
      if (!garageId) {
        return res.status(400).json({ status: 'error', message: 'Aucun garage rattache a ce compte mecanicien' });
      }
      const { rows } = await pool.query(
        'SELECT * FROM interventions WHERE garage_id = $1 ORDER BY created_at DESC',
        [garageId]
      );
      return res.json({ count: rows.length, interventions: rows });
    }

    const { rows } = await pool.query(
      'SELECT * FROM interventions WHERE user_id = $1 ORDER BY created_at DESC',
      [req.user.id]
    );
    res.json({ count: rows.length, interventions: rows });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// PATCH /interventions/:id/statut : le mecanicien du garage concerne accepte/refuse/avance le RDV
router.patch('/:id/statut', requireAuth, requireRole('mecanicien'), async (req, res) => {
  const parsed = updateStatutSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }

  try {
    const user = await pool.query('SELECT garage_id FROM users WHERE id = $1', [req.user.id]);
    const garageId = user.rows[0]?.garage_id;

    const { rows } = await pool.query(
      `UPDATE interventions
       SET statut = $1, updated_at = now()
       WHERE id = $2 AND garage_id = $3
       RETURNING *`,
      [parsed.data.statut, req.params.id, garageId]
    );

    if (!rows[0]) {
      return res.status(404).json({ status: 'error', message: 'Intervention introuvable pour ce garage' });
    }

    logEvent('rdv_statut_change', { intervention_id: rows[0].id, statut: rows[0].statut }, req.user.id);

    res.json(rows[0]);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

module.exports = router;
