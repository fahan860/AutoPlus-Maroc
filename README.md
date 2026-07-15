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
/api      Backend Node.js + Express + PostgreSQL (API REST)
/mobile   App mobile React Native (Expo)
/ml       Notebooks et modèles ML (Python 3.10) : pricing véhicule, recommandation garage, détection faux avis
/data     Data Lake local (events applicatifs en Parquet, non versionné)
/docs     Documents projet : cahier des charges, dossier startup, guides d'entretien terrain, planning
```

## Ce qui a été fait — Semaine 1 (Setup complet)

- Environnement Docker + PostgreSQL/PostGIS configuré via `docker-compose.yml`
- Squelette API Node.js/Express (`/api`) avec route `/health` qui vérifie la connexion à la base de données
- Environnement Python 3.10 (venv) pour le ML, avec `requirements.txt` et un premier notebook d'exploration
  de données fictives (garages, véhicules) via Faker
- App mobile scaffoldée avec Expo (`/mobile`)
- Documents startup existants (cahier des charges, BMC, guides d'entretien, etc.) rangés dans `/docs`
- `.gitignore` et `.env.example` mis en place

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Docker + Docker Compose)
- Node.js 20+
- Python 3.10 (`py -3.10` doit fonctionner — voir `py -0p` pour lister les versions installées)
- Un téléphone avec l'app **Expo Go** (Android/iOS) pour tester le mobile, ou un émulateur

> **Note environnement Windows avec Avast** : si `pip install` échoue avec une erreur
> `CERTIFICATE_VERIFY_FAILED`, voir la solution documentée dans [`ml/README.md`](ml/README.md)
> (Avast intercepte le TLS avec son propre certificat, non reconnu par défaut par Python).

## Lancer le projet

### 1. API + Base de données (Docker)

```powershell
copy .env.example .env
docker compose up -d --build
```

Tester que tout fonctionne :

```powershell
curl http://localhost:3000/health
```

→ Réponse attendue : `{"status":"ok","db_time":"..."}`

En cas de problème :

```powershell
docker compose logs api
docker compose logs db
```

Arrêter les services :

```powershell
docker compose down
```

### 2. ML / Notebooks (Python)

```powershell
cd ml
py -3.10 -m venv venv          # si pas déjà fait
.\venv\Scripts\pip install -r requirements.txt
.\venv\Scripts\jupyter notebook notebooks/01_exploration.ipynb
```

→ Exécuter les cellules : doit afficher un tableau de 10 garages fictifs et 50 véhicules fictifs.

### 3. Mobile (Expo)

```powershell
cd mobile
npm install    # si pas déjà fait
npx expo start
```

→ Scanner le QR code avec l'app **Expo Go** sur ton téléphone, ou taper `w` pour ouvrir dans le navigateur.

### 4. Import des garages scrapés (Postgres)

Les CSV bruts (`data/scraping/garages*.csv`) viennent de 3 scrapes telecontact.ma qui se recoupent.
`merge_and_clean_garages.py` les fusionne en une seule fiche par garage (dédup par `lien_fiche`,
en gardant la valeur la plus complète entre les sources) et nettoie les champs (encodage UTF-8,
téléphone normalisé, note vidée si aucun vrai avis).

```powershell
cd data/scraping
python merge_and_clean_garages.py garages_casablanca_telecontact.csv garages.csv garages_v2.csv -o gar