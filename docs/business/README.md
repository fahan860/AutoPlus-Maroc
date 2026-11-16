# Documentation business AUTO+ (07–13)

Copie versionnée des documents business du Project claude.ai « Auto+ » (dossier `business/`, version du 2026-11-16). Le contenu des fichiers 07 à 13 est repris tel quel : le Project reste la source de rédaction, et ce dossier est mis à jour par PR à chaque nouvelle version.

## Correspondance des numéros cités dans les documents

Les documents renvoient aux autres par leur numéro (`01`, `08` §5…). Dans le dépôt :

| Numéro | Fichier du Project | Fichier du dépôt |
|---|---|---|
| 01 | `01_guide_projet_CLAUDE.md` | [`CLAUDE.md`](../../CLAUDE.md) |
| 02 | `02_agents_roles.md` | [`.claude/agents/`](../../.claude/agents/) |
| 03 | `03_skills_procedures.md` | [`.claude/skills/`](../../.claude/skills/) |
| 04 | `04_permissions_et_PR.md` | [`.claude/settings.json`](../../.claude/settings.json), [`.github/pull_request_template.md`](../../.github/pull_request_template.md) |
| 05 | `05_README.md` | [`README.md`](../../README.md) |
| 06 | `06_RAPPORT_AVANCEMENT.md` | [`RAPPORT_AVANCEMENT.md`](../../RAPPORT_AVANCEMENT.md) |
| 07 | `07_strategie_startup.md` | [`07_strategie_startup.md`](07_strategie_startup.md) |
| 08 | `08_marche_concurrence.md` | [`08_marche_concurrence.md`](08_marche_concurrence.md) |
| 09 | `09_gtm_lancement_casablanca.md` | [`09_gtm_lancement_casablanca.md`](09_gtm_lancement_casablanca.md) |
| 10 | `10_kpi_experiences.md` | [`10_kpi_experiences.md`](10_kpi_experiences.md) |
| 11 | `11_roles_business.md` | [`11_roles_business.md`](11_roles_business.md) |
| 12 | `12_procedures_business.md` | [`12_procedures_business.md`](12_procedures_business.md) |
| 13 | `13_index_sources.md` | [`13_index_sources.md`](13_index_sources.md) |

Les rôles (11) et procédures (12) business ne sont pas encore des sous-agents ni des skills Claude Code : ils sont décrits ici comme référence.

## Vérification des références (2026-11-16)

Tous les fichiers du dépôt cités par 07–13 existent, sauf `docs/marketing/` (emplacement prévu pour les futurs briefs de campagne). Les noms d'événements de `10` §2 correspondent à `api/src/events.js` : les 15 événements marqués ✅ existent, et `app_ouverte`, `rdv_debut` et `parrainage_*` sont bien absents.

Points à corriger dans une prochaine version (le contenu n'a pas été modifié ici) :

| Document | Point | Constat dans le dépôt |
|---|---|---|
| 09 §1, 13 §3 | « 91 géolocalisés » attribué à `data/scraping/garages_clean.csv` | Ce fichier contient 123 garages dont **23** avec coordonnées. Les 91 garages géolocalisés viennent de l'enrichissement Telecontact (`RAPPORT_AVANCEMENT.md`, migration 007) : la requête par quartier doit porter sur la table `garages` de PostgreSQL, pas sur le CSV. |
| 09 §1, 11 §8 | « 104/123 mécanique générale » | Catégorie du CSV : 106 « Garage automobile / Mécanique », 15 « garage-automobile », 2 « Carrosserie ». À rapprocher des spécialités en base (migration 007). |
| 09 §1 | « 2,6 km » (modèle B) | Confirmé : `ml/reports/model_b_evaluation.json`, `distance_moyenne_top5_km` = 2,56. |
