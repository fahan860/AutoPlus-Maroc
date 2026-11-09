# AUTO+ Maroc — Checklist d'avancement

> Ordre réel adopté : plateforme (conception → dev) d'abord, terrain remis au planning, agent IA développé après que le cœur de la plateforme soit posé.
> MVP lancé en **web d'abord** (Next.js), app mobile native développée **après** validation de la beta.
> Coche au fur et à mesure (`- [ ]` → `- [x]`).

---

## Phase 0 — Conception ✅ TERMINÉE (Semaine 1)

- [x] Cahier des charges rédigé (10 sections)
- [x] Validation/signature cahier des charges
- [x] Choix stack technique figé (Node.js/Express, PostgreSQL+PostGIS, React Native, Python/ML)
- [x] Structure repo créée (`/api`, `/mobile`, `/ml`, `/data`, `/docs`)
- [x] Environnement Docker + PostgreSQL + Python + Node configuré

## Phase 1 — Fondations Backend + Data ✅ TERMINÉE (Semaine 2)

- [x] Schéma BDD complet (garages, users, vehicles, interventions, reviews, events)
- [x] Données de test injectées (garages, véhicules fictifs)
- [x] Scraping + import ~100 garages réels (Casablanca)
- [x] 5 endpoints REST de base (garages CRUD, register, login)
- [x] Pipeline events Redis → Parquet (Data Lake)

## Phase 2 — Terrain (reporté, à replanifier)

- [ ] Liste des 20 garages à visiter finalisée
- [ ] Script d'entretien garages/automobilistes prêt
- [ ] Visites terrain effectuées (garages)
- [ ] Interviews automobilistes menées
- [ ] Garages pilotes identifiés et engagés
- [ ] Synthèse des retours terrain rédigée

*(Statut : reporté — à réintégrer dans le planning une fois la plateforme suffisamment avancée pour être démontrée sur le terrain)*

## Phase 3 — Architecture & Design plateforme

- [ ] Wireframes des écrans clés (accueil, profil garage, RDV, profil user)
- [ ] Maquettes UI haute fidélité (Figma ou équivalent)
- [ ] Design system (couleurs, composants réutilisables)
- [ ] Schéma d'architecture technique finalisé (couches, flux de données)
- [ ] Documentation API (Swagger/OpenAPI) démarrée

## Phase 4 — Développement Backend (cœur métier)

- [ ] Endpoint recherche garages géolocalisée (`GET /garages?lat=&lng=`)
- [ ] Module prise de RDV (création, confirmation, refus)
- [ ] Authentification complète (OTP SMS ou email + JWT)
- [ ] Dashboard garagiste (gestion des demandes RDV)
- [ ] Notifications (push ou email) RDV confirmé / nouvelle demande
- [ ] Tests unitaires + tests d'intégration API

## Phase 5 — Développement Web (MVP, Next.js)

- [ ] Setup projet Next.js (responsive mobile-first)
- [ ] Écran accueil + carte garages (Google Maps API / Leaflet)
- [ ] Écran profil garage (photos, spécialités, avis)
- [ ] Flux de prise de RDV côté client
- [ ] Écran profil utilisateur + historique véhicule
- [ ] Dashboard garagiste (web, desktop-friendly)
- [ ] Notifications email/WhatsApp en fallback (pas de push natif au MVP)
- [ ] Tests responsive (mobile + desktop, plusieurs navigateurs)

## Phase 6 — Déploiement & CI/CD

- [ ] Déploiement backend en ligne (Railway/Render ou équivalent)
- [ ] Base de données en production
- [ ] Pipeline CI/CD (push → tests → build → déploiement auto)
- [ ] Environnements séparés (dev/staging/prod)
- [ ] Monitoring de base (logs, uptime)

## Phase 7 — Agent IA (après plateforme stable)

- [ ] Intégration API GPT-4o (ou modèle équivalent)
- [ ] Prompt système darija/français
- [ ] RAG basique (pgvector + base de pannes)
- [ ] Output structuré (diagnostic, urgence, conseil, garages, prix estimé)
- [ ] Tests avec questions réelles darija/français
- [ ] Intégration de l'agent dans l'app mobile

## Phase 8 — Modèles ML (post-MVP)

- [ ] Pipeline nettoyage + feature engineering
- [ ] Modèle A — Pricing véhicule (XGBoost)
- [ ] Modèle B — Recommandation garage (hybride)
- [ ] Modèle C — Détection faux avis
- [ ] Modèles loggés/versionnés (MLflow)
- [ ] Endpoints ML exposés en API

## Phase 9 — Beta & Lancement (web)

- [ ] Reprise du terrain : garages pilotes onboardés
- [ ] Beta fermée lancée (premiers utilisateurs réels, via lien web)
- [ ] Collecte feedback + itérations rapides
- [ ] Tests de charge avant ouverture publique
- [ ] Lancement public (web)

## Phase 10 — App mobile native (post-validation)

*(À lancer une fois la beta web validée : signal produit confirmé, usage réel mesuré)*

- [ ] Reprise du scaffold Expo (`/mobile`), portage des écrans validés côté web
- [ ] Notifications push natives
- [ ] Fonctionnalités device (caméra, géoloc native, mode offline si besoin)
- [ ] Publication App Store / Google Play (screenshots, descriptions FR/AR/Darija, politique de confidentialité)
- [ ] Lancement app mobile

---

## Vue d'ensemble rapide

| Phase | Statut |
|---|---|
| 0. Conception | ✅ Terminé |
| 1. Fondations Backend + Data | ✅ Terminé |
| 2. Terrain | ⏸️ Reporté |
| 3. Architecture & Design | 🔲 À faire |
| 4. Backend cœur métier | 🔲 À faire |
| 5. Web (MVP, Next.js) | 🔲 À faire |
| 6. Déploiement & CI/CD | 🔲 À faire |
| 7. Agent IA | 🔲 À faire (après plateforme) |
| 8. Modèles ML | 🔲 À faire (post-MVP) |
| 9. Beta & Lancement (web) | 🔲 À faire |
| 10. App mobile native | 🔲 À faire (post-validation) |
