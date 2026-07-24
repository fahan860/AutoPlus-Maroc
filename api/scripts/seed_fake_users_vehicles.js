/**
 * Seed de donnees fictives (Semaine 2) pour les tables `users` et `vehicles`.
 *
 * IMPORTANT : contrairement au plan initial ("10 garages fictifs"), la table
 * `garages` contient deja de vraies donnees scrapees (voir
 * scripts/import_garages_csv.js + data/scraping/garages_clean.csv), donc ce
 * script NE TOUCHE PAS a `garages`. Il seed uniquement les automobilistes et
 * leurs vehicules, pour pouvoir tester les futurs endpoints (RDV, avis...)
 * sans attendre les vraies inscriptions.
 *
 * Prerequis :
 *   - docker compose up -d (la base "db" doit tourner)
 *   - migrations 001 et 002 deja executees
 *   - npm install (ajoute @faker-js/faker)
 *
 * Usage (depuis le dossier api/) :
 *   node scripts/seed_fake_users_vehicles.js
 *
 * Idempotent : relancer le script ne duplique rien (ON CONFLICT DO NOTHING
 * sur telephone/plaque), grace a une seed Faker fixe (42, comme le notebook
 * ml/notebooks/01_exploration.ipynb).
 */

require('dotenv').config();
const { faker } = require('@faker-js/faker');
const { Pool } = require('pg');

const NB_USERS = 30;
const NB_VEHICLES = 50;
const MARQUES = ['Renault', 'Dacia', 'Peugeot', 'Volkswagen', 'Fiat'];

faker.seed(42);

async function main() {
  const pool = new Pool({ connectionString: process.env.DATABASE_URL });

  // ── Users (automobilistes fictifs) ──
  const userIds = [];
  let usersInserted = 0;

  for (let i = 0; i < NB_USERS; i += 1) {
    const nom = faker.person.fullName();
    const telephone = `06${faker.string.numeric(8)}`;
    const email = faker.internet.email({ firstName: nom.split(' ')[0] }).toLowerCase();

    const result = await pool.query(
      `INSERT INTO users (nom, telephone, email, role)
       VALUES ($1, $2, $3, 'automobiliste')
       ON CONFLICT (telephone) DO NOTHING
       RETURNING id`,
      [nom, telephone, email]
    );

    if (result.rows[0]) {
      userIds.push(result.rows[0].id);
      usersInserted += 1;
    }
  }

  // Si le script a deja tourne, on recupere les users existants pour pouvoir
  // quand meme leur rattacher des vehicules.
  if (userIds.length < NB_USERS) {
    const { rows } = await pool.query(
      `SELECT id FROM users WHERE role = 'automobiliste' ORDER BY id LIMIT $1`,
      [NB_USERS]
    );
    for (const row of rows) {
      if (!userIds.includes(row.id)) userIds.push(row.id);
    }
  }

  // ── Vehicles (rattaches aleatoirement aux users ci-dessus) ──
  let vehiclesInserted = 0;

  for (let i = 0; i < NB_VEHICLES; i += 1) {
    const userId = faker.helpers.arrayElement(userIds);
    const plaque = `${faker.number.int({ min: 1, max: 99999 })}-A-${faker.number.int({ min: 1, max: 99 })}`;

    const result = await pool.query(
      `INSERT INTO vehicles (user_id, plaque, marque, modele, annee)
       VALUES ($1, $2, $3, $4, $5)
       ON CONFLICT (plaque) DO NOTHING
       RETURNING id`,
      [
        userId,
        plaque,
        faker.helpers.arrayElement(MARQUES),
        faker.vehicle.model(),
        faker.number.int({ min: 2005, max: 2025 }),
      ]
    );

    if (result.rows[0]) vehiclesInserted += 1;
  }

  await pool.end();

  console.log(`Seed termine : ${usersInserted} users inseres (${userIds.length} disponibles au total), ${vehiclesInserted} vehicles inseres.`);
}

main().catch((err) => {
  console.error('Erreur seed :', err);
  process.exit(1);
});
