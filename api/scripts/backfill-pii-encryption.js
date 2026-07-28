/**
 * Chiffre en place le telephone/email des utilisateurs encore en clair
 * (crees avant l'introduction du chiffrement, voir migrations/005_encrypt_pii.sql)
 * et renseigne leurs colonnes de hash. Idempotent : ne retraite pas les
 * lignes ou telephone_hash est deja renseigne.
 *
 * Usage : node api/scripts/backfill-pii-encryption.js
 */

require('dotenv').config();
const { pool } = require('../src/db');
const { encrypt, hashForLookup } = require('../src/crypto');

async function run() {
  const { rows } = await pool.query(
    'SELECT id, telephone, email FROM users WHERE telephone_hash IS NULL'
  );

  for (const row of rows) {
    await pool.query(
      'UPDATE users SET telephone = $1, telephone_hash = $2, email = $3, email_hash = $4 WHERE id = $5',
      [
        encrypt(row.telephone),
        hashForLookup(row.telephone),
        row.email ? encrypt(row.email) : null,
        row.email ? hashForLookup(row.email) : null,
        row.id,
      ]
    );
    console.log(`Utilisateur ${row.id} chiffre`);
  }

  console.log(`${rows.length} utilisateur(s) traite(s)`);
  await pool.end();
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
