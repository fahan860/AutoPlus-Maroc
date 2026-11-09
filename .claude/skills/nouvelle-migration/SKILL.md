---
name: nouvelle-migration
description: Créer une migration de base de données AUTO+ (nouvelle table, colonne, index, contrainte) au bon numéro, idempotente, et l'appliquer en local. À utiliser pour tout changement de schéma PostgreSQL.
---
# Nouvelle migration

1. Liste `api/migrations/` et prends le numéro suivant sur 3 chiffres (après `009_…` vient `010_…`). Nom : `NNN_verbe_objet.sql` en snake_case, ex. `010_add_funnel_events.sql`.
2. Ne modifie jamais une migration existante, même pour corriger une faute : crée-en une nouvelle.
3. Écris du SQL idempotent :
   - `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS`
   - `ALTER TABLE … ADD COLUMN IF NOT EXISTS`
   - contraintes et types dans un bloc `DO $$ BEGIN … EXCEPTION WHEN duplicate_object THEN NULL; END $$;`
   - en tête, un commentaire de 2 lignes : pourquoi cette migration, et quelle fonctionnalité l'utilise.
4. Données personnelles (téléphone, e-mail…) : colonne chiffrée + colonne de hachage, comme dans `005_encrypt_pii.sql`. Jamais en clair.
5. Applique-la deux fois de suite pour prouver l'idempotence :
   ```powershell
   Get-Content api\migrations\NNN_xxx.sql -Raw | docker exec -i autoplus-db psql -q -U autoplus -d autoplus
   ```
   La seconde exécution ne doit produire aucune erreur.
6. Mets à jour le code qui l'utilise (`api/src/routes/…`) et, si le schéma change le nombre de migrations, la ligne « Migrations de base » du `RAPPORT_AVANCEMENT.md`.
7. Rappelle dans la description de la PR que chaque membre doit appliquer la migration sur sa base tant que les migrations ne sont pas automatiques.
