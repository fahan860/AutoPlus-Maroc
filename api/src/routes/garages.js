/**
 * Routes garages : consultation de l'annuaire (donnees reelles scrapees,
 * voir scripts/import_garages_csv.js) + creation manuelle.
 */

const express = require('express');
const { z } = require('zod');
const { pool } = require('../db');
const { logEvent } = require('../events');

const router = express.Router();

const createGarageSchema = z.object({
  nom: z.string().min(1),
  categorie: z.string().optional(),
  adresse: z.string().optional(),
  ville: z.string().optional(),
  telephone: z.string().optional(),
  source: z.string().default('manuel'),
});

// GET /garages?lat=&lng=&radius_km=&ville=
// Si lat/lng fournis : tri par distance (necessite que `geom` soit rempli via
// geocoding - pas encore fait sur les donnees scrapees actuelles, voir
// commentaire dans migrations/001_create_garages.sql). Sans lat/lng : liste
// simple, filtrable par ville.
router.get('/', async (req, res) => {
  try {
    const { lat, lng, radius_km: radiusKm, ville } = req.query;

    const whereClauses = [];
    const params = [];

    if (ville) {
      params.push(ville);
      whereClauses.push(`ville = $${params.length}`);
    }

    const where = whereClauses.length ? `WHERE ${whereClauses.join(' AND ')}` : '';

    let rows;

    if (lat && lng) {
      const point = `ST_SetSRID(ST_MakePoint($${params.length + 1}, $${params.length + 2}), 4326)::geography`;
      params.push(Number(lng), Number(lat));

      let radiusFilter = '';
      if (radiusKm) {
        params.push(Number(radiusKm) * 1000);
        radiusFilter = `${where ? 'AND' : 'WHERE'} geom IS NOT NULL AND ST_DWithin(geom, ${point}, $${params.length})`;
      }

      ({ rows } = await pool.query(
        `SELECT id, nom, categorie, adresse, ville, telephone, note, nb_avis, a_completer,
                ST_Distance(geom, ${point}) AS distance_m
         FROM garages
         ${where}
         ${radiusFilter}
         ORDER BY geom IS NULL, distance_m ASC NULLS LAST
         LIMIT 50`,
        params
      ));
    } else {
      ({ rows } = await pool.query(
        `SELECT id, nom, categorie, adresse, ville, telephone, note, nb_avis, a_completer
         FROM garages
         ${where}
         ORDER BY note DESC NULLS LAST
         LIMIT 50`,
        params
      ));
    }

    logEvent('recherche_garage', { lat: lat || null, lng: lng || null, ville: ville || null, resultats: rows.length });

    res.json({ count: rows.length, garages: rows });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// GET /garages/:id
router.get('/:id', async (req, res) => {
  try {
    const { rows } = await pool.query('SELECT * FROM garages WHERE id = $1', [req.params.id]);
    if (!rows[0]) return res.status(404).json({ status: 'error', message: 'Garage introuvable' });

    logEvent('consultation_garage', { garage_id: rows[0].id });

    res.json(rows[0]);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// POST /garages
router.post('/', async (req, res) => {
  const parsed = createGarageSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }

  const { nom, categorie, adresse, ville, telephone, source } = parsed.data;

  try {
    const { rows } = await pool.query(
      `INSERT INTO garages (nom, categorie, adresse, ville, telephone, source, a_completer)
       VALUES ($1, $2, $3, COALESCE($4, 'Casablanca'), $5, $6, $7)
       RETURNING *`,
      [nom, categorie || null, adresse || null, ville, telephone || null, source, !telephone]
    );

    logEvent('garage_cree', { garage_id: rows[0].id, source });

    res.status(201).json(rows[0]);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

module.exports = router;
