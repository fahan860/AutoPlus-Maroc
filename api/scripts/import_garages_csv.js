/**
 * Importe un CSV de garages scrapes (colonnes: nom,categorie,adresse,ville,
 * telephone,note,nb_avis,lien_fiche) dans la table `garages` de PostgreSQL.
 *
 * Prerequis :
 *   - docker compose up -d (la base "db" doit tourner)
 *   - la migration api/migrations/001_create_garages.sql doit avoir ete
 *     executee une fois (voir README plus bas)
 *   - npm install (ajoute csv-parse)
 *
 * Usage (depuis le dossier api/) :
 *   node scripts/import_garages_csv.js ../data/scraping/garages_casablanca_clean.csv telecontact.ma
 *
 * Utilise le CSV NETTOYE (garages_casablanca_clean.csv, colonne a_completer
 * incluse), pas le CSV brut de scraping.
 *
 * Le script fait un UPSERT sur `lien_fiche` : relancer l'import avec un CSV
 * plus recent met a jour les lignes existantes au lieu de les dupliquer.
 */

require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { parse } = require('csv-parse/sync');
const { Pool } = require('pg');

async function main() {
  const [, , csvPathArg, sourceArg] = process.argv;

  if (!csvPathArg) {
    console.error('Usage: node scripts/import_garages_csv.js <chemin_csv> [source]');
    process.exit(1);
  }

  const csvPath = path.resolve(csvPathArg);
  const source = sourceArg || 'telecontact.ma';

  if (!fs.existsSync(csvPath)) {
    console.error(`Fichier introuvable : ${csvPath}`);
    process.exit(1);
  }

  const raw = fs.readFileSync(csvPath, 'utf-8');
  const rows = parse(raw, { columns: true, skip_empty_lines: true, trim: true });

  console.log(`${rows.length} lignes lues dans ${csvPath}`);

  const pool = new Pool({ connectionString: process.env.DATABASE_URL });

  let inserted = 0;
  let updated = 0;
  let skipped = 0;

  for (const row of rows) {
    if (!row.nom || !row.lien_fiche) {
      skipped += 1;
      continue;
    }

    const note = row.note && !isNaN(parseFloat(row.note)) ? parseFloat(row.note) : null;
    const nbAvis = row.nb_avis && !isNaN(parseInt(row.nb_avis, 10)) ? parseInt(row.nb_avis, 10) : 0;

    const aCompleter = row.a_completer
      ? String(row.a_completer).toLowerCase() === 'true'
      : !row.telephone;

    const result = await pool.query(
      `INSERT INTO garages (nom, categorie, adresse, ville, telephone, note, nb_avis, lien_fiche, source, a_completer, scraped_at)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, now())
       ON CONFLICT (lien_fiche) DO UPDATE SET
         nom = EXCLUDED.nom,
         categorie = EXCLUDED.categorie,
         adresse = EXCLUDED.adresse,
         ville = EXCLUDED.ville,
         telephone = EXCLUDED.telephone,
         note = EXCLUDED.note,
         nb_avis = EXCLUDED.nb_avis,
         source = EXCLUDED.source,
         a_completer = EXCLUDED.a_completer,
         updated_at = now()
       RETURNING (xmax = 0) AS inserted`, // xmax=0 => ligne neuve, sinon c'etait un update
      [
        row.nom,
        row.categorie || null,
        row.adresse || null,
        row.ville || 'Casablanca',
        row.telephone || null,
        note,
        nbAvis,
        row.lien_fiche,
        source,
        aCompleter,
      ]
    );

    if (result.rows[0].inserted) inserted += 1;
    else updated += 1;
  }

  await pool.end();

  console.log(`Import termine : ${inserted} inserees, ${updated} mises a jour, ${skipped} ignorees (donnees incompletes).`);
}

main().catch((err) => {
  console.error('Erreur import :', err);
  process.exit(1);
});
