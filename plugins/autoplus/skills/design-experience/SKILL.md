---
name: design-experience
description: Concevoir une expérience AUTO+ avant de la lancer (acquisition, activation, prix, canal WhatsApp, parrainage) — hypothèse, métrique unique issue d'un événement, seuils de décision fixés à l'avance, échantillon, coût, ICE — et l'inscrire au backlog EXP-NN. À utiliser avant toute campagne ou dépense.
---
# Concevoir une expérience AUTO+

Rôle principal : `growth-lead` (sous-agent). La mesure est faite par `marketing-analyst` ; la décision finale par le CSO. Celui qui conçoit l'expérience ne valide pas son résultat.

Référence embarquée : `references/10_kpi_experiences.md` (§1 NSM, §2 funnel ↔ événements, §6 backlog EXP-01 à EXP-06, §7 journal). Source de vérité : `docs/business/10_kpi_experiences.md`.

## Procédure

<!-- procedure:design-experience -->
Fiche à remplir **avant** de lancer, à copier dans `10` §6 :

| Champ | Contenu |
|---|---|
| ID | EXP-NN |
| Hypothèse | « Nous croyons que <segment> fera <comportement> parce que <raison> » (+ ID H) |
| Métrique | une seule métrique principale, issue d'un événement existant (`api/src/events.js`) ou à ajouter |
| Seuil de décision | succès si ≥ X ; échec si < Y ; entre les deux = prolonger une fois |
| Méthode | landing page, offre Wizard-of-Oz, test WhatsApp, A/B, visite terrain… |
| Échantillon / durée | taille minimale et date de fin |
| Coût | MAD et heures |
| Score ICE | Impact, Confiance, Facilité (1–10) |
| Résultat | mesuré, avec date et source (requête SQL ou fichier Parquet) |
| Décision | continuer / pivoter / arrêter → journal |

Règle : pas de seuil fixé après coup ; pas de résultat sans requête reproductible.
<!-- /procedure -->

## Contrôles avant lancement
1. **Doublon** : l'hypothèse n'est-elle pas déjà couverte par EXP-01 à EXP-06 (`10` §6) ? Si oui, réviser la fiche existante.
2. **Mesurabilité** : la métrique s'appuie sur un événement existant (`user_register`, `recherche_garage`, `recommandation_garages`, `agent_message`, `consultation_garage`, `rdv_demande`, `rdv_statut_change`, `avis_poste`, `garage_cree`…). Si l'événement manque (`app_ouverte`, `rdv_debut`, `parrainage_*`, `garage_onboarde`, source d'acquisition), l'expérience est **bloquée** : rédige d'abord le ticket technique.
3. **Prérequis produit** : l'app doit être en ligne pour toute expérience côté automobiliste (aujourd'hui : non déployée).
4. **Budget** : coût plafonné ; si dépense publicitaire, CAC cible fixé avant lancement.
5. **Seuils** : X et Y écrits, avec leur justification, avant toute collecte.

## Rendu
La fiche complète, le statut (prête / bloquée + raison), les lignes à ajouter dans `10` §6, **À contre-vérifier** (qui mesure, quelle requête), **Décisions proposées** (3 max), **Ce qui reste à valider**.
