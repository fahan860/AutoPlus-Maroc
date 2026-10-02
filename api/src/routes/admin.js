/**
 * Routes admin : validation des revendications de garage par les mecaniciens
 * + gestion des comptes utilisateurs (activation/desactivation)
 * + moderation des avis signales par le modele de detection de faux avis (Modele C).
 * Toutes les routes de ce fichier exigent le role 'admin' (voir POST
 * /users/register, role=admin, protege par ADMIN_SIGNUP_CODE).
 */

const express = require('express');
const { z } = require('zod');
const { pool } = require('../db');
const { requireAuth, requireRole } = require('../middleware/auth');
const { logEvent } = require('../events');
const { decrypt } = require('../crypto');
const { recomputeGarageNote } = require('./reviews');

const router = express.Router();

router.use(requireAuth, requireRole('admin'));

const statutSchema = z.object({
  statut: z.enum(['valide', 'refuse']),
});

const actifSchema = z.object({
  actif: z.boolean(),
});

const moderationSchema = z.object({
  decision: z.enum(['valide', 'rejete']),
});

// telephone/email sont stockes chiffres (voir ../crypto) : on les dechiffre
// juste avant de les renvoyer au back-office.
function withDecryptedContact(row) {
  return {
    ...row,
    telephone: decrypt(row.telephone),
    email: row.email ? decrypt(row.email) : null,
  };
}

// GET /admin/mecaniciens/pending : revendications de garage en attente de validation
router.get('/mecaniciens/pending', async (_req, res) => {
  try {
    const { rows } = await pool.query(
      `SELECT users.id, users.nom, users.telephone, users.email, users.created_at,
              garages.id AS garage_id, garages.nom AS garage_nom, garages.ville AS garage_ville
       FROM users
       JOIN garages ON garages.id = users.garage_id
       WHERE users.role = 'mecanicien' AND users.garage_statut = 'en_attente'
       ORDER BY users.created_at ASC`
    );
    res.json({ count: rows.length, mecaniciens: rows.map(withDecryptedContact) });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// PATCH /admin/mecaniciens/:userId/statut : valider ou refuser une revendication de garage
router.patch('/mecaniciens/:userId/statut', async (req, res) => {
  const parsed = statutSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }

  try {
    const { rows } = await pool.query(
      `UPDATE users
       SET garage_statut = $1, updated_at = now()
       WHERE id = $2 AND role = 'mecanicien'
       RETURNING id, nom, telephone, role, garage_id, garage_statut`,
      [parsed.data.statut, req.params.userId]
    );

    if (!rows[0]) {
      return res.status(404).json({ status: 'error', message: 'Compte mecanicien introuvable' });
    }

    logEvent('admin_mecanicien_statut', { user_id: rows[0].id, statut: rows[0].garage_statut }, req.user.id);

    res.json(withDecryptedContact(rows[0]));
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// GET /admin/users : liste de tous les comptes (moderation)
router.get('/users', async (req, res) => {
  const { role } = req.query;
  try {
    const params = [];
    let where = '';
    if (role) {
      params.push(role);
      where = 'WHERE role = $1';
    }
    const { rows } = await pool.query(
      `SELECT id, nom, telephone, email, role, garage_id, garage_statut, actif, created_at
       FROM users ${where}
       ORDER BY created_at DESC`,
      params
    );
    res.json({ count: rows.length, users: rows.map(withDecryptedContact) });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// PATCH /admin/users/:id/actif : activer / desactiver un compte
router.patch('/users/:id/actif', async (req, res) => {
  const parsed = actifSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }

  try {
    const { rows } = await pool.query(
      `UPDATE users SET actif = $1, updated_at = now() WHERE id = $2
       RETURNING id, nom, telephone, role, actif`,
      [parsed.data.actif, req.params.id]
    );

    if (!rows[0]) {
      return res.status(404).json({ status: 'error', message: 'Utilisateur introuvable' });
    }

    logEvent('admin_user_actif', { user_id: rows[0].id, actif: rows[0].actif }, req.user.id);

    res.json(withDecryptedContact(rows[0]));
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// GET /admin/reviews/en-verification : avis masques par le modele, en attente d'une decision
router.get('/reviews/en-verification', async (_req, res) => {
  try {
    const { rows } = await pool.query(
      `SELECT r.id, r.note, r.commentaire, r.created_at, r.score_faux_avis, r.raisons_moderation,
              r.garage_id, g.nom AS garage_nom, r.user_id, u.nom AS auteur, u.created_at AS auteur_inscrit_le,
              i.statut AS rdv_statut
       FROM reviews r
       JOIN garages g ON g.id = r.garage_id
       JOIN users u ON u.id = r.user_id
       LEFT JOIN interventions i ON i.id = r.intervention_id
       WHERE r.moderation_statut = 'en_verification'
       ORDER BY r.score_faux_avis DESC NULLS LAST, r.created_at`
    );
    res.json({ count: rows.length, reviews: rows });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// PATCH /admin/reviews/:id/moderation : l'admin publie (valide) ou rejette un avis signale.
// Ces decisions sont les futures etiquettes d'entrainement du modele, sur de vrais avis.
router.patch('/reviews/:id/moderation', async (req, res) => {
  const parsed = moderationSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }

  try {
    const { rows } = await pool.query(
      `UPDATE reviews
       SET moderation_statut = $1, modere_le = now(), modere_par = $2
       WHERE id = $3 AND moderation_statut = 'en_verification'
       RETURNING id, garage_id, moderation_statut, score_faux_avis`,
      [parsed.data.decision, req.user.id, req.params.id]
    );
    if (!rows[0]) {
      return res.status(404).json({ status: 'error', message: 'Avis introuvable ou deja modere' });
    }

    await recomputeGarageNote(rows[0].garage_id);
    logEvent('admin_moderation_avis', {
      review_id: rows[0].id,
      decision: rows[0].moderation_statut,
      score_faux_avis: rows[0].score_faux_avis,
    }, req.user.id);

    res.json(rows[0]);
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

module.exports = router;
