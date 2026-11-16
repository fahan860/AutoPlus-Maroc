# AUTO+ : index de la documentation et des sources (13)

> Point d'entrée unique. Les documents techniques et business sont séparés : **01–06 = technique et suivi** (racine du Project), **07–13 = business** (dossier `business/` du Project).
> Dates : « Project » = date d'ajout dans le Project claude.ai ; « contenu » = date indiquée dans le document. Dépôt = `fahan860/AutoPlus-Maroc`, branche `main`, dernier commit vérifié le 2026-11-09 (merge PR #8).
> Dernière mise à jour : 2026-11-16.

## 1. Documents du Project claude.ai

### Technique et suivi (inchangés le 2026-11-16)
| # | Fichier | Contenu | Équivalent dans le dépôt | Dates |
|---|---|---|---|---|
| 01 | `01_guide_projet_CLAUDE.md` | Architecture, commandes, règles, pièges, priorités nov.–déc. | `CLAUDE.md` | Project 2026-11-09 |
| 02 | `02_agents_roles.md` | 8 rôles (techniques + marketing) | `.claude/agents/*.md` | Project 2026-11-09 |
| 03 | `03_skills_procedures.md` | 5 procédures (livrer-tache, nouvelle-migration, point-hebdo, evaluer-agent-ia, autoplus-brand-voice) | `.claude/skills/*/SKILL.md` | Project 2026-11-09 |
| 04 | `04_permissions_et_PR.md` | Permissions Claude Code, modèle de PR | `.claude/settings.json`, `.github/pull_request_template.md` | Project 2026-11-09 |
| 05 | `05_README.md` | README du dépôt (installation, historique S1–S4, modèle A) | `README.md` | Project 2026-11-09 |
| 06 | `06_RAPPORT_AVANCEMENT.md` | Rapport d'avancement S1–S14 | `RAPPORT_AVANCEMENT.md` | contenu au 2026-10-03 |

### Business (créés le 2026-11-16)
| # | Fichier | Contenu | Rôle propriétaire |
|---|---|---|---|
| 07 | `07_strategie_startup.md` | Vision, problème, segments, personas, **statut réel des fonctionnalités**, proposition de valeur, BMC, revenus, prix, positionnement | Startup Strategist / Business Strategist |
| 08 | `08_marche_concurrence.md` | Vérification des chiffres du dossier, TAM/SAM/SOM, concurrents Maroc, modèles internationaux, paiement et réglementation, sources | Market Researcher / Competitor Analyst |
| 09 | `09_gtm_lancement_casablanca.md` | Marché initial, phases P0–P3, cold start, garages, automobilistes, partenariats, budget | GTM Strategist |
| 10 | `10_kpi_experiences.md` | North Star Metric, funnel ↔ événements, CAC/LTV, expériences, journal de décisions | Growth Lead |
| 11 | `11_roles_business.md` | CSO + 10 rôles business | CSO |
| 12 | `12_procedures_business.md` | 8 procédures business | CSO |
| 13 | `13_index_sources.md` | Ce document | CSO |

### Navigation rapide
| Je veux… | Lire |
|---|---|
| coder / déployer / tester | 01, 03, 04, 05 |
| savoir où en est le projet | 06 (technique), 10 §7 (décisions), cockpit |
| préparer la soutenance | 06, 07, 08, `academic-writer` (02), `revue-pitch` (12) |
| parler à des garages ou automobilistes | 09, `customer-discovery` (12), `autoplus-brand-voice` (03) |
| citer un chiffre de marché | 08 §1 (statut de vérification) puis 08 §9 (sources) |
| fixer un prix | 07 §7–8, `validation-prix` (12) |
| lancer une campagne / expérience | 09, 10 §6, `plan-campagne`, `design-experience` (12) |

## 2. Documents business existants dans le dépôt (`docs/`)

