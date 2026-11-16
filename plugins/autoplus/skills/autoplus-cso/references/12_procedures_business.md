# AUTO+ : procédures business (12)

> Complète `03_skills_procedures.md` (5 procédures techniques et voix de marque). Dans ce Project : « applique la procédure <nom> ».
> Rôles cités : voir `11_roles_business.md`. Étiquettes `[FAIT]` / `[ESTIMATION]` / `[HYPOTHÈSE]` obligatoires.
> Dernière mise à jour : 2026-11-16.

| Procédure | Rôle principal | Fréquence | Sortie |
|---|---|---|---|
| `analyse-concurrent` | Competitor Analyst | à chaque nouveau concurrent, revue trimestrielle | fiche + mise à jour `08` §4–5 |
| `customer-discovery` | Customer Researcher | campagne de 2–3 semaines | plan + entretiens |
| `synthese-interviews` | Customer Researcher | après chaque lot de 5 entretiens | synthèse + matrice d'hypothèses |
| `design-experience` | Growth Lead | avant toute expérience | fiche d'expérience dans `10` §6 |
| `validation-prix` | Business Strategist | avant d'annoncer un prix | recommandation de prix |
| `plan-campagne` | GTM Strategist + PMM | par campagne | brief + budget + mesure |
| `revue-pitch` | Pitch Coach | avant chaque pitch/soutenance | liste de corrections + Q/R |
| `revue-business-hebdo` | CSO | chaque semaine | bilan + décisions |

---

## analyse-concurrent

1. **Identifier** : nom, URL, type (direct / indirect / substitut), date de consultation.
2. **Collecter** (sources publiques uniquement) : offre, prix publiés (MAD), zones couvertes, canaux visibles (Instagram, Google Ads, terrain…), application (store, note, nombre d'avis), promesse principale, 5 avis clients récents (positifs et négatifs, paraphrasés).
3. **Classer** chaque info : `[FAIT]` (capture/URL datée), `[ESTIMATION]`, `[HYPOTHÈSE]`. Trafic web : uniquement si outil cité (SimilarWeb…) avec période.
4. **Comparer** sur la grille fixe de `08` §5 (mise en relation, RDV en ligne, avis vérifiés, diagnostic IA, darija, paiement, couverture Casablanca, outil garage).
5. **Conclure** : « Impact pour AUTO+ » = 3 opportunités + 1 menace, une action chacune.
6. **Mettre à jour** `08` (tableau concurrents + sources) et dater la ligne.

## customer-discovery

1. **Choisir l'hypothèse la plus risquée** dans la matrice (aujourd'hui : H9 WTP automobiliste, H18 WTP mécanicien, H3 arnaque prix, H15 réputation, H20 jours perdus).
2. **Guide** : partir de `docs/AutoPlus_Guide_Interview_V2.docx` et ajouter les 7 questions manquantes de `docs/AutoPlus_Analyse_CustomerDiscovery.docx` §4 (WTP auto, WTP méca, audit digital, temps de recherche, diagnostic, paiement, concurrence). FR + darija latine.
3. **Échantillon** (fixé avant le terrain) : 15 automobilistes dont ≥ 5 hors réseau personnel (stations-service, parkings, sorties de garages) ; 10 mécaniciens dont ≥ 3 avec présence Google Maps et ≥ 3 sans ; quartiers de Casablanca différents ; Tétouan en complément, signalé à part.
4. **Conduite** : 20 min, aucune mention d'application avant la fin, questions sur le passé (« la dernière fois… combien as-tu payé ») ; enregistrement uniquement avec accord.
5. **Fiche de synthèse** remplie dans les 10 min (modèle du guide V2), score 0–3.
6. **Stockage** : notes nominatives dans `docs/terrain/` (local, non versionné) ; seules les synthèses anonymisées vont ailleurs.
7. Après chaque lot de 5 : `synthese-interviews`.

## synthese-interviews

