# AUTO+ : KPI, expériences et décisions (10)

> Rôles : Growth Lead (propriétaire), marketing-analyst (mesure, 02), CSO (décisions). Procédures : `design-experience`, `revue-business-hebdo` (12).
> **Aucune valeur mesurée à ce jour** : l'application n'est pas en ligne et aucun utilisateur réel n'est inscrit (seed de 30 automobilistes fictifs). Toutes les cibles sont des `[HYPOTHÈSE]`.
> Dernière mise à jour : 2026-11-16.

## 1. North Star Metric

**Proposition : nombre de RDV terminés par semaine à Casablanca** (`interventions.statut = 'termine'`).

| Pourquoi | Limite |
|---|---|
| Seul moment où les deux faces obtiennent de la valeur (client réparé, garage payé) | Ne mesure pas la satisfaction → suivre aussi la note moyenne post-RDV |
| Déjà mesurable : cycle `demande → confirme → en_cours → termine/annule` (API) et événement `rdv_statut_change` | Dépend de la mise à jour du statut par le garagiste → à vérifier en pilote |
| Base naturelle d'une future commission | — |

Métriques d'équilibre (« input metrics ») : garages actifs / semaine (≥ 1 RDV confirmé), délai médian de confirmation, taux de RDV annulés.

## 2. Funnel et événements

| Étape | Définition | Événement existant (`api/src/events.js`) | Statut |
|---|---|---|---|
| Acquisition | installation / première ouverture | — | **manquant** : `app_ouverte` (priorité 2 de `01`) |
| Inscription | compte créé | `user_register` | ✅ |
| Activation 1 | recherche ou diagnostic | `recherche_garage`, `recommandation_garages`, `agent_message` | ✅ |
| Activation 2 | fiche garage vue | `consultation_garage` | ✅ |
| Intention | début de réservation | — | **manquant** : `rdv_debut` |
| Conversion | RDV demandé | `rdv_demande` | ✅ |
| Confirmation | RDV confirmé par le garage | `rdv_statut_change` (statut `confirme`) | ✅ |
| Réalisation | RDV terminé (NSM) | `rdv_statut_change` (statut `termine`) | ✅ |
| Recommandation | avis posté | `avis_poste` | ✅ |
| Referral | parrainage | — | **manquant** : `parrainage_envoye`, `parrainage_converti` |
| Face garage | garage créé / revendiqué | `garage_cree`, `garage_cree_par_mecanicien` | ✅ |

Autres événements existants : `user_login`, `email_verifie`, `vehicule_ajoute`, `estimation_prix_vehicule`, `agent_conversation_supprimee`, `admin_*`.
Événements à ajouter (ticket technique, une PR) : `app_ouverte`, `rdv_debut`, `parrainage_envoye`, `parrainage_converti`, `garage_onboarde` (fiche complétée), source d'acquisition (`utm_source` / code) à l'inscription.

## 3. Tableau de bord cible

| Famille | KPI | Formule | Cible pilote | Valeur |
|---|---|---|---|---|
| Acquisition | Inscriptions / semaine | count `user_register` | [HYPOTHÈSE] [À COMPLÉTER] | non mesuré |
| Activation | % inscrits avec `rdv_demande` sous 7 j | — | [HYPOTHÈSE] 20 % | non mesuré |
| Liquidité | % de `rdv_demande` confirmés sous 24 h | — | [HYPOTHÈSE] ≥ 70 % | non mesuré |
| Réalisation | NSM : RDV terminés / semaine | — | [À COMPLÉTER après 4 semaines de pilote] | non mesuré |
| Rétention auto | % d'utilisateurs avec un 2ᵉ RDV sous 90 j | cohortes mensuelles | [HYPOTHÈSE] | non mesuré |
| Rétention garage | garages actifs S+4 / garages onboardés | — | [HYPOTHÈSE] ≥ 60 % | non mesuré |
| Qualité | note moyenne post-RDV ; % d'avis masqués par la modération | `reviews` | — | non mesuré |
| IA | conversations agent → `rdv_demande` | — | — | non mesuré (évaluation `evaluer-agent-ia` à faire) |
| Revenu | revenu par RDV terminé ; MRR garages | — | 0 pendant le pilote (gratuit) | 0 |

## 4. CAC, LTV et unit economics

Formules à appliquer dès que des dépenses et des revenus réels existent :

- **CAC** (par face) = dépenses d'acquisition de la période ÷ nouveaux utilisateurs activés de la face. Inclure le temps terrain valorisé à part (heures × taux horaire hypothétique).
- **LTV garage** = revenu mensuel moyen par garage × marge brute × durée de vie moyenne (mois) = revenu mensuel × marge ÷ churn mensuel.
- **LTV automobiliste** = RDV / an × revenu par RDV × marge × durée de vie (ans).
- **Ratio cible** LTV/CAC ≥ 3 ; délai de remboursement du CAC ≤ 12 mois (repères usuels SaaS/marketplace, à adapter).

