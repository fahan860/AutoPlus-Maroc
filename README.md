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
          + pipeline de flush Redis -> Parquet (data/pipeline) + base de connaissance pannes/OBD-II
          pour le RAG de l'agent IA, pgvector (data/pannes)
/ai       Agent IA de diagnostic (RAG + LLM, futur service Python/FastAPI) : cadrage, schéma et corpus
          de la Knowledge Base (voir ai/docs/V1_SCOPE.md)
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
- Endpoints `vehicles` et `interventions` (CRUD véhicules, cycle de vie RDV `demande → confirme →
  en_cours → termine/annule`), protégés par JWT (`api/src/middleware/auth.js`)

### Semaine 3 — App mobile (automobiliste)

- Authentification (inscription / connexion), session persistée via `expo-secure-store`
- Écran Garages : liste triée par distance (géolocalisation `expo-location`) ou carte (`react-native-maps`)
- Écran Détail garage + prise de RDV (choix véhicule + type de panne)
- Écran Mes véhicules (liste + ajout)
- Écran Mes RDV (suivi du statut)
- Voir `mobile/src/` — `api/` (client HTTP), `context/AuthContext.js`, `navigation/`, `screens/`

### Semaine 4 — Sécurité des comptes, vérification email, garage par mécanicien, Agent IA (RAG)

- **Sécurité des comptes** : email désormais obligatoire à l'inscription (comme le téléphone), mot de
  passe soumis à une politique stricte (8 caractères min., majuscule, minuscule, chiffre, caractère
  spécial) avec checklist temps réel côté mobile, connexion possible par téléphone **ou** email
  (`POST /users/login` avec `identifiant`)
- **Vérification d'email** : code à 6 chiffres envoyé à l'inscription (`api/src/services/mailer.js`,
  SMTP configurable, code affiché dans les logs serveur en dev si SMTP absent) ; l'app mobile bloque
  l'accès (`VerifyEmailScreen`) tant que le compte n'est pas vérifié
- **Chiffrement des données personnelles** : téléphone et email sont chiffrés au repos en base
  (AES-256-GCM, `api/src/crypto.js`) avec un hash HMAC-SHA256 déterministe à côté pour permettre la
  recherche/l'unicité sans jamais comparer la valeur en clair (voir `api/migrations/005_encrypt_pii.sql`
  et le script de bascule `api/scripts/backfill-pii-encryption.js`)
- **Back-office admin retiré de l'app mobile** : le rôle admin et les routes `/admin/*` restent dans
  l'API (isolées, protégées par rôle + `ADMIN_SIGNUP_CODE`) en vue d'un outil séparé dédié, mais ne sont
  plus accessibles ni sélectionnables depuis l'app grand public
- **Garage créé directement par le mécanicien** (`CreateGarageScreen`), en plus de la revendication d'une
  fiche scrapée existante ; profil enrichi (adresse, ville)
- **Écran "Mes RDV"** : ajout d'une section "Prendre un rendez-vous" pour démarrer une réservation
  directement depuis cet écran
- **Agent IA — base de connaissance pannes (RAG, pgvector)** : `data/pannes/` — table `base_pannes`
  (50 pannes automobile réalistes, marché marocain) et table `codes_obd` (3071 codes OBD-II importés,
  catégorisés par mots-clés, reliés à `base_pannes` par similarité d'embedding quand la catégorie est
  fiable, 967/3071 reliés). Ce chantier est mené en parallèle du cadrage plus large de l'Agent IA (`/ai`,
  Phase 0-2 : `V1_SCOPE.md`, `KB_SCHEMA.md`, premier corpus `kb_corpus_v1.csv`) — les deux bases restent
  à faire converger.
- **Agent IA — base de données de la Knowledge Base (Phases 3-6)** : `ai/db/schema.sql` crée
  `kb_documents` (1 ligne par entrée du corpus, champs conformes à `KB_SCHEMA.md`) et `kb_chunks`
  (texte + embedding, index HNSW). `ai/scripts/load_kb_corpus.py` charge `kb_corpus_v1.csv`
  (22 entrées validées), génère les embeddings et les upsert. `ai/scripts/query_kb.py` implémente le
  retrieval combiné recherche vectorielle + filtres metadonnées (`systeme`, `vehicule`, `langue`,
  `gravite`), testé et fonctionnel en CLI comme en import (`search_kb(...)`, prêt à être appelé par le
  futur service agent).
- **Embeddings — passage à `intfloat/multilingual-e5-large`** (1024 dims, remplace
  `paraphrase-multilingual-MiniLM-L12-v2`, 384 dims, sur `base_pannes` et `kb_chunks`) : un test de
  retrieval a montré que MiniLM confondait des symptômes distincts (grincement au freinage classé après
  un cliquetis de direction sans rapport). e5-large corrige nettement le classement — vérifié sur les cas
  qui échouaient. Contrepartie : modèle ~2 Go, un peu plus lent par requête. Convention e5 à respecter
  partout : préfixer `"passage: "` les textes indexés, `"query: "` les requêtes utilisateur.