| Document | Contenu | Date du contenu | Statut / remarque |
|---|---|---|---|
| `AutoPlus_Maroc_Dossier_Startup_2026_CORRIGE.pdf` | Dossier stratégique 16 p. : marché, garages, digital, Google Trends, concurrence, revenus, TAM/SAM/SOM, roadmap | mai 2026 | **Chiffres partiellement non vérifiés** (voir 08 §1) ; roadmap dépassée |
| `AutoPlus_Lean_BMC.pptx` | Lean Business Model Canvas, 1 slide | mai 2026 | Repris et mis à jour dans 07 §6 |
| `AutoPlus_Assumption_Matrix.xlsx` | 20 hypothèses (H1–H20), risque, certitude, priorité | mai 2026 | Toutes « À valider » |
| `AutoPlus_Analyse_CustomerDiscovery.docx` | Alignement matrice ↔ guide ; 7 questions manquantes | mai 2026 | Recommandations à intégrer au guide |
| `AutoPlus_Guide_Interview_V2.docx` | Guide d'entretien A1–A7 / B1–B7 + fiche de synthèse + tracker | 2025–2026 | Tracker vide (0 entretien) |
| `AutoPlus_Guide_Interview_Terrain.docx` | Première version du guide | — | Remplacée par V2 |
| `AutoPlus_Fiche_PFA.docx` | Fiche PFA (objectifs, livrables) | 2025–2026 | Encadrant non renseigné |
| `AutoPlus_Plan_Organisation_PreDev.docx` | Plan MVP web, risques, objectifs CQFD | juillet 2026 | MVP web Next.js remplacé par l'app Expo (10 §7) |
| `AutoPlus_Checklist_Avancement.md` | Checklist par phase | — | **Obsolète** : phases 3–5 non cochées alors que l'app mobile existe |
| `AutoPlus_Suivi_Projet.xlsx` | 31 tâches mai–sept. 2026 | mai 2026 | Obsolète ; remplacé par le cockpit |
| `marche/recherche de users.docx` | Estimation 18 000 besoins/jour, volumes de recherche | mai 2026 | Estimations, volumes « Keyword Planner » non sourcés |
| `marche/chiffres(automobile market,digitalisation).docx` | Chiffres marché et digital | mai 2026 | **Transcription d'une conversation avec un chatbot** : ne pas citer comme source |
| `marche/HCP....docx` | Chiffres HCP / OFPPT | 2024 (données) | Plus prudent ; liens HCP à retrouver |
| `marche/*.csv` | Exports Google Trends (séries, géographie) | 2021–2026 | Données brutes exploitables |
| `cahier-des-charges/*.docx` (v1–v3) | Cahier des charges | 2026 | — |
| `autoplus_planning_stage.html`, `autoplus_roadmap.html`, `AutoPlus_Presentation_Avancement.html`, diagrammes | Planning 26 semaines, roadmap, conception | 2026 | Techniques / académiques |
| `ml/AUTO+_Partie_Machine_Learning.pdf` | Document IA détaillé | oct. 2026 | Technique |
| `docs/terrain/` | Listes d'ateliers, notes nominatives | — | **Local uniquement**, non versionné |

## 3. Données et références techniques utiles au business

| Élément | Emplacement | Usage business |
|---|---|---|
| 123 garages de Casablanca (91 géolocalisés) | `data/scraping/garages_clean.csv` | pipeline garages, choix des quartiers (09 §1) |
| Événements utilisateurs | `api/src/events.js` → `data/events/` (Parquet, local) | funnel et KPI (10) |
| Résultats ML | `ml/reports/*.json` | pitch : chiffres mesurés uniquement, réel vs simulé |
| Base de pannes et codes OBD | `data/pannes/` | contenu « conseils entretien » |

## 4. Suivi et artefacts

- Cockpit (tâches, planning, risques, journal) : https://claude.ai/artifact/Apdhu5U4y9gKXhhAzHTqXb
- Affiche « Fonctionnement d'AUTO+ » : https://claude.ai/artifact/2Y3YWr8G7GvssodXuoxUgo
- Démo Streamlit (modèle A) : https://fahan-autoplus.streamlit.app
- Étude de cas portfolio : https://fatima-zahrae-ahannuk.vercel.app/projects/autoplus

## 5. Sources externes

Liste complète, datée et numérotée (S1–S53) : `08_marche_concurrence.md` §9, avec la liste des sources non accessibles.

## 6. Documents manquants

| Document | Pourquoi il manque | Rôle | Priorité |
|---|---|---|---|
| Synthèse des entretiens terrain | 0 entretien réalisé | Customer Researcher | **Critique** avant soutenance |
| Audit Google Maps des 123 garages (EXP-04) | non fait | Garage Partnerships Manager | Haute |
| Relevé de prix terrain Casablanca (vidange, diagnostic, main-d'œuvre) | prix publiés anciens ou nationaux | Market Researcher | Haute |
| Hypothèses financières recalculées | projections de mai 2026 non adossées | Business Strategist | Moyenne |
| Mentions légales, CGU, politique de confidentialité | bêta non lancée | [À COMPLÉTER : responsable] | Haute avant P1 |
| Évaluation chiffrée de l'agent IA | priorité technique 5 | ml-engineer | Haute |
| Fiches concurrent détaillées (Carabas, ReparTrust, Piassaty) | sites non lisibles ou activité non vérifiée | Competitor Analyst | Moyenne |
| Version corrigée du dossier startup (`dossier-startup-v2`) | chiffres corrigés dans 08 §1, PDF non modifié | Market Researcher | Haute avant soutenance |
| Déclaration CNDP, choix du statut juridique | obligations identifiées (08 §6) | [À COMPLÉTER : responsable] | Haute avant P1 |
| Pitch deck business | — | Pitch Coach | Avant soutenance |
