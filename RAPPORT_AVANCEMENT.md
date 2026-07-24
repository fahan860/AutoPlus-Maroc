# Rapport d'avancement — AUTO+ Maroc

**Projet** : AUTO+ (AutoPlus Maroc) — plateforme intelligente des services automobile
**Stagiaires** : Fatima Zahra Ahannuk & Marouane
**Période couverte** : Semaine 1 → Semaine 2 (30 juin – 16 juillet 2026)
**Référence planning** : [`docs/autoplus_planning_stage.html`](docs/autoplus_planning_stage.html) (26 semaines, juillet → décembre 2026)

---

## 1. Résumé exécutif

L'environnement technique complet (Docker, API, base de données, mobile, ML) est en place et fonctionnel depuis la Semaine 1. La Semaine 2 a été consacrée à la construction d'un pipeline de données réel pour l'annuaire des garages : **123 garages de Casablanca** ont été collectés depuis deux sources indépendantes (annuaire professionnel telecontact.ma et OpenStreetMap), nettoyés, dédupliqués et importés en base PostgreSQL/PostGIS — dont 23 avec géolocalisation exploitable.

En revanche, le schéma de base de données complet (véhicules, utilisateurs, interventions, avis), les endpoints API métier, le pipeline d'events (Data Lake), et le développement de l'app mobile restent à faire : le travail effectué a privilégié l'acquisition de données réelles plutôt que les données fictives (Faker) initialement prévues au planning, ce qui est une déviation volontaire et justifiée mais qui décale une partie du reste du contenu de la Semaine 2.

---

## 2. Ce qui a été fait

### Semaine 1 (30 juin – 6 juillet) — Setup complet ✅

