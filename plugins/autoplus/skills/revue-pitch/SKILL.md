---
name: revue-pitch
description: Relire un pitch ou la partie business de la soutenance AUTO+ — structure du deck, audit de chaque chiffre contre ses sources, audit d'honnêteté (fonctionnalités réelles, données simulées), 15 questions difficiles avec réponses sourcées. À utiliser avant chaque pitch, candidature d'incubateur ou soutenance.
---
# Revue de pitch AUTO+

Rôle principal : `pitch-coach` (sous-agent). Contre-vérification : `market-researcher` pour les chiffres de marché, `business-strategist` pour le modèle. Le rapport PFA académique relève d'`academic-writer`.

Références embarquées : `references/07_strategie_startup.md` (§4 statut réel des fonctionnalités, §7 revenus, §9 positionnement), `references/08_marche_concurrence.md` (§1 statut de chaque chiffre du dossier, §9 sources), `references/10_kpi_experiences.md` (KPI, expériences). Résultats ML : `ml/reports/*.json` dans le dépôt.

## Entrée
Le deck (fichier ou texte des slides) ou la trame. Sans deck, produire une trame de 10–12 slides puis appliquer l'audit.

## Procédure

<!-- procedure:revue-pitch -->
1. Vérifier la structure : problème · solution · démo · marché · concurrence · modèle · traction · GTM · équipe · demande.
2. **Audit des chiffres** : chaque chiffre → source dans `08`/`10` ; signaler tout chiffre issu du dossier de mai 2026 non revérifié ; marché ≠ traction.
3. **Audit d'honnêteté** : fonctionnalités annoncées = statut réel (`07` §4) ; résultats ML avec type de données (réelles / simulées) et métrique.
4. **Questions difficiles** (15) : cold start, WTP, cash, concurrence (Google Maps, WhatsApp), défensibilité, réglementation, équipe à temps partiel, coût LLM, exactitude de l'IA, fraude aux avis, sortie de plateforme (désintermédiation)… avec réponse de 2 phrases et preuve.
5. Rendre : corrections par slide (Bloquant / Important / Suggestion) + fiche Q/R.
<!-- /procedure -->

## Points de contrôle systématiques
- Parc automobile : 4 747 215 (HCP, fin 2024), pas « 4,95 M » ; Casablanca-Settat 35 %, pas 37 % (`08` §1).
- « Le terrain est libre » → reformulation de `08` §4.
- Projections an 1 du dossier (200 garages, 15 000 utilisateurs, ~1,8 M MAD) : à retirer ou présenter comme hypothèses non validées (`10` §5).
- Traction : aujourd'hui aucune mesure réelle (0 utilisateur réel, 0 entretien) ; ne présenter que ce qui est mesuré.
- Modèle C et filtrage collaboratif du modèle B : données simulées.
- Fonctionnalités ⚪ / 💡 (paiement, garantie, OBD, rappels) : jamais présentées comme existantes.

## Rendu
| Slide | Problème | Gravité | Correction | Source |
|---|---|---|---|---|

Puis la fiche Q/R (question · réponse en 2 phrases · preuve), **À contre-vérifier**, **Décisions proposées** (3 max), **Ce qui reste à valider**.
