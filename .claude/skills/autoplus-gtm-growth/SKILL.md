---
name: autoplus-gtm-growth
description: Go-to-market, plan marketing et growth AUTO+ à Casablanca : phases pilote/bêta/lancement, cold start, acquisition garages et automobilistes, campagnes, expériences et KPI.
---
# AUTO+ — Go-To-Market, Marketing & Growth

Couvre : **Go-To-Market Strategy**, **Marketing Planning**, **Growth Marketing**. Sous-agents : `gtm-strategist`, `garage-partnerships`, `growth-lead`, `pmm` ; mesure par `marketing-analyst`, contenus par `content-creator`. Documents cibles : `docs/business/09_gtm_lancement_casablanca.md`, `docs/business/10_kpi_experiences.md`.

Références embarquées (copies vérifiées de `docs/business/`, le skill fonctionne hors du dépôt) :
- `references/09_gtm_lancement_casablanca.md` : §1 marché initial, §2 phases P0–P3 et critères de sortie, §3 cold start, §4 garages, §5 automobilistes, §6 partenariats, §7 check-list, §8 budget.
- `references/10_kpi_experiences.md` : §1 NSM, §2 funnel ↔ événements, §3 tableau de bord, §6 backlog EXP-01 à EXP-06.
- `references/07_strategie_startup.md` : §3 personas, §4 statut réel des fonctionnalités.
- `references/12_procedures_business.md` : procédures complètes.

## Principes
- Offre avant demande ; 2–3 quartiers denses de Casablanca ; concierge WhatsApp pendant le pilote ; valeur solo (agent IA darija, estimation de prix) ; les garages amènent leurs clients.
- Ne jamais promettre de volume de clients à un garage ; pilote gratuit tant que la liquidité n'est pas mesurée.
- North Star Metric : RDV terminés par semaine. Chaque campagne vise une étape du funnel de `10` §2 ; si l'événement de mesure manque, créer le ticket avant de lancer.
- Une expérience = une hypothèse, une métrique, un seuil de décision fixé avant le lancement, un budget plafonné (skill `design-experience`).
- Budgets : `[HYPOTHÈSE]` tant qu'aucune dépense réelle n'est mesurée ; CAC calculé uniquement sur des données réelles.
- Messages : un seul appel à l'action, darija en lettres latines puis français (`autoplus-brand-voice`), uniquement des fonctionnalités implémentées (`07` §4).
- Point de départ au 2026-11-16 : app non déployée, pas de build installable, 0 garage pilote, 0 entretien. Ne planifie pas une phase dont le prérequis n'est pas livré.
- Comptage des garages par quartier : table `garages` de PostgreSQL (91 géolocalisés), pas `data/scraping/garages_clean.csv` (23 géolocalisés).

## Marketing Planning

<!-- procedure:plan-campagne -->
1. **Objectif** lié à une étape du funnel (`10` §2) et à un seuil chiffré.
2. **Cible** : persona (`07` §3), quartier(s) de Casablanca, face (automobiliste ou garage).
3. **Message** : brief PMM → contenus par `content-creator` (02) avec `autoplus-brand-voice` ; un seul appel à l'action.
4. **Canal** et **budget** : tableau canal · coût prévu · CAC cible · code de suivi (lien UTM, code parrainage).
5. **Préalable technique** : les événements de mesure existent (sinon, ticket « événement manquant » avant lancement).
6. **Calendrier** : préparation, diffusion, mesure (J+7, J+14).
7. **Bilan** : coût réel, résultats, CAC mesuré, décision → journal.
<!-- /procedure -->

## Growth
Backlog d'expériences priorisé ICE dans `10` §6 (chaque nouvelle expérience passe par le skill `design-experience`) ; revue hebdomadaire (skill `revue-business-hebdo`) ; leviers prioritaires : activation sous 7 jours, confirmation garage sous 24 h, parrainage garage → client, rétention à 90 jours. Le résultat d'une expérience est mesuré par `marketing-analyst`, pas par celui qui l'a conçue.

## Rendu
Plan ou fiche d'expérience → événements requis → budget → critères de passage de phase → lignes pour le journal du cockpit (`AAAA-MM-JJ · Business · Texte`).
