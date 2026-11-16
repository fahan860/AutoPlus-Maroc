---
name: validation-prix
description: Valider un prix AUTO+ avant de l'annoncer — frais par RDV honoré, abonnement garage, mise en avant ou premium automobiliste — à partir d'ancrages réels, d'un test Van Westendorp simplifié et d'un engagement réel d'au moins 5 garages. À utiliser avant toute annonce de prix (pitch, garages, store).
---
# Validation de prix AUTO+

Rôle principal : `business-strategist` (sous-agent). La disposition à payer est contre-vérifiée par `customer-researcher`, jamais par celui qui recommande le prix.

Références embarquées (copies de `docs/business/`, vérifiées par `tools/sync_skill_references.py`) : `references/07_strategie_startup.md` (§7 options de revenus, §8 hypothèses et contraintes), `references/08_marche_concurrence.md` (§5 prix observés, §6 paiement et réglementation, §7 modèles internationaux), `references/10_kpi_experiences.md` (§4 unit economics, EXP-01). Les numéros cités (`07`, `08`…) renvoient à ces fichiers.

## Procédure

<!-- procedure:validation-prix -->
1. **Ancrages réels** : ce que l'automobiliste paie aujourd'hui (vidange, diagnostic, main-d'œuvre) et ce que le garagiste dépense pour sa visibilité — uniquement depuis entretiens ou prix publiés (`08` §5).
2. **Options à tester**, une par face :
   - Garage : gratuit pendant le pilote → commission par RDV honoré / forfait mensuel / « mise en avant ».
   - Automobiliste : gratuit (recommandé tant que la liquidité n'est pas atteinte) → éventuellement option premium (rappels, historique, assistant illimité).
3. **Tests** : Van Westendorp simplifié en fin d'entretien (trop cher / cher / bon marché / trop bon marché) **après** avoir établi la douleur ; puis test d'engagement réel (pré-réservation d'une place « garage pilote payant », dépôt symbolique, signature d'une lettre d'intention).
4. **Critère** : un prix est « validé » seulement avec un engagement réel (paiement, signature) d'au moins 5 garages ; sinon il reste `[HYPOTHÈSE]`.
5. **Contraintes Maroc** : forte préférence pour le cash, facturation légale (statut juridique requis pour facturer une commission), coût d'un moyen de paiement en ligne. Voir `07` §8.
6. Rendre : prix recommandé, fourchette, preuves, risques, prochaine expérience.
<!-- /procedure -->

## Règles d'exécution
- État au 2026-11-16 : 0 entretien, 0 lettre d'intention. Aucun prix ne peut être « validé » ; tout montant reste `[HYPOTHÈSE]` ou `[ESTIMATION]` avec le calcul montré.
- Les fourchettes du dossier de mai 2026 (abonnement 299–799 MAD, commission 5–10 %, premium 49–99 MAD) sont des hypothèses non testées.
- Calculs reproductibles (Python), entrées et formule affichées. Aucun calcul de tête.
- AUTO+ ne fixe jamais le prix des prestations des garages (précédent Autobutler, `08` §6) : seulement le prix de son propre service.
- Les 4 questions Van Westendorp en darija sont rédigées par `terrain-analyst` avec `autoplus-brand-voice`.

## Rendu
| Option | Prix ou fourchette | Étiquette | Preuves (n, source) | Risques |
|---|---|---|---|---|

Puis : prix recommandé, prochaine expérience (fiche `design-experience`), **À contre-vérifier** (affirmation · rôle vérificateur), **Décisions proposées** (3 max), **Ce qui reste à valider**, ligne pour le journal (`AAAA-MM-JJ · Décision · Raison · Source · Réversible ?`).
