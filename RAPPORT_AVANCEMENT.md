# Rapport d'avancement — AUTO+ Maroc

**Projet** : AUTO+ (AutoPlus Maroc) — plateforme intelligente des services automobile
**Stagiaires** : Fatima Zahra Ahannuk & Marouane
**Période couverte** : Semaine 1 → Semaine 14 (30 juin – 3 octobre 2026)
**Référence planning** : [`docs/autoplus_planning_stage.html`](docs/autoplus_planning_stage.html) (26 semaines, juillet → décembre 2026)
**Document détaillé de la partie IA** : [`ml/AUTO+_Partie_Machine_Learning.pdf`](ml/AUTO+_Partie_Machine_Learning.pdf)

---

## 1. Résumé exécutif

Le produit de base est en place : API, base de données, pipeline d'événements et application mobile (automobiliste et mécanicien), avec authentification sécurisée et données personnelles chiffrées. Les **trois modèles de Machine Learning** du planning et l'**agent IA de diagnostic** sont livrés de bout en bout : données, modèle, service, écran mobile testé sur iPhone.

| Composant IA | Résultat principal | Données |
|---|---|---|
| Modèle A — prix d'un véhicule d'occasion | Erreur moyenne 11 779 DH (10,8 %), R² 0,939 | Réelles (101 896 annonces) |
| Modèle B — recommandation de garages | 87,5 % des pannes bien comprises, 93 % de garages pertinents | Réelles + simulées (choix des clients) |
| Modèle C — détection de faux avis | Précision 100 %, rappel 84 % | Simulées (2 980 avis) |
| Agent IA de diagnostic | Question ou analyse sourcée en ~3 s, français et darija, garages proposés | Réelles (22 entrées + 50 pannes) |

**Retard sur le planning** : le travail réalisé correspond aux semaines 1 à 7 du planning (et à une partie de la semaine 8). Le déploiement en ligne, la CI/CD, le monitoring et les volets terrain et business (bêta, garages pilotes, paiement) n'ont pas commencé.

---

## 2. Ce qui a été fait

### Semaines 1–2 — Socle technique et données (juillet)

- Docker (PostgreSQL/PostGIS, Redis), API Node.js/Express, application Expo, environnement Python.
- Schéma de base complet : `garages`, `users`, `vehicles`, `interventions`, `reviews`, `events`.
- **123 garages réels** de Casablanca (telecontact.ma + OpenStreetMap), nettoyés, dédupliqués, importés.
- Endpoints REST (garages, inscription, connexion JWT, véhicules, interventions avec cycle de vie du RDV).
- Pipeline d'événements : chaque action est journalisée dans Redis puis vidée vers un Data Lake Parquet.

### Semaine 3 — Application mobile (fin juillet)

- Inscription avec choix du rôle (automobiliste, mécanicien), revendication de garage, tableau de bord garagiste.
- Garages en liste et sur carte, fiche garage, prise de RDV, véhicules, suivi des RDV, avis.
- Détection automatique de l'adresse de l'API sur le réseau local.

### Semaine 4 — Sécurité et base de connaissance IA (fin juillet – août)

- E-mail obligatoire, politique de mot de passe, connexion par téléphone ou e-mail.
- Vérification de l'e-mail par code (désactivable : `EMAIL_VERIFICATION_ENABLED`, voir § 5).
- **Chiffrement des données personnelles** (téléphone, e-mail) en AES-256-GCM, recherche par hachage.
- Création de garage par le mécanicien ; back-office admin retiré de l'app grand public.
- Base de connaissance de l'agent IA : 50 pannes, 3 071 codes OBD-II, 22 entrées validées, recherche vectorielle (pgvector, multilingual-e5-large) ; choix de Mistral pour la darija après test.

### Modèle A — Estimation du prix d'un véhicule (PR #2, 30 septembre)

- Jeu public MUCars-2024 (101 896 annonces, Université Abdelmalek Essaâdi, CC BY 4.0), nettoyé par 10 règles → 70 368 annonces.
- 5 modèles comparés dans les mêmes conditions (médiane, régression linéaire, Random Forest, XGBoost, CatBoost) → **XGBoost**, réglé avec Optuna (40 essais, MLflow).
- Résultat sur un jeu de test jamais vu : erreur moyenne **11 779 DH (10,8 %)**, R² 0,939, 81 % des annonces à ±15 %.
- Service FastAPI (`POST /predict/vehicle-value`), route `POST /vehicles/estimate`, écran **« Estimer mon véhicule »** (prix, fourchette, fiabilité).

### Modèle B — Recommandation de garages (PR #3, 2 octobre)

- Collecte des fiches Telecontact : **91 garages géolocalisés sur 123** (contre 23) ; spécialités enregistrées avec leur source (migration 007).
- Classification de la panne par multilingual-e5-large : 87,5 % de bonnes catégories (MiniLM 67,5 %, mots-clés 40 %).
- Score = 40 % spécialité + 50 % distance + 10 % note bayésienne ; **93 % de garages pertinents** dans le top 5, à 2,6 km en moyenne.
- Biais corrigé grâce à une mesure de diversité : avec les premiers poids, un seul garage (dont la fiche liste les 10 spécialités) sortait 1er dans 100 % des cas ; désormais aucun ne dépasse 20 %.
- Filtrage collaboratif SVD sur données simulées : 45 % contre 32 % pour le contenu seul (démonstration).
- Service `POST /recommend/garages`, écrans **« Quel est le problème ? »** et **« Garages conseillés »**.

