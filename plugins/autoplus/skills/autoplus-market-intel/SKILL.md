---
name: autoplus-market-intel
description: "Recherche de marché et analyse concurrentielle AUTO+ (Maroc d'abord) : chiffres vérifiés, TAM/SAM/SOM, fiches concurrents, modèles internationaux, avec sources datées."
---
# AUTO+ — Market & Competitive Intelligence

Couvre deux besoins : **Market Research** et **Competitor Analysis**. Sous-agents : `market-researcher` (marché, TAM/SAM/SOM, réglementation) et `competitor-analyst` (concurrents). Document cible : `docs/business/08_marche_concurrence.md`.

Références embarquées (copies vérifiées de `docs/business/`, le skill fonctionne hors du dépôt) :
- `references/08_marche_concurrence.md` : §1 statut des chiffres du dossier, §2 contexte, §3 TAM/SAM/SOM, §4–5 concurrents et grille, §6 réglementation, §7 modèles internationaux, §9 sources S1–S53.
- `references/07_strategie_startup.md` : §4 statut réel des fonctionnalités d'AUTO+ (pour la grille de positionnement).
- `references/12_procedures_business.md` : procédures complètes.

## Avant de chercher
1. Lis `references/08_marche_concurrence.md` (§1 statut des chiffres, §4–5 concurrents, §9 sources) pour ne pas refaire ce qui existe.
2. Reformule la question et la décision qu'elle doit éclairer.

## Standards de recherche
- Maroc d'abord ; Casablanca pour le pilote ; international seulement comme modèle à adapter.
- Hiérarchie : source primaire (HCP, AIVAM, ANRT, Bank Al-Maghrib, ministères, rapports annuels) > presse économique datée > blog. **Jamais une réponse de chatbot** comme source (`docs/marche/chiffres(automobile market,digitalisation).docx` en est une).
- Chaque fait : URL + date de publication (et date de consultation). Sinon « non trouvé ».
- Étiquettes : `[FAIT]`, `[ESTIMATION]` (calcul montré), `[HYPOTHÈSE]`.
- Aucun chiffre inventé (trafic, prix, nombre de garages, parts de marché).
- Plusieurs angles de requête : français, anglais, arabe et darija ; au moins une recherche par acteur.

## Market Research
1. Vérifier les chiffres cités : ✅ confirmé / 🔄 mis à jour / ❌ corrigé / ⚠️ non vérifiable, avec source (format de `08` §1).
2. TAM/SAM/SOM bottom-up : nombre de véhicules × dépense annuelle × part adressable, chaque paramètre étiqueté. SOM lié à la capacité réelle (garages actifs × RDV/semaine) (`08` §3).
3. Contexte local : pouvoir d'achat, usage du cash, moyens de paiement, réglementation (loi 09-08/CNDP, loi 31-08, statut juridique, TVA) (`08` §2 et §6).

## Competitor Analysis

<!-- procedure:analyse-concurrent -->
1. **Identifier** : nom, URL, type (direct / indirect / substitut), date de consultation.
2. **Collecter** (sources publiques uniquement) : offre, prix publiés (MAD), zones couvertes, canaux visibles (Instagram, Google Ads, terrain…), application (store, note, nombre d'avis), promesse principale, 5 avis clients récents (positifs et négatifs, paraphrasés).
3. **Classer** chaque info : `[FAIT]` (capture/URL datée), `[ESTIMATION]`, `[HYPOTHÈSE]`. Trafic web : uniquement si outil cité (SimilarWeb…) avec période.
4. **Comparer** sur la grille fixe de `08` §5 (mise en relation, RDV en ligne, avis vérifiés, diagnostic IA, darija, paiement, couverture Casablanca, outil garage).
5. **Conclure** : « Impact pour AUTO+ » = 3 opportunités + 1 menace, une action chacune.
6. **Mettre à jour** `08` (tableau concurrents + sources) et dater la ligne.
<!-- /procedure -->

Ne dénigre jamais un concurrent dans un contenu public. Les chiffres structurants trouvés par un rôle sont contre-vérifiés par un autre (ou par le CSO) avant d'entrer dans `08`.

## Rendu
1. Réponse courte à la question.
2. Tableaux (faits étiquetés).
3. Contradictions avec les documents existants.
4. Mises à jour proposées pour `08` (lignes exactes).
5. Sources (titre, URL, date).
