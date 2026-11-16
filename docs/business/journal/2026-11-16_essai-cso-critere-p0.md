# Essai du protocole CSO : critère de sortie P0 (2026-11-16)

> Premier essai réel du skill `autoplus-cso` (orchestration dans la session principale). Sources : `docs/business/09`, `10`, `README.md`, `CLAUDE.md`. Aucune mesure terrain n'existe à cette date.
> Statut de la décision : **proposée**, à confirmer par l'équipe.

**Question :** le critère de sortie P0 « ≥ 5 garages d'accord pour le pilote » (`09` §2) est-il atteignable d'ici le 20 décembre 2026 ?

## Plan d'exécution
| # | Sous-question | Sous-agent | Vague |
|---|---|---|---|
| 1 | Faisabilité du critère au regard de P0 et des prérequis techniques | `gtm-strategist` | 1 (parallèle) |
| 2 | Entonnoir garages : contacts → visites → accords, jours terrain | `garage-partnerships` | 1 (parallèle) |
| 3 | Vérification des affirmations importantes de 1 | `business-strategist` | vérification (parallèle) |
| 4 | Vérification des affirmations importantes de 2 | `growth-lead` | vérification (parallèle) |
| 5 | Contre-examen de la recommandation | `pitch-coach` | contre-examen |

## Confrontation
| Affirmation | Producteur | Vérificateur | Verdict |
|---|---|---|---|
| P0 = 16 nov. → 20 déc. 2026 | gtm | business | confirmée (période « proposée ») |
| Visite 20 min + démo 3 min ; onboarding 30 min avec RDV fictif | gtm | business | confirmée (`09` §4) |
| Déploiement et build Android « en développement » | gtm | business | confirmée (`07` §4) |
| « Expo Go exige le même Wi-Fi » | gtm | business | **corrigée** : la source dit « Expo Go, même Wi-Fi » |
| Plan initial 10 visites → ≥ 5 accords = 50 % implicite, non mesuré | gtm | business | confirmée (même seuil qu'EXP-01) |
| « Accord pilote » non défini | gtm | business | confirmée |
| `validation-prix` exige ≥ 5 engagements | gtm | business | confirmée |
| 91 garages géolocalisés en base, 23 dans le CSV | garages | growth | confirmée |
| Disponibilité 60 %, acceptation 25 % | garages | growth | **non vérifiable** → `[HYPOTHÈSE]` |
| Onboarding complet = app en ligne | garages | growth | confirmée par déduction |
| Nombre de garages par quartier inconnu | garages | growth | confirmée |

**Contradiction entre rôles :** `gtm-strategist` propose de réduire le critère à ≥ 3 accords ; `garage-partnerships` propose de le garder à ≥ 5 avec 20 visites. Aucune mesure ne permet de trancher : le taux d'acceptation est une hypothèse.

## Recommandation (proposée)
1. Garder la cible ≥ 5, en définissant « accord » = pilote gratuit accepté (date d'onboarding fixée **ou** onboarding prévu dès que l'API est en ligne). La lettre d'intention payante (EXP-01) est mesurée à part.
2. Prévoir ~20 visites dans 2–3 quartiers choisis par requête sur la table `garages` (PostgreSQL), pas sur le CSV.
3. Point d'étape **après 5 visites** (avancé suite au contre-examen) : < 1 accord → repli à ≥ 3 garages dans un seul quartier (mode concierge de `09` §2). Démonstration par vidéo tant que l'API n'est pas en ligne.

Alternatives écartées : réduire d'emblée à ≥ 3 (abandonne `validation-prix`, qui exige 5 engagements) ; décaler P0 après la soutenance (aucun résultat terrain pour le jury).

## Contre-examen (`pitch-coach`) et réponses
| Objection | Réponse du CSO |
|---|---|
| 20 visites à 25 % ne laissent aucune marge ; le point d'étape après 10 visites est trop tard | Acceptée : point d'étape avancé à 5 visites |
| « Accord » lié à une date d'onboarding intenable tant que l'API n'est pas en ligne | Acceptée : définition élargie (onboarding prévu à la mise en ligne) ; date de déploiement à obtenir de `deploy-engineer` |
| Capacité terrain et vivier par quartier non démontrés | Risque accepté : requête par quartier et calendrier terrain sont les deux premières actions |

## Journal
`2026-11-16 · Garder le critère P0 « ≥ 5 garages d'accord » avec 20 visites et point d'étape à 5 visites · aucun taux d'acceptation mesuré, validation-prix exige 5 engagements · docs/business/journal/2026-11-16_essai-cso-critere-p0.md · oui — proposée`

## Ce qui reste à valider
- Nombre de garages géolocalisés par quartier (requête `marketing-analyst`).
- Date de mise en ligne de l'API (`deploy-engineer`).
- Jours terrain disponibles et coût des déplacements `[À COMPLÉTER]`.
- Taux de disponibilité et d'acceptation réels, mesurés sur les 5 premières visites.

## Enseignement pour le protocole
Deux sous-agents ont utilisé une information personnelle sur l'équipe venant de la mémoire de l'assistant, pas du dépôt. Le brief type interdit désormais d'utiliser la mémoire ou le profil (`autoplus-cso`, brief type).
