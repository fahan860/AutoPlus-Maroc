/**
 * Routes admin : validation des revendications de garage par les mecaniciens
 * + gestion des comptes utilisateurs (activation/desactivation).
 * Toutes les routes de ce fichier exigent le role 'admin' (voir POST
 * /users/register, role=admin, protege par ADMIN_SIGNUP_CODE).
 */

const express = require('express');
const { z } = require('zod');
const { pool } = require('../db');
const { requireAuth, requireRole } = require('../middleware/auth');
const { logEvent } = require('../events');
const { decrypt } = require('../crypto');

const router = express.Router();

router.use(requireAuth, requireRole('admin'));

const statutSchema = z.object({
  statut: z.enum(['valide', 'refuse']),
});

const actifSchema = z.object({
  actif: z.boolean(),
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

module.exports = router;