### Modèle C — Détection de faux avis (PR #4, 2 octobre)

- 2 980 avis simulés, 4 types de fraude dont un absent de l'entraînement.
- 4 méthodes comparées : les modèles appris détectent 100 % des fraudes connues mais 0 % de la fraude jamais vue ; une règle métier compense. Système retenu : gradient boosting + règle « avis sur un RDV annulé » → **précision 100 %, rappel 84 %**, aucun vrai avis masqué.
- Modération à la publication (migration 008) : avis suspect masqué jusqu'à la décision d'un admin (`/admin/reviews/...`).
- Testé sur iPhone et par 4 scénarios sur l'API réelle.

### Agent IA de diagnostic (PR #5, 3 octobre)

- Conversation en français ou en darija : question de précision, puis analyse prudente et sourcée (causes, vérifications sans risque, gravité) et 3 garages conseillés.
- Reformulation en français avant la recherche (corrige la compréhension de la darija), garde-fous (sources vérifiées, gravité plancher, 2 questions maximum, alerte de sécurité, refus hors sujet).
- LLM configurable : Groq gratuit pour les tests, Mistral (choix de l'équipe) dès que son API est activée.
- Service `POST /agent/chat`, onglet **Assistant** et **historique des conversations** (migration 009).

### Transverse

- **Migration vers Expo SDK 57** (Expo Go sur iOS n'accepte que le dernier SDK), `expo-doctor` 21/21.
- **Bugs corrigés** : l'API redémarrait en boucle (module `nodemailer` absent du conteneur) ; la vérification d'e-mail cassée (migration 006 non appliquée) ; la note d'un garage effaçait ses avis Telecontact à chaque nouvel avis ; les avis de l'app n'étaient pas rattachés au RDV.
- Service ML dans Docker : 4 composants chargés une fois, **37 tests automatiques** (15 A, 9 B, 5 C, 8 agent).
- Documentation : README, notebooks et figures (`ml/notebooks`, `ml/reports`), document IA en PDF.

---

## 3. Écarts par rapport au planning

| Prévu | Statut |
|---|---|
| S1–S4 : setup, BDD, API, app, agent IA V1 | ✅ fait (agent : évaluation chiffrée restante) |
| S4 : déploiement en ligne + CI/CD | 🔴 non commencé |
| S5 : pipeline de nettoyage, feature store | 🟡 nettoyage et variables faits par modèle, pas de feature store commun |
| S6–S7 : modèles A, B, C + MLflow + FastAPI | ✅ fait |
| S8 : agent IA V2, Docker complet | 🟡 Docker complet fait ; agent V2 non commencé |
| S9 : tests de charge, monitoring | 🔴 non commencé |
| S10–S13 : A/B testing, Airflow, paiement CMI, WhatsApp, préparation App Store | 🔴 non commencé |
| Terrain : visites de garages, bêta fermée, 20 interviews | ⚪ non suivi dans le dépôt — à confirmer avec l'équipe |

**Justification** : la priorité a été donnée à des composants IA complets et mesurés (données réelles quand elles existaient, comparaisons honnêtes, tests), plutôt qu'à une couverture superficielle de toutes les semaines.

---

## 4. Ce qui reste à faire (par priorité)

1. **Agent IA** : évaluation chiffrée sur ~20 conversations ; validation de la darija par un locuteur natif ; passage à Mistral.
2. **Déploiement en ligne** (Railway ou Render) pour la démonstration au jury.
3. **CI/CD** (GitHub Actions) : tests et build à chaque Pull Request.
4. Fusionner la base de pannes et la base de connaissance de l'agent ; ajouter les termes manquants (« plaquettes », « amortisseurs »).
5. Application automatique des migrations de base.
6. En fin de projet : configuration SMTP puis réactivation de la vérification d'e-mail.
7. Volets terrain et business : confirmation des spécialités des garages pilotes, bêta, pitch.

---

## 5. Points de vigilance

- **Données simulées** pour le filtrage collaboratif (B) et les faux avis (C) : preuves de concept, pas des performances réelles.
- **Spécialités des garages** : 104 sur 123 sont une hypothèse « mécanique générale », à confirmer sur le terrain.
- **Vérification d'e-mail désactivée** (`EMAIL_VERIFICATION_ENABLED=false`) tant qu'aucun envoi d'e-mail n'est configuré.
- **LLM** : l'API Mistral demande un plan payant ; Groq (gratuit) produit une darija imparfaite.
- **Migrations manuelles** : chaque membre doit appliquer 006 à 009 sur sa base (oubli déjà arrivé).

---

## 6. Indicateurs clés au 3 octobre 2026

| Indicateur | Valeur |
|---|---|
| Semaines écoulées | 14 / 26 |
| Garages en base | 123, dont 91 géolocalisés |
| Composants IA en service | 4 (modèles A, B, C + agent) |
| Tests automatiques du service ML | 37 |
| Pull Requests fusionnées | 5 |
| Migrations de base | 9 |
| Écrans mobiles ajoutés pour l'IA | 6 (estimation, résultat, ma panne, garages conseillés, assistant, historique) |
