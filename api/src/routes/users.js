/**
 * Routes users : inscription + connexion (mot de passe pour l'instant ;
 * l'OTP SMS prevu Semaine 3 remplacera/completera ce flux).
 */

const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { z } = require('zod');
const { pool } = require('../db');
const { logEvent } = require('../events');

const router = express.Router();

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-a-changer-en-prod';
const JWT_EXPIRES_IN = '30d';

const registerSchema = z.object({
  nom: z.string().min(1),
  telephone: z.string().min(9).max(20),
  email: z.string().email().optional(),
  mot_de_passe: z.string().min(6),
});

const loginSchema = z.object({
  telephone: z.string().min(9).max(20),
  mot_de_passe: z.string().min(1),
});

function toPublicUser(user) {
  const { mot_de_passe_hash, ...publicUser } = user;
  return publicUser;
}

function signToken(user) {
  return jwt.sign({ sub: user.id, role: user.role }, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
}

// POST /users/register
router.post('/register', async (req, res) => {
  const parsed = registerSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }

  const { nom, telephone, email, mot_de_passe } = parsed.data;

  try {
    const existing = await pool.query('SELECT id FROM users WHERE telephone = $1', [telephone]);
    if (existing.rows[0]) {
      return res.status(409).json({ status: 'error', message: 'Ce numero de telephone est deja utilise' });
    }

    const hash = await bcrypt.hash(mot_de_passe, 10);

    const { rows } = await pool.query(
      `INSERT INTO users (nom, telephone, email, mot_de_passe_hash, role)
       VALUES ($1, $2, $3, $4, 'automobiliste')
       RETURNING *`,
      [nom, telephone, email || null, hash]
    );

    const user = rows[0];

    logEvent('user_register', { role: user.role }, user.id);

    res.status(201).json({ user: toPublicUser(user), token: signToken(user) });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

// POST /users/login
router.post('/login', async (req, res) => {
  const parsed = loginSchema.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ status: 'error', message: parsed.error.errors[0].message });
  }

  const { telephone, mot_de_passe } = parsed.data;

  try {
    const { rows } = await pool.query('SELECT * FROM users WHERE telephone = $1', [telephone]);
    const user = rows[0];

    if (!user || !user.mot_de_passe_hash) {
      return res.status(401).json({ status: 'error', message: 'Identifiants invalides' });
    }

    const valid = await bcrypt.compare(mot_de_passe, user.mot_de_passe_hash);
    if (!valid) {
      return res.status(401).json({ status: 'error', message: 'Identifiants invalides' });
    }

    logEvent('user_login', {}, user.id);

    res.json({ user: toPublicUser(user), token: signToken(user) });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

module.exports = router;
