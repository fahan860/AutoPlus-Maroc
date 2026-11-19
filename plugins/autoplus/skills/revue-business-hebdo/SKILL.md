---
name: revue-business-hebdo
description: Faire la revue business hebdomadaire d'AUTO+ — entretiens, pipeline garages, NSM et funnel, expériences, dépenses, hypothèses et risques qui changent, 3 priorités vérifiables, lignes pour le journal du cockpit. À lancer chaque semaine après /point-hebdo.
---
# Revue business hebdomadaire AUTO+

Coordination : session principale (CSO). Mesures : `marketing-analyst`. Pipeline : `garage-partnerships`. Expériences : `growth-lead`. Le point technique est fait avant par `/point-hebdo`.

Références embarquées : `references/09_gtm_lancement_casablanca.md` (§2 phases et critères de sortie, §4 pipeline), `references/10_kpi_experiences.md` (§1 NSM, §3 tableau de bord, §6 expériences, §7 journal).

## Procédure

<!-- procedure:revue-business-hebdo -->
À lancer chaque semaine, après `point-hebdo` (03) pour la partie technique.

1. **Collecte** (sans rien inventer) : nouveaux entretiens, garages contactés/visités/actifs, événements de la semaine (requêtes `marketing-analyst`), expériences en cours, dépenses.
2. **Rendre** :
   - Chiffres de la semaine vs semaine précédente (NSM et funnel, `10`), avec source.
   - Hypothèses dont le statut a changé.
   - Expériences : lancées / terminées / décisions.
   - Pipeline garages.
   - Risques business qui ont changé.
   - 3 priorités business de la semaine suivante, chacune avec un résultat vérifiable.
   - Lignes pour le journal du cockpit : `AAAA-MM-JJ · Business · Texte`.
3. Mettre à jour `10` §7 (journal de décisions) si une décision a été prise.
<!-- /procedure -->

## Où collecter
| Donnée | Source | Règle |
|---|---|---|
| Entretiens | synthèses anonymisées (IDs A01…, M01…) ; notes brutes dans `docs/terrain/` (local) | compter, ne rien recopier de nominatif |
| Pipeline garages | suivi local (`docs/terrain/`) | comptages par statut uniquement |
| Événements / NSM | `data/events/` (Parquet) et PostgreSQL via `marketing-analyst` | requête et période citées ; tant que l'app n'est pas en ligne : « non mesuré » |
| Expériences | `10` §6 | statut et seuil d'origine, jamais modifié après coup |
| Dépenses | déclarées par l'équipe | `[À COMPLÉTER]` si non fournies |
| Phase en cours | `09` §2 | comparer aux critères de sortie |

## Rendu
Le bilan dans l'ordre de la procédure, puis la décision de passage de phase (oui / non / pas encore + critère manquant), les lignes du journal et **Ce qui reste à valider**. Une semaine sans donnée est rapportée comme telle.
