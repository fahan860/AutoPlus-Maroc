# AUTO+ (AutoPlus Maroc)

Plateforme intelligente des services automobile au Maroc — mise en relation automobilistes ↔ garages,
diagnostic assisté par IA (darija/français), SaaS garage et marketplace pièces.

## Objectif du projet

Le Maroc compte 4,95M de véhicules et 18 000 besoins d'entretien/réparation par jour, mais 95% du secteur
n'est pas digitalisé. AUTO+ digitalise cette mise en relation via une app mobile B2C + un SaaS B2B pour
garages, avec un agent IA de diagnostic (darija/français).

Ce dépôt est aussi le support du PFA (Projet de Fin d'Année) : chaque semaine correspond à une étape du
planning de stage (voir [`docs/autoplus_planning_stage.html`](docs/autoplus_planning_stage.html)).

## Structure du dépôt

```
/api      Backend Node.js + Express + PostgreSQL/PostGIS (API REST) + Redis (events)
/mobile   App mobile React Native (Expo)
/ml       Notebooks et modèles ML (Python) : pricing véhicule, recommandation garage, détection faux avis
/data     Scraping garages (data/scraping) + Data Lake local en Parquet (data/events, non versionné)
          + pipeline de flush Redis -> Parquet (data/pipeline)
/docs     Documents projet : cahier des charges, dossier startup, guides d'entretien terrain, planning
```

## Ce qui a été fait

### Semaine 1 — Setup complet

- Environnement Docker + PostgreSQL/PostGIS configuré via `docker-compose.yml`
- Squelette API Node.js/Express (`/api`) avec route `/health` qui vérifie la connexion à la base de données
- Environnement Python (venv) pour le ML, avec `requirements.txt` et un premier notebook d'exploration
  de données fictives (garages, véhicules) via Faker
- App mobile scaffoldée avec Expo (`/mobile`)
- Documents startup existants (cahier des charges, BMC, guides d'entretien, etc.) rangés dans `/docs`
- `.gitignore` et `.env.example` mis en place

### Semaine 2 — BDD + API + Pipeline d'ingestion

- Schéma BDD complet : tables `garages`, `users`, `vehicles`, `interventions`, `reviews`, `events`
  (voir `api/migrations/`)
- Scraping et import de ~100 garages réels (Casablanca, via Telecontact.ma) dans la table `garages`
  (voir `data/scraping/` et `api/scripts/import_garages_csv.js`)
- Seed de données fictives (30 automobilistes + 50 véhicules) pour les tests
  (`api/scripts/seed_fake_users_vehicles.js`)
- 5 endpoints REST : `GET /garages`, `GET /garages/:id`, `POST /garages`, `POST /users/register`,
  `POST /users/login` (auth par mot de passe + JWT ; l'OTP SMS est prévu Semaine 3)
- Pipeline events : chaque action (recherche garage, inscription, connexion...) est loggée en JSON dans
  Redis (`events:queue`), puis vidée périodiquement vers le Data Lake Parquet par
  `data/pipeline/flush_events_to_parquet.py` (voir `data/README.md`)

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Docker + Docker Compose)
- Node.js 20+
- Python 3.10+ (`py -0p` pour lister les versions installées sur Windows)
- Un téléphone avec l'app **Expo Go** (Android/iOS) pour tester le mobile, ou un émulateur

> **Note environnement Windows avec Avast** : si `pip install` échoue avec une erreur
> `CERTIFICATE_VERIFY_FAILED`, voir la solution documentée dans [`ml/README.md`](ml/README.md)
> (Avast intercepte le TLS avec son propre certificat, non reconnu par défaut par Python).

## Lancer le projet

### 1. API + Base de données + Redis (Docker)

```powershell
copy .env.example .env
docker compose up -d --build
```

Tester que tout fonctionne :

```powershell
curl http://localhost:3000/health
```

→ Réponse attendue : `{"status":"ok","db_time":"..."}`

Endpoints disponibles : `GET /garages`, `GET /garages/:id`, `POST /garages`, `POST /users/register`,
`POST /users/login`.

En cas de problème :

```powershell
docker compose logs api
docker compose logs db
docker compose logs redis
```

Arrêter les services :

```powershell
docker compose down
```

### 2. ML / Notebooks / Pipeline events (Python)

```powershell
cd ml
py -3.13 -m venv venv          # si pas déjà fait (adapter la version selon `py -0p`)
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\jupyter notebook notebooks/01_exploration.ipynb
```

Pour vider la queue Redis vers le Data Lake Parquet (une fois l'API utilisée un minimum, pour
qu'il y ait des events à flush) :

```powershell
.\venv\Scripts\python ..\data\pipeline\flush_events_to_parquet.py
```

### 3. Mobile (Expo)

```powershell
cd mobile
npm install    # si pas déjà fait
npx expo start
```

→ Scanner le QR code avec l'app **Expo Go** sur ton téléphone, ou taper `w` pour ouvrir dans le navigateur.

## Roadmap

Voir la synthèse complète dans la mémoire du projet et le planning détaillé semaine par semaine dans
[`docs/autoplus_planning_stage.html`](docs/autoplus_planning_stage.html) :

- **Juillet 2026** — Terrain + MVP complet (setup, BDD/API, app mobile, agent IA V1)
- **Août 2026** — Beta + 3 modèles ML en production (pricing, recommandation, détection faux avis)
- **Sept–Oct 2026** — Itération, paiement CMI, candidatures accélérateurs
- **Nov–Déc 2026** — Lancement public + pitch + rapport final
