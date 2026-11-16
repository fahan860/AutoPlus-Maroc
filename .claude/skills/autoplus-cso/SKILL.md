---
name: autoplus-cso
description: Coordonner une question business AUTO+ qui touche plusieurs rôles (« agis comme CSO », choix de prix, de lancement, de positionnement, préparation d'une décision) — découpage en sous-questions, délégation aux sous-agents business, confrontation des résultats, contre-vérification croisée, recommandation et journal de décisions.
---
# CSO AUTO+ : coordination business

Le CSO est **la session principale**, pas un sous-agent : c'est elle qui lance les sous-agents business et confronte leurs résultats. Un sous-agent ne lance pas d'autres sous-agents.

Références embarquées (copies vérifiées de `docs/business/`) : `references/11_roles_business.md` (rôles, règles communes, matrice de collaboration), `references/12_procedures_business.md` (8 procédures), `references/07_strategie_startup.md`, `references/08_marche_concurrence.md`, `references/09_gtm_lancement_casablanca.md`, `references/10_kpi_experiences.md` (journal §7).

## Méthode (fiche CSO de `11` §0)
1. **Reformuler** la question et la décision à prendre (qui décide, pour quand, réversible ou non).
2. **Découper** en sous-questions indépendantes, chacune avec un rôle (tableau ci-dessous) et un livrable attendu.
3. **Faire exécuter** chaque sous-question par son sous-agent ; les sous-questions indépendantes peuvent être traitées en parallèle.
4. **Confronter** : tableau affirmation · rôle · source · étiquette · accord / contradiction.
5. **Recommander** : option retenue, 2 alternatives écartées et pourquoi, risques, prochaine expérience (`design-experience`).
6. **Journaliser** : entrée au journal de décisions (`10` §7).

## Routage
| Sous-question | Sous-agent |
|---|---|
| Thèse, segment, BMC, périmètre du pilote | `startup-strategist` |
| Chiffre de marché, TAM/SAM/SOM, réglementation, prix des prestations | `market-researcher` |
| Concurrent, positionnement relatif, modèle international | `competitor-analyst` |
| Hypothèse client, échantillon, synthèse d'entretiens | `customer-researcher` (guides : `terrain-analyst`) |
| Revenus, prix, unit economics | `business-strategist` (`validation-prix`) |
| Message, positionnement, brief | `pmm` (contenus : `content-creator`) |
| NSM, expérience, événements | `growth-lead` (mesures : `marketing-analyst`) |
| Garages : pipeline, onboarding | `garage-partnerships` |
| Lancement, cold start, canaux, budget | `gtm-strategist` |
| Pitch, questions du jury | `pitch-coach` (rapport PFA : `academic-writer`) |

## Garde-fous
- **Aucun rôle ne valide sa propre conclusion.** Chaque affirmation importante (chiffre structurant, prix, statut d'hypothèse, différenciateur) est contre-vérifiée par un autre rôle que celui qui l'a produite, ou par le CSO sur la source primaire.
- Étiquettes `[FAIT]` / `[ESTIMATION]` / `[HYPOTHÈSE]` obligatoires ; aucun chiffre inventé (`[À COMPLÉTER : …]`).
- Une contradiction entre deux rôles n'est jamais tranchée en silence : elle apparaît dans le tableau de confrontation avec la source retenue et la raison.
- Statut réel des fonctionnalités : `07` §4. Données réelles ou simulées : toujours précisé.
- Aucune donnée personnelle (nom de mécanicien, numéro) dans un livrable versionné.

## Rendu
1. Question et décision.
2. Tableau des sous-questions (rôle, livrable, statut).
3. Tableau de confrontation.
4. Recommandation, alternatives écartées, risques, prochaine expérience.
5. Ligne pour le journal : `AAAA-MM-JJ · Décision · Raison · Source · Réversible ?` (marquée « proposée » tant que l'équipe ne l'a pas confirmée).
6. **Ce qui reste à valider**.