| Paramètre | Valeur | Statut |
|---|---|---|
| Prix abonnement garage | 299–799 MAD/mois (dossier mai 2026) | [HYPOTHÈSE] non testé (H18) |
| Commission | 5–10 % du ticket (dossier mai 2026) | [HYPOTHÈSE] non testé ; aucun paiement intégré |
| Ticket moyen d'une intervention à Casablanca | [À COMPLÉTER : entretiens + prix publiés, `08` §5] | — |
| Churn garage | [À COMPLÉTER] | — |
| Coût d'acquisition garage (visite terrain) | [À COMPLÉTER : heures/visite × visites/garage signé] | — |
| Coût variable par conversation IA (LLM) | [À COMPLÉTER : mesurer via `evaluer-agent-ia`] | — |

## 5. Hypothèses financières de travail

Les projections du dossier de mai 2026 (an 1 : 200 garages, 15 000 utilisateurs, ~1,8 M MAD) **ne sont adossées à aucune mesure** et supposaient un lancement au T3 2026 qui n'a pas eu lieu. Elles sont conservées dans le PDF mais ne doivent plus être citées comme objectifs. Un scénario prudent sera recalculé quand la procédure `validation-prix` aura produit un prix validé et que 4 semaines de pilote auront donné un premier taux de conversion.

## 6. Backlog d'expériences

| ID | Hypothèse (ID matrice) | Méthode | Métrique · seuil | ICE | Statut |
|---|---|---|---|---|---|
| EXP-01 | H18 : les garages acceptent de payer pour des clients qualifiés | 10 visites + proposition « pilote gratuit 3 mois puis X MAD » avec lettre d'intention | ≥ 5 lettres signées sur 10 | 8·6·7 | à lancer |
| EXP-02 | H9 : les automobilistes réservent via l'app plutôt que par bouche-à-oreille | Bêta Android + 3 garages pilotes d'un même quartier | ≥ 20 % des inscrits font un `rdv_demande` sous 7 j | 9·5·5 | bloqué (déploiement + build) |
| EXP-03 | Le diagnostic IA en darija attire des automobilistes | Reel/TikTok « l'IA t'explique ta panne » → lien store | taux clic → inscription [à fixer] | 6·5·8 | à lancer après bêta |
| EXP-04 | H19 : les garages ont peu de présence digitale | Audit Google Maps des 123 garages (fiche, nombre d'avis, note) | part sans fiche ou < 10 avis ; si < 30 %, revoir la promesse « visibilité » | 7·8·9 | **à lancer en premier** (bureau, 1 journée) |
| EXP-05 | WhatsApp est le bon canal de confirmation | Concierge : confirmations RDV envoyées à la main sur WhatsApp pendant le pilote | taux de RDV honorés vs sans relance | 6·6·7 | à lancer en pilote |
| EXP-06 | Le parrainage garage → client fonctionne | QR code au comptoir de chaque garage pilote | inscriptions par garage / semaine | 7·5·6 | bloqué (événements parrainage) |

ICE = Impact · Confiance · Facilité (1–10), à réviser après chaque revue hebdo.

## 7. Journal de décisions

Format : `AAAA-MM-JJ · Décision · Raison · Source · Réversible ?`

| Date | Décision | Raison | Source | Réversible |
|---|---|---|---|---|
| 2026-05 | Modèle de revenus envisagé : SaaS garage + commission + leads + freemium B2C | Dossier startup | `docs/AutoPlus_Maroc_Dossier_Startup_2026_CORRIGE.pdf` | oui (non validé) |
| 2026-07 | Pilote limité à Casablanca | 123 garages scrapés à Casablanca, concentration du parc | `06_RAPPORT_AVANCEMENT.md` | oui |
| 2026-07 | Application mobile Expo au lieu du MVP web Next.js prévu | Constat dépôt : `mobile/` développé, pas de Next.js | dépôt ; contredit `docs/AutoPlus_Checklist_Avancement.md` | — |
| 2026-08-18 | Agent IA en français et darija dès la V1, KB en français | Décision d'équipe | `05_README.md` | oui |
| 2026-10 | Terrain (entretiens, garages pilotes) non réalisé ; priorité aux composants IA | Arbitrage de temps | `06_RAPPORT_AVANCEMENT.md` §3 | — |
| 2026-11-16 | Pilote gratuit pour les deux faces jusqu'à liquidité mesurée ; monétisation testée par lettres d'intention garages | Cold start, aucune WTP validée | `07` §7, `09` | oui — **proposée, à confirmer par l'équipe** |
