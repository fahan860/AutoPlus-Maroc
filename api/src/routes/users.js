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
const { encrypt, decrypt, hashForLookup } = require('../crypto');

const router = express.Router();

const JWT_SECRET = process.env.JWT_SECRET || 'dev-secret-a-changer-en-prod';
const JWT_EXPIRES_IN = '30d';

// Code exige pour s'inscrire en tant qu'admin (evite qu'un compte admin soit
// cree librement depuis l'app mobile). A definir en variable d'environnement.
const ADMIN_SIGNUP_CODE = process.env.ADMIN_SIGNUP_CODE || null;

// 8 caracteres minimum, au moins une majuscule, une minuscule, un chiffre et
// un caractere special.
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;
const PASSWORD_MESSAGE =
  'Le mot de passe doit contenir au moins 8 caracteres, une majuscule, une minuscule, un chiffre et un caractere special';

const registerSchema = z.object({
  nom: z.string().min(1),
  telephone: z.string().min(9).max(20),
  email: z.string().email(),
  mot_de_passe: z.string().regex(PASSWORD_REGEX, PASSWORD_MESSAGE),
  role: z.enum(['automobiliste', 'mecanicien', 'admin']).default('automobiliste'),
  // Requis si role = 'mecanicien' : garage existant (base scrapee) que le
  // mecanicien revendique. La revendication reste "en_attente" jusqu'a
  // validation par un admin (voir routes/admin.js).
  garage_id: z.number().int().optional(),
  // Requis si role = 'admin'.
  admin_code: z.string().optional(),
});

const loginSchema = z.object({
  identifiant: z.string().min(3),
  mot_de_passe: z.string().min(1),
});

function toPublicUser(user) {
  const { mot_de_passe_hash, telephone_hash, email_hash, telephone, email, ...publicUser } = user;
  return {
    ...publicUser,
    telephone: decrypt(telephone),
    email: email ? decrypt(email) : null,
  };
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

  const { nom, telephone, email, mot_de_passe, role, garage_id: garageId, admin_code: adminCode } = parsed.data;

  // Regles specifiques par role, verifiees avant toute ecriture en base.
  if (role === 'admin') {
    if (!ADMIN_SIGNUP_CODE || adminCode !== ADMIN_SIGNUP_CODE) {
      return res.status(403).json({ status: 'error', message: 'Code administrateur invalide' });
    }
  }

  if (role === 'mecanicien' && !garageId) {
    return res.status(400).json({
      status: 'error',
      message: 'garage_id est requis pour un compte mecanicien (choisir un garage existant a revendiquer)',
    });
  }

  const telephoneHash = hashForLookup(telephone);
  const emailHash = hashForLookup(email);

  try {
    const existing = await pool.query(
      'SELECT id, telephone_hash FROM users WHERE telephone_hash = $1 OR email_hash = $2',
      [telephoneHash, emailHash]
    );
    if (existing.rows[0]) {
      const message =
        existing.rows[0].telephone_hash === telephoneHash
          ? 'Ce numero de telephone est deja utilise'
          : 'Cet email est deja utilise';
      return res.status(409).json({ status: 'error', message });
    }

    let garageStatut = null;
    if (role === 'mecanicien') {
      const garage = await pool.query('SELECT id FROM garages WHERE id = $1', [garageId]);
      if (!garage.rows[0]) {
        return res.status(404).json({ status: 'error', message: 'Garage introuvable' });
      }
      // On tolere qu'un garage soit revendique par plusieurs comptes en attente
      // (donnees scrapees, pas de proprietaire "verifie" au depart) : l'admin
      // tranche a la validation. On bloque juste les doublons deja valides.
      const dejaValide = await pool.query(
        "SELECT id FROM users WHERE garage_id = $1 AND garage_statut = 'valide'",
        [garageId]
      );
      if (dejaValide.rows[0]) {
        return res.status(409).json({ status: 'error', message: 'Ce garage est deja revendique et valide par un autre compte' });
      }
      garageStatut = 'en_attente';
    }

    const hash = await bcrypt.hash(mot_de_passe, 10);

    const { rows } = await pool.query(
      `INSERT INTO users (nom, telephone, telephone_hash, email, email_hash, mot_de_passe_hash, role, garage_id, garage_statut)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
       RETURNING *`,
      [
        nom,
        encrypt(telephone),
        telephoneHash,
        encrypt(email),
        emailHash,
        hash,
        role,
        role === 'mecanicien' ? garageId : null,
        garageStatut,
      ]
    );

    const user = rows[0];

    logEvent('user_register', { role: user.role, garage_id: user.garage_id }, user.id);

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

  const { identifiant, mot_de_passe } = parsed.data;

  try {
    const identifiantHash = hashForLookup(identifiant);
    const { rows } = await pool.query(
      'SELECT * FROM users WHERE telephone_hash = $1 OR email_hash = $1',
      [identifiantHash]
    );
    const user = rows[0];

    if (!user || !user.mot_de_passe_hash) {
      return res.status(401).json({ status: 'error', message: 'Identifiants invalides' });
    }

    const valid = await bcrypt.compare(mot_de_passe, user.mot_de_passe_hash);
    if (!valid) {
      return res.status(401).json({ status: 'error', message: 'Identifiants invalides' });
    }

    if (!user.actif) {
      return res.status(403).json({ status: 'error', message: 'Ce compte a ete desactive' });
    }

    logEvent('user_login', {}, user.id);

    res.json({ user: toPublicUser(user), token: signToken(user) });
  } catch (err) {
    res.status(500).json({ status: 'error', message: err.message });
  }
});

module.exports = router;
