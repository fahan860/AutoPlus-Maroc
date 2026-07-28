/**
 * Routes garages : consultation de l'annuaire (donnees reelles scrapees,
 * voir scripts/import_garages_csv.js) + creation manuelle.
 */

const express = require('express');
const { z } = require('zod');
const { pool } = require('../db');
const { requireAuth, requireRole } = require('../middleware/auth');
const { logEvent } = require('../events');

const router = express.Router();

// Recupere le garage valide (revendication approuvee par un admin) du
// mecanicien connecte, ou renvoie une erreur HTTP explicite.
async function getGarageValideDuMecanicien(req, res) {
  const { rows } = await pool.query(
    'SELECT garage_id, garage_statut FROM users WHERE id = $1',
    [req.user.id]
  );
  const info = rows[0];

  if (!info || !info.garage_id) {
    res.status(400).json({ status: 'error', message: 'Aucun garage rattache a ce compte mecanicien' });
    return null;
  }
  if (info.garage_statut !== 'valide') {
    res.status(403).json({
      status: 'error',
      message: `Revendication du garage ${info.garage_statut === 'refuse' ? 'refusee' : 'en attente de validation par un admin'}`,
    });
    return null;
  }
  return info.garage_id;
}

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
                ST_Y(geom::geometry) AS latitude, ST_X(geom::geometry) AS longitude,
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
        `SELECT id, nom, categorie, adresse, ville, telephone, note, nb_avis, a_completer,
                ST_Y(geom::geometry) AS latitude, ST_X(geom::geometry) AS longitude
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

// GET /garages/mine : tableau de bord du mecanicien connecte (son garage + compteurs de RDV)
router.get('/mine', requireAuth, requireRole('mecanicien'), async (req, res) => {
  try {
    const garageId = await getGarageValideDuMecanicien(req, res);
    if (!garageId) return; // reponse deja envoyee par le helper

    const garage = await pool.query(
      `SELECT id, nom, categorie, adresse, ville, telephone, note, nb_avis,
              ST_Y(geom::geometry) AS latitude, ST_X(geom::geometry) AS longitude
       FROM garages WHERE id = $1`,
      [garageId]
    );

    const compteurs = await pool.query(
      `SELECT statut, COUNT(*)::int AS total
       FROM interventions WHERE garage_id = $1 GROUP BY statut`,
      [garageId]
    );

    res.json({
      garage: garage.rows[0],
      compteurs_rdv: compteurs.rows.reduce((acc, row) => ({ ...acc, [row.statut]: row.total }), {}),
    });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// GET /garages/mine/vehicules : vehicules des clients ayant eu un RDV dans ce garage
router.get('/mine/vehicules', requireAuth, requireRole('mecanicien'), async (req, res) => {
  try {
    const garageId = await getGarageValideDuMecanicien(req, res);
    if (!garageId) return;

    const { rows } = await pool.query(
      `SELECT DISTINCT vehicles.id, vehicles.plaque, vehicles.marque, vehicles.modele, vehicles.annee,
              users.nom AS proprietaire
       FROM vehicles
       JOIN interventions ON interventions.vehicle_id = vehicles.id
       JOIN users ON users.id = vehicles.user_id
       WHERE interventions.garage_id = $1
       ORDER BY vehicles.id DESC`,
      [garageId]
    );
    res.json({ count: rows.length, vehicules: rows });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// GET /garages/:id
router.get('/:id', async (req, res) => {
  try {
    const { rows } = await pool.query(
      `SELECT id, nom, categorie, adresse, ville, telephone, note, nb_avis, a_completer, source, scraped_at, created_at,
              ST_Y(geom::geometry) AS latitude, ST_X(geom::geometry) AS longitude
       FROM garages WHERE id = $1`,
      [req.params.id]
    );
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
