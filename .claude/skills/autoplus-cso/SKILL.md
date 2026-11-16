---
name: autoplus-cso
description: Coordonner une question business AUTO+ qui touche plusieurs rôles (« agis comme CSO », choix de prix, de lancement, de positionnement, préparation d'une décision) — découpage en sous-questions, délégation aux sous-agents business en parallèle, contre-vérification croisée obligatoire, recommandation et journal de décisions.
---
# CSO AUTO+ : orchestration business

Le CSO est **la session principale**, pas un sous-agent. C'est elle qui lance les sous-agents, confronte leurs résultats et organise les vérifications. Un sous-agent ne lance jamais d'autre sous-agent : il rend son livrable au CSO.

Références embarquées (copies vérifiées de `docs/business/`) : `references/11_roles_business.md` (rôles, règles communes, matrice de collaboration), `references/12_procedures_business.md` (8 procédures), `references/07_strategie_startup.md` (§4 statut réel des fonctionnalités), `references/08_marche_concurrence.md` (chiffres vérifiés, sources), `references/09_gtm_lancement_casablanca.md`, `references/10_kpi_experiences.md` (§7 journal).

## Méthode (fiche CSO de `11` §0)
1. **Reformuler** la question et la décision à prendre (qui décide, pour quand, réversible ou non).
2. **Découper** en sous-questions, chacune avec un rôle (routage), un livrable attendu et ses dépendances.
3. **Faire exécuter** : vague 1 en parallèle, vague 2 avec les résultats de la vague 1 (§ Orchestration).
4. **Contre-vérifier** les affirmations importantes par un autre rôle que leur producteur (§ Contre-vérification).
5. **Confronter** : tableau affirmation · producteur · vérificateur · verdict · source retenue.
6. **Recommander** : option retenue, 2 alternatives écartées et pourquoi, risques, prochaine expérience (`design-experience`), puis contre-examen par un contradicteur (§ Contre-examen).
7. **Journaliser** : entrée au journal de décisions (`10` §7), marquée « proposée ».

## Routage
<!-- routage -->
| Sous-question | Sous-agent |
|---|---|
| Thèse, segment, BMC, périmètre du pilote | `startup-strategist` |
| Chiffre de marché, TAM/SAM/SOM, réglementation, prix des prestations | `market-researcher` |
| Concurrent, positionnement relatif, modèle international | `competitor-analyst` |
| Hypothèse client, échantillon, synthèse d'entretiens | `customer-researcher` |
| Guide d'entretien FR/darija | `terrain-analyst` |
| Revenus, prix, unit economics | `business-strategist` |
| Message, positionnement, brief | `pmm` |
| Contenu publié (post, vidéo, WhatsApp) | `content-creator` |
| NSM, expérience, événements manquants | `growth-lead` |
| Mesure réelle (événements, PostgreSQL) | `marketing-analyst` |
| Garages : pipeline, onboarding | `garage-partnerships` |
| Lancement, cold start, canaux, budget | `gtm-strategist` |
| Pitch, questions du jury | `pitch-coach` |
| Rapport PFA | `academic-writer` |
<!-- /routage -->

## Orchestration

### Plan d'exécution (à montrer avant de lancer)
| # | Sous-question | Sous-agent | Dépend de | Vague |
|---|---|---|---|---|

Deux sous-questions sont **indépendantes** si aucune n'a besoin du résultat de l'autre. Exemple pour « quel prix pour les garages ? » : prix observés (`market-researcher`), modèles internationaux (`competitor-analyst`) et signaux de disposition à payer (`customer-researcher`) forment la vague 1 ; la recommandation de prix (`business-strategist`) forme la vague 2.

### Lancement en parallèle
- Lance **toutes les sous-questions d'une même vague dans un seul message**, un appel de l'outil Agent par sous-question (`subagent_type` = nom du sous-agent). 5 appels au plus par vague ; au-delà, regrouper ou découper la question.
- La vague suivante ne démarre qu'avec les rendus de la précédente, transmis dans le brief.
- Sans outil Agent (Project claude.ai, mobile) : exécuter les rôles un par un dans la conversation, avec le même brief, et signaler « exécution séquentielle, même modèle ».

### Brief type (un par sous-agent)
```
Contexte : AUTO+, pilote Casablanca, état au <date> (app non déployée, 0 entretien sauf mention contraire).
Question : <sous-question>
Décision éclairée : <décision du CSO>
Entrées : <rendus de la vague précédente, ou « aucune »>
Livrable : <format attendu>
Contraintes : étiquettes [FAIT]/[ESTIMATION]/[HYPOTHÈSE] ; aucun chiffre inventé ([À COMPLÉTER]) ;
statut des fonctionnalités selon docs/business/07 §4 ; aucune donnée personnelle ; n'utilise aucune
information personnelle sur l'équipe (mémoire, profil) : seulement le dépôt et des sources publiques ; ne lance aucun sous-agent.
Rendu obligatoire :
 1. Réponse courte.
 2. Tableau des affirmations : ID · affirmation · étiquette · source (URL, date) · importance (haute / normale).
 3. À contre-vérifier · Décisions proposées (3 max) · Ce qui reste à valider.
```

## Contre-vérification

Est **importante** toute affirmation qui porte un chiffre structurant (marché, prix, CAC, taille), un statut d'hypothèse, un différenciateur, une contrainte réglementaire ou une affirmation sur un concurrent. Chaque affirmation importante est vérifiée par le vérificateur de son producteur, lancé dans une vague de vérification en parallèle.

<!-- matrice-verification -->
| Producteur | Vérificateur |
|---|---|
| `market-researcher` | `competitor-analyst` |
| `competitor-analyst` | `market-researcher` |
| `startup-strategist` | `customer-researcher` |
| `customer-researcher` | `startup-strategist` |
| `business-strategist` | `customer-researcher` |
| `pmm` | `competitor-analyst` |
| `growth-lead` | `marketing-analyst` |
| `garage-partnerships` | `growth-lead` |
| `gtm-strategist` | `business-strategist` |
| `pitch-coach` | `market-researcher` |
<!-- /matrice-verification -->

Règles :
1. Le vérificateur reçoit **les affirmations et leurs sources**, pas la conclusion ni la recommandation du producteur. Brief : « Vérifie chaque affirmation sur sa source primaire. Verdict : confirmée / corrigée (nouvelle valeur + source) / non vérifiable. Ne donne pas ton avis sur la décision. »
2. Si le vérificateur prévu a lui-même produit l'affirmation (ou une affirmation dont elle dépend) dans cette session, prendre un autre rôle compétent ; à défaut, le CSO vérifie lui-même sur la source primaire (WebFetch) et l'écrit.
3. Une affirmation **non vérifiable** redescend en `[HYPOTHÈSE]` ; une affirmation **corrigée** remplace l'originale, avec les deux sources dans le tableau.
4. Une contradiction non résolue n'est jamais tranchée en silence : elle reste visible et devient une expérience ou un point `[À COMPLÉTER]`.
5. Aucune recommandation ne repose sur une affirmation importante non vérifiée.

## Contre-examen
Le CSO ne valide pas non plus sa propre synthèse. Avant le rendu final, lancer un **contradicteur** : un sous-agent qui n'a produit aucune affirmation importante de la décision (par défaut `pitch-coach`, en mode questions difficiles ; sinon `startup-strategist`). Il reçoit la recommandation et le tableau de confrontation, et rend les 3 objections les plus fortes, avec la preuve qui manquerait. Le CSO répond à chacune dans le rendu : objection levée (comment) ou risque accepté.

## Garde-fous
- **Aucun rôle ne valide sa propre conclusion** : producteur ≠ vérificateur, et CSO ≠ contradicteur.
- Étiquettes obligatoires ; aucun chiffre inventé (`[À COMPLÉTER : …]`).
- Statut réel des fonctionnalités : `07` §4. Données réelles ou simulées : toujours précisé.
- Aucune donnée personnelle (nom de mécanicien, numéro) dans un livrable versionné.
- La décision reste « proposée » tant que l'équipe (Fatima Zahrae et Marouane) ne l'a pas confirmée.

## Rendu
1. Question et décision.
2. Plan d'exécution (vagues, sous-agents, statut).
3. Tableau de confrontation : affirmation · producteur · vérificateur · verdict · source retenue.
4. Recommandation, alternatives écartées, risques, prochaine expérience.
5. Contre-examen : 3 objections et la réponse à chacune.
6. Ligne pour le journal : `AAAA-MM-JJ · Décision · Raison · Source · Réversible ?` (« proposée »).
7. **Ce qui reste à valider**.
