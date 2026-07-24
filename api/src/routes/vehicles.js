/**
 * Routes vehicles : gestion des vehicules de l'utilisateur connecte.
 * L'historique par plaque (recherche libre, Semaine 4 - agent IA) sera
 * ajoute separement ; ici on gere uniquement le CRUD de base cote client.
 */

const express = require('express');
const { z } = require('zod');
const { pool } = require('../db');
const { requireAuth } = require('../middleware/auth');
const { logEvent } = require('../events');

const router = express.Router();

const createVehicleSchema = z.object({
  plaque: z.string().min(1),
  marque: z.string().optional(),
  modele: z.string().optional(),
  annee: z.number().int().min(1980).max(2100).optional(),
});

// GET /vehicles : liste des vehicules de l'utilisateur connecte
router.get('/', requireAuth, async (req, res) => {
  try {
    const { rows } = await pool.query(
      'SELECT * FROM vehicles WHERE user_id = $1 ORDER BY created_at DESC',
      [req.user.id]
    );
    res.json({ count: rows.length, vehicles: rows });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// GET /vehicles/:id : detail (uniquement si le vehicule appartient a l'utilisateur)
router.get('/:id', requireAuth, async (req, res) => {
  try {
    const { rows } = await pool.query(
      'SELECT * FROM vehicles WHERE id = $1 AND user_id = $2',
      [req.params.id, req.user.id]
    );
    if (!rows[0]) return res.status(404).json({ status: 'error', message: 'Vehicule introuvable' });
    res.json(rows[0]);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// POST /vehicles : ajoute un vehicule pour l'utilisateur connecte
router.post('/', requireAuth, async (req, res) => {
  const parsed = createVehicleSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }

  const { plaque, marque, modele, annee } = parsed.data;

  try {
    const existing = await pool.query('SELECT id FROM vehicles WHERE plaque = $1', [plaque]);
    if (existing.rows[0]) {
      return res.status(409).json({ status: 'error', message: 'Cette plaque est deja enregistree' });
    }

    const { rows } = await pool.query(
      `INSERT INTO vehicles (user_id, plaque, marque, modele, annee)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING *`,
      [req.user.id, plaque, marque || null, modele || null, annee || null]
    );

    logEvent('vehicule_ajoute', { vehicle_id: rows[0].id }, req.user.id);

    res.status(201).json(rows[0]);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

module.exports = router;