- Environnement Docker + PostgreSQL/PostGIS opérationnel (`docker-compose.yml`)
- Squelette API Node.js/Express avec route `/health` (vérifie la connexion DB)
- Environnement Python 3.10 pour le ML (venv, `requirements.txt`, premier notebook d'exploration avec données fictives Faker)
- App mobile scaffoldée avec Expo (React Native) — écran par défaut, non personnalisé
- Documents startup (cahier des charges, BMC, guides d'entretien terrain) rangés dans `/docs`
- Test end-to-end validé (`curl /health` → connexion DB confirmée)
- Commit : `f0d2c1b`

### Semaine 2 (7 – 16 juillet) — Pipeline de données garages 🔶 (en cours)

**Ce qui était prévu au planning** : schéma BDD complet (6 tables), 5 endpoints API REST, pipeline d'events (Redis → Parquet), données de test fictives, 10 visites terrain.

**Ce qui a été réalisé à la place / en plus** — un pipeline de collecte de données réelles, plus ambitieux que le plan initial mais couvrant uniquement le périmètre "garages" :

1. **Table `garages` créée** en PostgreSQL/PostGIS (`api/migrations/001_create_garages.sql`) : nom, catégorie, adresse, ville, téléphone, note, nombre d'avis, source, géolocalisation (`GEOGRAPHY(POINT)`), flag `a_completer`.

2. **Scraping source 1 — telecontact.ma** (annuaire professionnel marocain, Fatima) :
   - Script `data/scraping/scraper_garages_telecontact.py`
   - 3 CSV bruts scrapés à des moments différents, fusionnés et dédupliqués (`merge_and_clean_garages.py`) par clé `lien_fiche`
   - Normalisation : téléphone au format marocain, notes (virgule → point), encodage UTF-8 + BOM pour compatibilité Excel FR/MA
   - Résultat : **100 garages uniques**, avec catégorie, adresse, note/avis réels quand disponibles

3. **Scraping source 2 — OpenStreetMap** (API Overpass, gratuite, Marouane) :
   - Script `data/scrape_garages_osm.py`
   - Requête géographique sur la bbox de Casablanca (`shop=car_repair`, `craft=car_repair`, `amenity=car_repair`)
   - Résultat : 35 points, dont 26 nommés — avec coordonnées GPS précises

4. **Fusion des deux sources** (`data/scraping/merge_osm_into_clean.py`, nouveau) :
   - Déduplication par comparaison de noms normalisés (accents/casse/ponctuation ignorés)
   - 9 points OSM sans nom exclus (non exploitables dans un annuaire), 3 doublons avec telecontact.ma exclus
   - **23 garages uniques ajoutés depuis OSM**, avec latitude/longitude

5. **Import en base** (`api/scripts/import_garages_csv.js`, étendu) :
   - Import idempotent par `UPSERT` sur `lien_fiche` (relancer l'import ne duplique jamais)
   - Peuplement automatique de la colonne géospatiale `geom` quand des coordonnées sont disponibles
   - **123 garages en base au total** : 100 telecontact.ma (sans géoloc) + 23 OpenStreetMap (avec géoloc complète)

6. **Incident résolu** : un bug d'écriture a corrompu plusieurs fichiers du pipeline en cours de session (octets nuls) ; Fatima a restauré ce qui était récupérable et abandonné proprement le seul fichier irrécupérable (données déjà intégrées ailleurs, aucune perte réelle).

**État actuel des données** :

| Source | Garages | Avec téléphone | Avec géolocalisation |
|---|---|---|---|
| telecontact.ma | 100 | 58 | 0 |
| OpenStreetMap | 23 | 3 | 23 |
| **Total** | **123** | **61** | **23** |

---

## 3. Écarts par rapport au planning initial

| Prévu (Semaine 2) | Statut |
|---|---|
| Schéma BDD complet : `vehicles`, `garages`, `users`, `interventions`, `events`, `reviews` | 🔴 Seule la table `garages` existe |
| 5 endpoints API REST (`POST /garages`, `GET /garages?lat=&lng=`, `POST /users/register`, `POST /users/login`, `GET /garages/:id`) | 🔴 Aucun endpoint métier — seule la route `/health` existe |
| Données de test fictives via Faker (10 garages, 50 véhicules) | 🟡 Fait en Semaine 1 (notebook), mais remplacé en pratique par des **données réelles** scrapées |
| Pipeline d'events → Redis → Parquet (Data Lake) | 🔴 Non commencé |
| 10 garages visités sur le terrain (Sidi Maarouf) | ⚪ Non trackable depuis le dépôt Git — à confirmer avec l'équipe |
| Rapport d'avancement N°2 | ⚪ À rédiger |

**Justification de la déviation** : l'équipe a choisi de bâtir un vrai jeu de données (123 garages réels géolocalisés) plutôt que des données 100% fictives — un choix pragmatique qui nourrira directement le futur modèle de recommandation (Modèle B, Semaine 7) et la carte de l'app mobile (Semaine 3). Ce choix a cependant pris le temps qui devait aller aux endpoints API et au schéma BDD complet.

---

## 4. Ce qui reste à faire

### Court terme — pour clôturer la Semaine 2
- [ ] Créer les tables manquantes : `vehicles`, `users`, `interventions`, `events`, `reviews`
- [ ] Développer les 5 endpoints API REST prévus (garages, auth utilisateur)
- [ ] Mettre en place le pipeline d'events (Redis → Parquet, structure `events/year=2026/month=07/day=DD/`)
- [ ] Enrichir les **42 garages telecontact.ma sans téléphone** (`a_completer = true`) — soit par nouvelle passe de scraping, soit par appel terrain
- [ ] Rédiger le Rapport d'avancement N°2 (schéma BDD, justification PostGIS, diagramme de flux — inclure le pipeline de scraping réalisé)

### Semaine 3 (14–20 juillet) — App mobile + terrain
- [ ] Écran d'accueil mobile + carte des garages (Google Maps API) — les 123 garages géolocalisés/à géolocaliser sont prêts à être consommés
- [ ] Écran profil garage, authentification OTP SMS
- [ ] Module de prise de RDV + dashboard mécanicien
- [ ] Visite des 10 garages restants sur le terrain, identification de 5 garages pilotes, 20 interviews automobilistes

### Semaine 4 (21–27 juillet) — Agent IA V1 + déploiement
- [ ] Intégration GPT-4o (darija/français), RAG basique avec pgvector
- [ ] Déploiement backend + BDD en ligne (Railway/Render), CI/CD GitHub Actions

---

## 5. Points de vigilance / dette technique

- **Deux pipelines de scraping en parallèle** (`data/scraping/` pour telecontact.ma, `data/` pour OSM) : fusionnés au niveau des données, mais pas au niveau du code — à harmoniser si une 3ᵉ source est ajoutée.
- **Script `data/scraping/clean_garages_csv.py`** semble redondant avec `merge_and_clean_garages.py` (même logique de normalisation, sur un seul fichier au lieu de trois) — à vérifier s'il est encore utilisé, sinon à supprimer.
- **Couverture géographique limitée à Casablanca** — conforme au planning actuel, mais à garder en tête pour l'expansion Rabat prévue en Semaine 22-24.
- **`docs/hdhdd.html`** : fichier non suivi à la racine de `/docs`, semble être une copie accidentelle du tracker de suivi de stage — à nettoyer ou renommer.
- **Fichier `garages_osm.csv` dupliqué** à la racine du dépôt et dans `/data` — à ne garder qu'à un seul endroit.
- **Configuration locale (`api/.env`)** non versionnée (normal, `.gitignore`) mais pas documentée dans le README pour le développement en local hors Docker — à ajouter si l'équipe travaille aussi en dehors des conteneurs.

---

## 6. Indicateurs clés au 16 juillet 2026

- **2/26 semaines** du planning de stage écoulées
- **123 garages** en base de données (objectif Semaine 7 : 20 garages sur la plateforme — déjà dépassé en volume de données brutes, mais aucun n'est encore "actif" côté produit/mobile)
- **61/123 garages** avec un numéro de téléphone valide
- **23/123 garages** géolocalisés (prêts pour une recherche "à proximité")
- **1 endpoint API** fonctionnel (`/health`) sur les 5 prévus
- **0 table BDD** sur les 6 prévues au-delà de `garages`
