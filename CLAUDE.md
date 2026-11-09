# AUTO+ (AutoPlus Maroc) — Guide pour Claude

Marketplace garages ↔ automobilistes au Maroc : app mobile B2C + espace garagiste, 3 modèles ML
et un agent IA de diagnostic (français / darija). PFA en binôme (Fatima Zahrae & Marouane),
planning de 26 semaines (juillet → décembre 2026), soutenance fin décembre 2026.
Pilote limité à Casablanca : les 123 garages en base y sont tous (91 géolocalisés).

## Architecture

| Dossier | Rôle | Stack |
|---|---|---|
| `api/` | API REST (port 3000) | Node.js + Express, PostgreSQL 16 (PostGIS + pgvector), Redis, JWT, zod |
| `api/migrations/` | Schéma BDD, `001` → `009`, SQL idempotent | — |
| `ml/` | Service ML FastAPI (port 8000, appelé uniquement par l'API) | Python, XGBoost, multilingual-e5-large, MLflow, Optuna |
| `ml/src/model_a` | Prix d'un véhicule d'occasion | XGBoost |
| `ml/src/model_b` | Recommandation de garages | e5-large + score spécialité/distance/note |
| `ml/src/model_c` | Détection de faux avis | gradient boosting + règle métier |
| `ml/src/agent` | Agent IA de diagnostic (RAG) | pgvector + LLM (Groq en test, Mistral prévu) |
| `mobile/` | App mobile | Expo SDK 57, React Native, React Navigation |
| `data/` | Scraping garages, pipeline events Redis → Parquet (`data/events/`, non versionné), base de pannes | Python |
| `ai/` | Cadrage et corpus de la base de connaissance de l'agent | — |
| `docs/` | Dossier startup, BMC, guides d'interview, planning, rapports ; `cahier-des-charges/`, `marche/` (CSV et notes, PDF en local), `diagrammes/`, `terrain/` (local uniquement : contient des numéros) | — |

## Commandes

```powershell
docker compose up -d --build                     # db, redis, ml-api, api
docker compose logs api                          # aussi : ml-api, db, redis
docker compose up -d --build --renew-anon-volumes api   # après ajout d'une dépendance npm
powershell -ExecutionPolicy Bypass -File .\lancer-tlf.ps1  # tout le premier lancement (Windows)
powershell -ExecutionPolicy Bypass -File .\activer-ia.ps1  # données de l'agent IA + embeddings

# Migrations (non automatiques, idempotentes) :
Get-ChildItem api\migrations\*.sql | Sort-Object Name | ForEach-Object {
  Get-Content $_.FullName -Raw | docker exec -i autoplus-db psql -q -U autoplus -d autoplus }

cd api; node scripts/import_garages_csv.js ../data/scraping/garages_clean.csv   # import garages
cd ml\service; ..\venv\Scripts\python -m pytest tests -q                        # 37 tests ML
cd mobile; npx expo start                                                        # app (Expo Go, même Wi-Fi)
```

## Règles de travail

- Une tâche = une branche = une Pull Request. Proposer un plan avant de coder une tâche non triviale.
- Toute modification de schéma = nouvelle migration numérotée (`010_...sql`), idempotente. Ne jamais modifier une migration existante.
- Après un changement côté ML, lancer les tests du service ; ne pas annoncer un résultat non mesuré.
- Données personnelles (téléphone, e-mail) chiffrées en AES-256-GCM (`api/src/crypto.js`) : ne jamais les stocker ni les logger en clair.
- Ne jamais lire, afficher ni committer `.env` ou `api/.env` (clés Groq/Mistral, JWT, SMTP). Utiliser `.env.example`.
- Chaque action utilisateur importante doit émettre un événement (`api/src/events.js`) : c'est la source des KPI marketing.
- Textes destinés aux utilisateurs : français et darija, ton simple et rassurant (voir le skill `autoplus-brand-voice`).
- Distinguer données réelles et simulées (modèle B en partie, modèle C entièrement simulés).

## Pièges connus

- `relation "users" does not exist` → migrations non appliquées.
- `extension "vector" is not available` → `docker compose up -d --build db`.
- Le premier démarrage de `ml-api` télécharge e5-large (~2,2 Go, jusqu'à 5 min).
- Vérification d'e-mail désactivée (`EMAIL_VERIFICATION_ENABLED=false`) tant que le SMTP n'est pas configuré.
- La refonte UI d'août (15 écrans mobiles) est sur la branche locale `refonte-ui-mobile-aout`, basée sur une ancienne version : la fusionner fichier par fichier, pas en bloc.
- Le dépôt est public : jamais de numéro de téléphone, de nom de mécanicien ou de document tiers sous licence dans un fichier versionné.

## Priorités restantes (novembre–décembre 2026)

1. Déploiement en ligne (Render ou Railway) + migrations automatiques au démarrage.
2. Événements du funnel marketing (ouverture app, vue garage, début/confirmation RDV, parrainage).
3. CI/CD GitHub Actions (tests + build à chaque PR).
4. Build bêta installable (Android d'abord).
5. Évaluation chiffrée de l'agent IA sur ~20 conversations FR/darija ; passage à Mistral.
6. Volet terrain : interviews (disposition à payer), 10–20 garages pilotes, bêta, pitch.

## Sous-agents disponibles (`.claude/agents/`)

- `marketing-analyst` : funnel et KPI à partir des événements Parquet et de PostgreSQL.
- `market-researcher` : concurrents, prix, tendances du marché marocain, avec sources.
- `content-creator` : posts, scripts vidéo, messages WhatsApp/Facebook en français et darija.
- `code-reviewer` : relecture d'une PR (sécurité, migrations, tests, données personnelles).
- `ml-engineer` : entraîner, évaluer et comparer les modèles A, B, C ; chiffres mesurés uniquement.
- `deploy-engineer` : mise en ligne (Render/Railway), migrations automatiques, CI/CD, build Android.
- `terrain-analyst` : guides d'interview FR/darija, disposition à payer, synthèse, garages pilotes.
- `academic-writer` : rapport PFA, rapport d'avancement, soutenance et questions du jury.

## Skills du projet (`.claude/skills/`, appelables en `/nom`)

- `/livrer-tache` : une tâche = une branche = une PR, de bout en bout.
- `/nouvelle-migration` : migration SQL numérotée, idempotente, testée deux fois.
- `/point-hebdo` : bilan de la semaine depuis git et les PR, entrées pour le journal du cockpit.
- `/evaluer-agent-ia` : évaluation chiffrée de l'agent sur ~20 conversations FR/darija.
- `autoplus-brand-voice` : ton et règles de tout texte destiné aux utilisateurs.

## Suivi du projet

- Cockpit (tâches, planning, risques, journal) : https://claude.ai/artifact/Apdhu5U4y9gKXhhAzHTqXb
- Affiche « Fonctionnement d'AUTO+ » : https://claude.ai/artifact/2Y3YWr8G7GvssodXuoxUgo
- Modèle de PR : `.github/pull_request_template.md`.