- **Agent IA — langue** : décidé en équipe (18/08/2026) — français **et** darija dès la V1, mais la KB
  et le retrieval restent 100% français ; c'est le LLM qui reformule la réponse finale en darija (voir
  `ai/docs/V1_SCOPE.md`). Testé avec Mistral : `mistral-small-latest` mélangeait français/darija et a
  inventé une cause hors contexte (rejeté) ; `mistral-medium-latest` produit une darija cohérente,
  correctement ancrée sur le contexte, et refuse de répondre plutôt que d'halluciner quand le retrieval
  ne remonte rien de pertinent — comportement à confirmer par un locuteur natif de l'équipe avant
  arbitrage final. Gemini testé mais bloqué : facturation non configurée sur le projet Google associé.
- Reste hors périmètre "base de données" : le service Python/FastAPI lui-même (Phase 7+), l'intégration
  LLM en production (Phase 8), l'écran mobile de chat (Phase 14) et les tests qualité (Phase 15).

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

**Important** : le téléphone doit être sur le **même réseau Wi-Fi** que la machine qui fait tourner
l'API (`docker compose up`). L'app détecte automatiquement l'IP locale de la machine de dev via Expo
(`hostUri`) — pas de configuration manuelle nécessaire. Pour forcer une autre URL (API déployée, etc.),
renseigner `expo.extra.apiUrl` dans `mobile/app.json`.

#### Tester sur un émulateur Android (au lieu d'un téléphone)

1. Installer [Android Studio](https://developer.android.com/studio), puis créer un appareil virtuel :
   ouvrir **Android Studio → More Actions → Virtual Device Manager → Create device** (choisir un
   Pixel récent + une image système Android 14/15, télécharger si besoin).
2. Démarrer l'émulateur créé (bouton ▶ dans le Virtual Device Manager), ou en ligne de commande :
   ```powershell
   emulator -avd <nom_de_l_avd>
   ```
3. Lancer l'app dessus :
   ```powershell
   cd mobile
   npx expo start
   ```
   puis appuyer sur `a` dans le terminal (ou `npx expo start --android` directement). Expo installe
   Expo Go sur l'émulateur automatiquement au premier lancement si besoin.
4. **Piège réseau propre aux émulateurs** : l'auto-détection par IP LAN (qui fonctionne très bien sur un
   téléphone physique) échoue en général sur un émulateur Android — le pare-feu Windows bloque souvent
   les connexions entrantes vers le port Docker (3000) depuis l'adaptateur réseau virtuel de l'émulateur,
   même si le port du bundler Metro (8081) passe (Node a déjà une autorisation pare-feu existante). Deux
   étapes pour contourner ça de façon fiable :
   ```powershell
   adb reverse tcp:3000 tcp:3000
   ```
   (à refaire à chaque redémarrage de l'émulateur), **et** forcer l'app à passer par ce tunnel au lieu de
   l'IP LAN, en renseignant dans `mobile/app.json` :
   ```json
   "extra": { "apiUrl": "http://localhost:3000" }
   ```
   Remettre `"apiUrl": null` pour retester sur un téléphone physique (l'auto-détection par IP LAN est ce
   qu'il faut dans ce cas).

> Un émulateur iOS (Xcode Simulator) n'est pas utilisable sur Windows — il faut un Mac. Sur Mac, aucun
> forward n'est nécessaire : le simulateur iOS partage directement le réseau de la machine hôte.

#### Carte des garages sur émulateur Android

En Expo Go sur émulateur Android, la carte (onglet "Carte") se charge mais affiche un fond vide (pas de
tuiles Google Maps) tant qu'aucune clé Google Maps API n'est renseignée dans
`mobile/app.json` → `expo.android.config.googleMaps.apiKey` — contrairement à ce qu'on pourrait attendre,
Expo Go ne fournit pas de clé de démo partagée pour ce SDK. La vue "Liste" (avec tri par distance) reste
utilisable sans configuration. Sur téléphone physique avec build autonome, même contrainte : une vraie
clé est nécessaire.

> La carte (onglet "Carte" dans Garages) fonctionne sans configuration dans **Expo Go**. Pour un build
> autonome (`expo prebuild` / EAS build), il faudra renseigner une vraie clé Google Maps dans
> `mobile/app.json` → `expo.android.config.googleMaps.apiKey`.

## Roadmap

Voir la synthèse complète dans la mémoire du projet et le planning détaillé semaine par semaine dans
[`docs/autoplus_planning_stage.html`](docs/autoplus_planning_stage.html) :

- **Juillet 2026** — Terrain + MVP complet (setup, BDD/API, app mobile, agent IA V1)
- **Août 2026** — Beta + 3 modèles ML en production (pricing, recommandation, détection faux avis)
- **Sept–Oct 2026** — Itération, paiement CMI, candidatures accélérateurs
- **Nov–Déc 2026** — Lancement public + pitch + rapport final