1. Tableau par entretien (ID anonyme A01…, M01…) : segment, quartier, canal actuel, douleur n°1, montant payé la dernière fois, signal WTP (oui/non + forme : abonnement, commission, par RDV), mode de paiement, solution déjà utilisée, score 0–3.
2. Compter : nombre d'entretiens qui confirment / contredisent chaque hypothèse. Verbatims paraphrasés ou courts, anonymes.
3. Séparer **comportements observés** et **intentions déclarées** ; une intention ne valide pas une WTP.
4. Statut par hypothèse : validée (≥ 60 % des entretiens d'un segment, n ≥ 8), invalidée, à tester. Seuils à écrire avant l'analyse si différents.
5. Mettre à jour `docs/AutoPlus_Assumption_Matrix.xlsx` (colonne STATUT + preuve) via une PR `docs/synthese-terrain-sNN`.
6. Rendre 3 décisions produit/prix justifiées et les inscrire au journal (`10` §7).

## design-experience

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

## validation-prix

1. **Ancrages réels** : ce que l'automobiliste paie aujourd'hui (vidange, diagnostic, main-d'œuvre) et ce que le garagiste dépense pour sa visibilité — uniquement depuis entretiens ou prix publiés (`08` §5).
2. **Options à tester**, une par face :
   - Garage : gratuit pendant le pilote → commission par RDV honoré / forfait mensuel / « mise en avant ».
   - Automobiliste : gratuit (recommandé tant que la liquidité n'est pas atteinte) → éventuellement option premium (rappels, historique, assistant illimité).
3. **Tests** : Van Westendorp simplifié en fin d'entretien (trop cher / cher / bon marché / trop bon marché) **après** avoir établi la douleur ; puis test d'engagement réel (pré-réservation d'une place « garage pilote payant », dépôt symbolique, signature d'une lettre d'intention).
4. **Critère** : un prix est « validé » seulement avec un engagement réel (paiement, signature) d'au moins 5 garages ; sinon il reste `[HYPOTHÈSE]`.
5. **Contraintes Maroc** : forte préférence pour le cash, facturation légale (statut juridique requis pour facturer une commission), coût d'un moyen de paiement en ligne. Voir `07` §8.
6. Rendre : prix recommandé, fourchette, preuves, risques, prochaine expérience.

## plan-campagne

1. **Objectif** lié à une étape du funnel (`10` §2) et à un seuil chiffré.
2. **Cible** : persona (`07` §3), quartier(s) de Casablanca, face (automobiliste ou garage).
3. **Message** : brief PMM → contenus par `content-creator` (02) avec `autoplus-brand-voice` ; un seul appel à l'action.
4. **Canal** et **budget** : tableau canal · coût prévu · CAC cible · code de suivi (lien UTM, code parrainage).
5. **Préalable technique** : les événements de mesure existent (sinon, ticket « événement manquant » avant lancement).
6. **Calendrier** : préparation, diffusion, mesure (J+7, J+14).
7. **Bilan** : coût réel, résultats, CAC mesuré, décision → journal.

## revue-pitch

1. Vérifier la structure : problème · solution · démo · marché · concurrence · modèle · traction · GTM · équipe · demande.
2. **Audit des chiffres** : chaque chiffre → source dans `08`/`10` ; signaler tout chiffre issu du dossier de mai 2026 non revérifié ; marché ≠ traction.
3. **Audit d'honnêteté** : fonctionnalités annoncées = statut réel (`07` §4) ; résultats ML avec type de données (réelles / simulées) et métrique.
4. **Questions difficiles** (15) : cold start, WTP, cash, concurrence (Google Maps, WhatsApp), défensibilité, réglementation, équipe à temps partiel, coût LLM, exactitude de l'IA, fraude aux avis, sortie de plateforme (désintermédiation)… avec réponse de 2 phrases et preuve.
5. Rendre : corrections par slide (Bloquant / Important / Suggestion) + fiche Q/R.

## revue-business-hebdo

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
