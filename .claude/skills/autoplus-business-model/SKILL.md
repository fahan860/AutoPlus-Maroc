---
name: autoplus-business-model
description: Customer research, business model, prix et positionnement AUTO+ : entretiens terrain, matrice d'hypothèses H1–H20, revenus B2C/B2B, validation de prix, déclaration de positionnement.
---
# AUTO+ — Customer, Business Model & Positioning

Couvre : **Customer Research**, **Business Model Development**, **Product Positioning**. Sous-agents : `customer-researcher` (guides : `terrain-analyst`), `business-strategist`, `startup-strategist`, `pmm`. Documents cibles : `docs/business/07_strategie_startup.md`, `docs/business/10_kpi_experiences.md`, `docs/AutoPlus_Assumption_Matrix.xlsx`.

Références embarquées (copies vérifiées de `docs/business/`, le skill fonctionne hors du dépôt) :
- `references/07_strategie_startup.md` : §2–3 problème et personas, §4 statut réel des fonctionnalités, §5 proposition de valeur, §6 BMC, §7–8 revenus et prix, §9 positionnement.
- `references/08_marche_concurrence.md` : §5 prix observés et grille concurrentielle, §6 paiement et réglementation, §7 modèles internationaux.
- `references/10_kpi_experiences.md` : §4 unit economics, §6 expériences, §7 journal.
- `references/12_procedures_business.md` : procédures complètes.

## Règles
- Statut des fonctionnalités : se référer à `07` §4 (implémenté / en développement / planifié / hypothèse). Ne jamais présenter le paiement en ligne, la garantie, l'OBD ou le SaaS avancé comme existants.
- Chaque affirmation sur le client renvoie à une hypothèse (H1–H20 de `docs/AutoPlus_Assumption_Matrix.xlsx`, ou nouvelle H21+) et à son statut. État au 2026-11-16 : 0 entretien, toutes les hypothèses « à valider ».
- Une intention déclarée ne valide pas une disposition à payer : il faut un comportement passé ou un engagement réel (signature, dépôt, paiement).
- Aucune conclusion sous 5 entretiens par segment sans le signaler.
- Données personnelles : aucun nom, numéro ou verbatim nominatif hors `docs/terrain/` (local).
- Textes pour automobilistes ou garagistes : skill `autoplus-brand-voice`.
- Aucun rôle ne valide sa propre conclusion : la synthèse est relue par un autre rôle avant la mise à jour de la matrice.

## Customer Research

<!-- procedure:customer-discovery -->
1. **Choisir l'hypothèse la plus risquée** dans la matrice (aujourd'hui : H9 WTP automobiliste, H18 WTP mécanicien, H3 arnaque prix, H15 réputation, H20 jours perdus).
2. **Guide** : partir de `docs/AutoPlus_Guide_Interview_V2.docx` et ajouter les 7 questions manquantes de `docs/AutoPlus_Analyse_CustomerDiscovery.docx` §4 (WTP auto, WTP méca, audit digital, temps de recherche, diagnostic, paiement, concurrence). FR + darija latine.
3. **Échantillon** (fixé avant le terrain) : 15 automobilistes dont ≥ 5 hors réseau personnel (stations-service, parkings, sorties de garages) ; 10 mécaniciens dont ≥ 3 avec présence Google Maps et ≥ 3 sans ; quartiers de Casablanca différents ; Tétouan en complément, signalé à part.
4. **Conduite** : 20 min, aucune mention d'application avant la fin, questions sur le passé (« la dernière fois… combien as-tu payé ») ; enregistrement uniquement avec accord.
5. **Fiche de synthèse** remplie dans les 10 min (modèle du guide V2), score 0–3.
6. **Stockage** : notes nominatives dans `docs/terrain/` (local, non versionné) ; seules les synthèses anonymisées vont ailleurs.
7. Après chaque lot de 5 : `synthese-interviews`.
<!-- /procedure -->

<!-- procedure:synthese-interviews -->
1. Tableau par entretien (ID anonyme A01…, M01…) : segment, quartier, canal actuel, douleur n°1, montant payé la dernière fois, signal WTP (oui/non + forme : abonnement, commission, par RDV), mode de paiement, solution déjà utilisée, score 0–3.
2. Compter : nombre d'entretiens qui confirment / contredisent chaque hypothèse. Verbatims paraphrasés ou courts, anonymes.
3. Séparer **comportements observés** et **intentions déclarées** ; une intention ne valide pas une WTP.
4. Statut par hypothèse : validée (≥ 60 % des entretiens d'un segment, n ≥ 8), invalidée, à tester. Seuils à écrire avant l'analyse si différents.
5. Mettre à jour `docs/AutoPlus_Assumption_Matrix.xlsx` (colonne STATUT + preuve) via une PR `docs/synthese-terrain-sNN`.
6. Rendre 3 décisions produit/prix justifiées et les inscrire au journal (`10` §7).
<!-- /procedure -->

## Business Model
Analyser séparément B2C, B2B et revenus additionnels (grille et options de `07` §7). Pour chaque option : mécanisme, faisabilité au Maroc (cash, facturation, prestataire de paiement), dépendance à la liquidité, preuve, horizon, verdict. Traiter explicitement le cold start et la désintermédiation. Projections : hypothèses ligne par ligne, jamais de chiffre de marché présenté comme revenu. Pour fixer un prix : skill `validation-prix`.

## Positioning
Déclaration : pour <cible> qui <problème>, AUTO+ est <catégorie> qui <bénéfice clé> ; contrairement à <alternative>, <différence prouvable>. Vérifier la différence contre `08` §5 et le statut des fonctionnalités (`07` §4). Version de travail actuelle : `07` §9.

## Rendu
Livrable demandé → hypothèses dont le statut change → 3 décisions proposées → entrée pour le journal (`10` §7) → ce qui reste à valider.
