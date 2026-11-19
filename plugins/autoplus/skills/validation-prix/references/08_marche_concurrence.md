# AUTO+ : marché et concurrence (08)

> Rôles : Market Researcher, Competitor Analyst (`11`). Procédure : `analyse-concurrent` (12).
> Veille du **2026-11-16** : deux recherches indépendantes (marché/réglementation/international ; concurrence Maroc), puis contre-vérification par le coordinateur des 4 sources structurantes (HCP parc, AIVAM 2026, ReparTrust, Piassaty).
> Étiquettes : `[FAIT]` (source primaire ou presse datée), `[ESTIMATION]` (calcul montré), `[HYPOTHÈSE]`. Numéros entre crochets `[S1]`… = sources du §9.
> Dernière mise à jour : 2026-11-16.

## 1. Vérification des chiffres du dossier startup (mai 2026)

Le dossier `docs/AutoPlus_Maroc_Dossier_Startup_2026_CORRIGE.pdf` reprend en partie des chiffres issus d'une conversation avec un chatbot (`docs/marche/chiffres(automobile market,digitalisation).docx`). Statut après vérification :

| Chiffre du dossier | Verdict | Valeur à utiliser | Source |
|---|---|---|---|
| 235 372 ventes neuves 2025 (+33,4 %) | ✅ Confirmé | 235 372 ; VP **208 848**, VUL 26 524 (le « 210 919 » de l'annexe est faux) | AIVAM via [S1] |
| Ventes 2026 | 🔄 Mis à jour | **208 642 à fin octobre 2026 (+11,9 %)** ; Dacia 41 256, Renault 30 145, Peugeot 12 035 | AIVAM via [S2] (vérifié) |
| Part de Dacia 25 % / 22,7 % | 🔄 Corrigé | 23,35 % des VP sur 11 mois 2025 [S3] ; ≈ 19,8 % du total à fin oct. 2026 `[ESTIMATION]` (41 256 / 208 642) | [S2] [S3] |
| Parc ≈ 4,95 M | ❌ Corrigé | **4 747 215 fin 2024** : 3 112 040 VP, 1 296 174 utilitaires, 339 001 motos | HCP, *Le Maroc en chiffres 2025*, via [S4] (vérifié) |
| Casablanca-Settat ≈ 37 % du parc | ❌ Corrigé | **35 %** (déclaration du président du Conseil régional, mars 2026) | [S5] |
| ~16 000 garages, 4 000 structurés, 25–30 000 informels, 60–70 % d'interventions informelles (« GIPAM ») | ⚠️ Non vérifiable | `[HYPOTHÈSE]` ; le GIPAM regroupe des acteurs de la **pièce de rechange**, pas des garages ; sa seule donnée publique trouvée : marché de la pièce ≈ 20 MMDH | [S6] |
| Smartphone 93 % | ⚠️ Non vérifiable | Utiliser plutôt : **35,8 M d'internautes (92,3 %)**, 56,1 M de connexions mobiles (144 %), 22,9 M d'identités réseaux sociaux | DataReportal *Digital 2027 Morocco* [S7] |
| Abonnés mobiles 54,9 M / 66,1 M | 🔄 Corrigé | ANRT : 59,16 M d'abonnés mobiles fin 2025 | [S8] |
| Dépense d'entretien ~3 000 MAD/an/véhicule | ⚠️ Non vérifiable | `[HYPOTHÈSE]` à mesurer en entretiens | — |
| 18 000 besoins/jour, 95 % hors ligne | ⚠️ Estimation interne | `[ESTIMATION]` : parc × 1,5 visite/an ÷ 365 ; la fréquence 1,5 et la part « en ligne » sont des hypothèses ; volumes Keyword Planner non sourcés | `docs/marche/recherche de users.docx` |
| Âge du parc | 🆕 Ajouté | **13 ans** en moyenne pour les VP (2022, étude projet « Improve ») | [S9] |
| Concurrents SimilarWeb (Drivvo, Logicat…) | ⚠️ Non revérifié | Trafic non revérifié ; **Logicat.ma : aucun lien avec l'automobile trouvé** | §4 |

**Règle** : seuls les chiffres ✅/🔄/🆕 peuvent être présentés comme faits (soutenance, pitch). Proposition : publier une version corrigée du dossier (PR `docs/dossier-startup-v2`) sans écraser le PDF actuel.

## 2. Contexte de marché (faits vérifiés)

| Indicateur | Valeur | Source |
|---|---|---|
| Parc total fin 2024 | 4 747 215 véhicules | [S4] |
| Ventes neuves 2025 / 2026 (10 mois) | 235 372 / 208 642 | [S1] [S2] |
| Âge moyen des VP | 13 ans (2022) | [S9] |
| Part de Casablanca-Settat dans le parc | 35 % | [S5] |
| Internautes | 35,8 M (92,3 %) | [S7] |
| Cash en circulation | ≈ 491–513 MMDH selon la définition (2025) | [S10] [S11] |
| Paiements par carte 2025 | 230,1 M d'opérations (dont 184,5 M sur TPE) | [S10] [S12] |
| E-commerce par carte 2025 | 44,8 M d'opérations, 12,1 MMDH | [S10] |
| M-wallets | 13,7 M fin 2024 (+32 %) | [S13] |
| Équipement des commerçants | ≈ 71 000 TPE ; < 5 % des commerçants équipés | [S14] |

Lecture : parc ancien (entretien et réparations fréquents `[HYPOTHÈSE]`), population très connectée, mais **économie de services encore très cash** et faible équipement des commerçants → le paiement in-app n'est pas un prérequis du pilote.

## 3. TAM, SAM, SOM (recalcul)

Le TAM du dossier (4,95 M × 3 000 MAD = 14,85 Mrd MAD) repose sur un parc surestimé et une dépense non sourcée. Nouveau calcul, paramètres explicites :

| Niveau | Définition | Calcul | Valeur |
|---|---|---|---|
| **TAM** | Dépense annuelle d'entretien/réparation des voitures et utilitaires au Maroc | 4 408 214 véhicules (VP + utilitaires, hors motos) `[FAIT]` × dépense annuelle *D* `[HYPOTHÈSE]` | *D* = 2 000 → 8,8 Mrd MAD ; *D* = 3 000 → 13,2 Mrd MAD `[ESTIMATION]` |
| **SAM** | Même dépense, région Casablanca-Settat | 35 % du parc `[FAIT]` ≈ 1 543 000 véhicules × *D* | *D* = 2 000 → 3,1 Mrd ; *D* = 3 000 → 4,6 Mrd MAD `[ESTIMATION]` |
| **SOM pilote** | Ce que le réseau AUTO+ peut traiter, limité par la capacité des garages actifs | *G* garages actifs × *R* RDV/semaine × 52 × ticket moyen *T* | ex. *G* = 20, *R* = 5 → 5 200 RDV/an × *T* `[HYPOTHÈSE]` |
| **Revenu AUTO+** | Part captée | RDV terminés × frais par RDV (ou *T* × commission) | [À COMPLÉTER après `validation-prix`] |

À compléter : *D* (entretiens + relevé de prix), part de la ville de Casablanca dans la région, *T* (prix observés §5).

## 4. Concurrence au Maroc

Recherche : 26 requêtes (français, anglais, arabe). **Aucune application B2C marocaine de réservation de garages n'a été trouvée** ; Google Play et les groupes Facebook n'ont pas été vérifiés → conclusion non exhaustive.

### Concurrents directs ou partiels
| Acteur | Ce qui est vérifié | Proximité avec AUTO+ | Source |
|---|---|---|---|
| **ReparTrust** (+ Piyes.com) | Levée pré-seed de 7,5 MDH (13/01/2026) ; suivi des réparations après sinistre, pré-inspection par IA, notation des garages (« ReparTrust Scoring ») ; sourcing de pièces via Piyes.com ; cibles B2B (assureurs, loueurs, flottes) ; pilotes prévus au Moyen-Orient. Nombre de garages non publié | Réseau noté + IA, mais B2B sinistres. Pourrait descendre vers le B2C ou s'allier aux assureurs `[HYPOTHÈSE]` | [S15] (vérifié) |
| **Carabas** (Casablanca) | Diagnostic à domicile avec rapport PDF, réparation à domicile, contrôle avant achat, RDV via site ou app | Parcours B2C le plus proche ; activité réelle 2026 non vérifiée | [S16] |

### Concurrents indirects (réseaux d'entretien, assureurs)
| Acteur | Vérifié | Source |
|---|---|---|
| **Piassaty** (Bamotors) | 3 centres à Casablanca (Beauséjour, Zenata, centre-ville), multimarque, vidange/diagnostic/clim/freins/VE, travaille avec assureurs et loueurs ; aucune prise de RDV en ligne mentionnée (23/10/2025) | [S17] (vérifié) |
| **Speedy** (Bridgestone) | 13 centres en 2019, objectif de doublement ; taille 2026 non vérifiée | [S18] |
| **Eurorepar Car Service** (Stellantis) | 1ᵉʳ garage à Casablanca en 2018, objectif 50 garages en 2020 ; taille 2026 non trouvée | [S19] |
| **Shell Helix Service Center** / **Midas** (Vivo Energy) | 1ᵉʳ centre Shell Helix à Casablanca en 2022, sans RDV ; Midas prévu dans des stations Shell (2017) | [S20] [S21] |
| **AutoGo** (Afriquia) | Entretien en station, 8 centres en 2017 | [S22] |
| **Point S** | ~20 points de vente (2020) | [S23] |
| **Fast Pro** | Réseau d'entretien à Casablanca, taille non trouvée | [S24] |
| **Allianz Maroc** | Réparation dans le garage au choix sans avance de frais, accord sous 24 h, parcours digital (sinistres) | [S25] |

### Substituts
Bouche-à-oreille, garage habituel, Google Maps, annuaires (Telecontact), annonces (Avito, non lisible), forums (Moteur.ma : fils « cherche un mécanicien honnête à Casablanca ») [S26], groupes Facebook/WhatsApp (non indexés `[HYPOTHÈSE]`), applis étrangères de carnet d'entretien ou d'OBD (Drivvo, Simply Auto, OBDAI : pas de mise en relation, pas de darija) [S27–S29]. Adjacents : Choufli (cotation VO par IA, avril 2026) [S30], Mister Auto (pièces) [S31].

### Reformulation de l'affirmation du dossier
Remplacer « Le terrain est libre » par :
> Les briques existent séparément (réseaux d'entretien de marque, ReparTrust en B2B sinistres, Carabas à domicile, parcours digitaux d'assureurs), mais aucune plateforme B2C combinant mise en relation avec les garages de quartier, avis vérifiés et diagnostic en darija n'a été trouvée (veille du 16/11/2026, non exhaustive).

## 5. Positionnement et prix observés

### Matrice de positionnement
| Critère | AUTO+ (statut `07` §4) | Fast-fit (Piassaty, Speedy…) | ReparTrust | Carabas | Google Maps | Drivvo / OBDAI |
|---|---|---|---|---|---|---|
| Garages indépendants de quartier | ✅ 123 en base | ❌ centres propres | 🟡 réseau B2B | ❌ mécanicien mobile | ✅ | ❌ |
| RDV en ligne | ✅ | non trouvé | n/a | ✅ | ❌ | ❌ |
| Avis + modération anti-fraude | ✅ (modèle sur données simulées) | — | scoring garages | — | avis non modérés | ❌ |
| Diagnostic IA | ✅ FR/darija | ❌ | pré-inspection IA (carrosserie) | diagnostic humain | ❌ | OBDAI : OBD + IA (anglais) |
| Darija | ✅ | — | — | — | — | ❌ |
| Paiement / garantie | ⚪ planifié | sur place | flux assureur | — | ❌ | ❌ |
| Outil pour le garage | ✅ tableau de bord RDV | interne | ✅ | — | fiche Google | ❌ |

### Prix de référence (à confirmer par relevé terrain)
| Prestation | Prix observé | Source | Fiabilité |
|---|---|---|---|
| Vidange (filtre + jusqu'à 5 L) | à partir de 370 MAD (national) | AutoActu, 13/01/2026 [S32] | prix « à partir de » |
| Kit distribution complet | à partir de 800 MAD | [S32] | idem |
| Purge liquide de frein | à partir de 150 MAD | [S32] | idem |
| Parallélisme | ~100 MAD | [S32] | idem |
| Contrôle technique | 370–400 MAD | [S32] | — |
| Diagnostic à Casablanca | 100–200 MAD, souvent offert si réparation | forum Moteur.ma, ~11 ans [S33] | **obsolète** |

Aucun tarif publié par une enseigne n'a été trouvé → **relevé terrain 2026 à faire** (5–10 garages et fast-fit de Casablanca) avant de fixer le frais par RDV.

## 6. Paiement et réglementation

| Sujet | Fait | Conséquence pour AUTO+ | Source |
|---|---|---|---|
| Acquisition carte | Fin du monopole CMI le 01/05/2025 ; 11 opérateurs agréés (NAPS, Damane Cash, Lana Cash, Chaabi Payment/M2T…) ; plafond de commission de 0,5 % sur cartes marocaines annoncé (titre TelQuel 07/10/2026, mécanisme non vérifié) | Plus d'options qu'en 2024 ; grilles YouCan Pay, Payzone, CMI, NAPS [À COMPLÉTER] | [S14] |
| Accès pour une jeune structure | Immatriculation (RC/ICE) et compte professionnel généralement requis `[HYPOTHÈSE]` | Pilote : paiement au garage en cash, AUTO+ facture plus tard le garage | — |
| Loi 09-08 / CNDP | Régime de déclaration (récépissé), autorisation pour données sensibles ou transfert vers un pays hors liste (à vérifier pour un hébergement cloud à l'étranger) ; amende 10 000–100 000 MAD pour traitement non déclaré | **Déclaration CNDP à préparer avant le pilote** ; vérifier la localisation de l'hébergeur | [S34] [S35] |
| Loi 31-08 (consommateur) | Information et rétractation pour la vente à distance, clauses abusives ; version révisée mentionnée en 2024 | Lire les articles sur prix et devis ; CGU claires ; prix toujours « indicatifs » | [S36] [S37] |
| Auto-entrepreneur | IR 1 % du CA (services), plafond 200 000 MAD, hors TVA ; retenue 30 % au-delà de 80 000 MAD de CA avec une même société cliente | Possible pour démarrer ; **SARL (AU) nécessaire** si facturation à des garages en société | [S38] |
| Droit de la concurrence | Autobutler (Danemark) sanctionné pour prix fixes convenus avec des garages (amende 7 M DKK) | **Ne jamais fixer les prix des garages** : fourchettes indicatives seulement | [S39] [S40] |
| TVA sur services numériques | non vérifié | [À COMPLÉTER : CGI] | — |

## 7. Modèles internationaux adaptables

| Acteur (pays) | Modèle | Ce qui est vérifié | Leçon pour AUTO+ |
|---|---|---|---|
| iDGarages (France) | Commission 10 % sur devis transformés, sans abonnement | ~1 200 garages en 2015 ; actionnaire Autodistribution (pièces) | Commission au succès + partenaire pièces [S41] |
| Vroomly (France) | Frais d'inscription garages + vente de pneus montés | ~3 000 garages ; démarrage avec 22 M d'interventions pour comparer les prix | Démarrer avec des données [S42] |
| ClickMechanic (UK) | Commission 20 % + TVA sur réservations réalisées, sans abonnement | prix fixes en ligne, mécaniciens mobiles | Zéro coût d'entrée pour le pro [S43] |
| Fixter (UK) | Réservation + collecte/livraison du véhicule | > 500 garages, revenu net +200 % (2021) | Service concierge comme différenciateur [S44] |
| Openbay (US) | 10 % par transaction, paiement plateforme | pilote à Boston avant national | Lancement ville par ville [S45] |
| YourMechanic / Wrench (US) | Mécanique mobile | consolidation par rachats | Les acteurs isolés ont été absorbés [S46] |
| Autobutler (Danemark) | Comparateur de devis | sanction pour prix convenus | Risque concurrence [S39] |
| GoMechanic (Inde) | Réseau d'ateliers de marque | 2023 : revenus gonflés, garages fictifs, 70 % de licenciements, revente | Métriques auditées, garages vérifiés [S47] |
| Pitstop (Inde), Carefer (Arabie saoudite), Fixit45 (Nigeria) | B2C + offre flottes ; Fixit45 adossé à la pièce | levées 1–3 M$ | Offre flottes tôt [S48–S50] |
| 3atlana, FriendyM (Égypte) | Entretien + assistance + rappels | 3atlana adossé à Ghabbour Auto | Partenaire groupe automobile [S51] [S52] |
| FIX'N'GO (Tunisie) | Chaîne propriétaire qui lance son app (oct. 2025) | — | Les réseaux fast-fit vont se digitaliser [S53] |

**5 leçons** : (1) payer au succès, pas d'abonnement au départ ; (2) ne jamais fixer les prix ; (3) garages vérifiés sur place et métriques auditables ; (4) partenaire pièces ou groupe automobile pour accéder aux garages ; (5) offre flottes (loueurs, VTC) comme revenu récurrent `[HYPOTHÈSE]`.

## 8. Impact pour AUTO+

| Type | Constat | Action |
|---|---|---|
| Opportunité | Aucune plateforme B2C de garages de quartier trouvée | Concentrer le message sur « garages de ton quartier + darija » |
| Opportunité | Fast-fit présents mais sans RDV en ligne visible | Partenariat possible (centres pilotes) plutôt que concurrence frontale |
| Opportunité | Modèle « commission au succès » éprouvé à l'étranger | Tester un frais par RDV honoré (EXP-01) |
| Menace | ReparTrust financé, réseau noté + IA | Surveiller tous les trimestres ; différencier par le B2C entretien courant et la darija |

## 9. Sources

Toutes consultées le 2026-11-16. « (vérifié) » = recontrôlée par le coordinateur.

| # | Titre | URL | Date |
|---|---|---|---|
| S1 | Marché automobile 2025 : 235 372 immatriculations (Le Matin) | https://lematin.ma/automobile/marche-automobile-marocain-2025-235372-immatriculations-un-record/324439 | 15/01/2026 |
| S2 | Ventes +11,9 % à fin octobre 2026 (FNH) (vérifié) | https://fnh.ma/articles/marche-automobile-les-ventes-progressent-de-11-9-a-fin-octobre-2026 | 03/11/2026 |
| S3 | Automobile 2025, une année de records (La Vie Éco) | https://www.lavieeco.com/affaires/automobile-2025-une-annee-de-records/ | 23/12/2025 |
| S4 | Parc automobile 2024, HCP (Infomédiaire) (vérifié) | https://www.infomediaire.net/?p=187463 | 05/12/2025 |
| S5 | Mobilité à Casablanca (Le Matin) | https://lematin.ma/regions/mobilite-a-casablanca-et-si-le-salut-passait-par-le-transport-en-commun/337661 | 31/03/2026 |
| S6 | Pièce de rechange : GIPAM (EcoActu) | https://ecoactu.ma/piece-de-rechange-automobile-gipam/ | 22/11/2022 |
| S7 | Digital 2027 Morocco (DataReportal) | https://datareportal.com/reports/digital-2027-morocco | 05/11/2026 |
| S8 | Téléphonie mobile fin 2025 (FNH) | https://fnh.ma/article/actualite-economique/telephone-mobile-maroc-2025-decembre | 16/03/2026 |
| S9 | Voitures électriques… âge moyen 13 ans (Le Matin) | https://lematin.ma/economie/voitures-electriquesle-maroc-toujours-sans-regles-defficacite-energetique/371254 | 20/10/2026 |
| S10 | Bank Al-Maghrib, rapport moyens de paiement 2025 | https://www.bkam.ma/content/download/852741/9198194/Rapport%20annuel%20DSSMP%202025.pdf | 2026 |
| S11 | Le cash atteint un niveau record (Le Matin) | https://lematin.ma/economie/le-cash-atteint-un-niveau-record-au-maroc/357147/amp | 21/07/2026 |
| S12 | Paiements par carte en 2025 (FNH) | https://fnh.ma/articles/paiements-par-carte-au-maroc-operations-en-2025 | 23/10/2026 |
| S13 | M-wallets en plein essor (Le Matin) | https://lematin.ma/economie/les-m-wallets-en-plein-essor-grace-aux-aides-sociales/315590/amp | 26/11/2025 |
| S14 | End of the CMI monopoly (TelQuel) | https://telquel.ma/2025/09/08/electronic-payments-will-the-end-of-the-cmi-monopoly-really-get-the-ball-rolling_1944604 | 08/09/2025 |
| S15 | ReparTrust lève 7,5 MDH (Le Matin) (vérifié) | https://lematin.ma/economie/repartrust-leve-75-mdh-pour-digitaliser-la-reparation-automobile/324090/amp | 13/01/2026 |
| S16 | Carabas (VC4A) | https://vc4a.com/ventures/carabas/ | non datée |
| S17 | Piassaty, 3ᵉ centre à Casablanca (Infomédiaire) (vérifié) | https://www.infomediaire.net/?p=184854 | 23/10/2025 |
| S18 | Speedy : nouvelles ambitions au Maroc (j2rauto) | https://j2rauto.com/reseaux/speedy-de-nouvelles-ambitions-au-maroc | 02/10/2019 |
| S19 | Euro Repar Car Service démarre (FNH) | https://fnh.ma/article/actualite-economique/euro-repar-car-service-demarre-ses-activites | 18/07/2018 |
| S20 | First Shell Helix Service Center in Casablanca (MWN) | https://www.moroccoworldnews.com/2022/05/45384/vivo-energy-morocco-opens-first-shell-helix-service-center-in-casablanca/ | 31/05/2022 |
| S21 | Midas / Vivo Energy (Franchise Magazine) | https://www.franchise-magazine.com/news-franchise/midas-shell-vivo-energy-afrique | 19/09/2017 |
| S22 | AutoGo, Afriquia (Wandaloo) | https://www.wandaloo.com/autonews/marque/modele/-autogo-_quand-afriquia-se-met-a-l-entretien-automobile/1909.html | 04/02/2017 |
| S23 | Point S Maroc (Bladi) | https://www.bladi.net/point-s-maroc,74837.html | 12/10/2020 |
| S24 | Fast Pro (Telecontact) | https://www.telecontact.ma/annonceur/fast-pro/2214505/casablanca.php | non datée |
| S25 | Allianz Maroc, parcours automobile (FNH) | https://fnh.ma/article/actualites-marocaines/allianz-maroc | 09/07/2025 |
| S26 | Forum Moteur.ma : mécanicien honnête à Casablanca | https://www.moteur.ma/fr/forum/voiture-automobile-bagnole/40161,cherche-un-bon-mecanicien-competent-et-honnete-a-casablanca.html | non datée |
| S27 | Drivvo (App Store) | https://apps.apple.com/app/id1206041425 | consultée 16/11/2026 |
| S28 | OBDAI (App Store) | https://apps.apple.com/us/app/id6741182859 | consultée 16/11/2026 |
| S29 | Simply Auto (App Store) | https://apps.apple.com/us/app/id893278325 | mise à jour 24/03/2022 |
| S30 | Choufli (MWN) | https://www.moroccoworldnews.com/2026/04/285346/choufli-the-moroccan-startup-bringing-ai-powered-car-pricing-to-morocco/ | 01/04/2026 |
| S31 | Mister Auto Maroc (FNH) | https://fnh.ma/article/actualite-entreprises/pieces-detachees-mister-auto-maroc-filiale-de-psa-accelere-son-developpement | 25/06/2019 |
| S32 | Entretien voiture : astuces (AutoActu) | https://autoactu.ma/2026/01/13/entretien-voiture-astuces-economiser-maroc-2025/ | 13/01/2026 |
| S33 | Prix du diagnostic à Casa (Moteur.ma) | https://www.moteur.ma/fr/forum/voiture-automobile-bagnole/23448,prix-du-diagnostic-a-casa.html | ~2015 |
| S34 | Déclarations et autorisations CNDP (Upsilon) | https://upsilon-consulting.com/declarations-autorisations-cndp-guide-pratique/ | 02/04/2026 |
| S35 | CNDP délibération D-939-2025 | https://www.cndp.ma/wp-content/uploads/2025/12/Deliberation-N%C2%B0-D-939-2025-du-28112025-relative-au-modele-de-declaration-simplifiee-relative-au-traitement-des-donnees-a-caractere-personnel-de-cookies-sur-un-terminal.pdf | 28/11/2025 |
| S36 | Loi 31-08 (Adala, texte) | https://adala.justice.gov.ma/api/uploads/2024/03/01/protection%20de%20consommateur-1709283839988.pdf | loi du 07/04/2011 |
| S37 | Nouveau cadre protection du consommateur (CMS) | https://cms.law/fr/mar/legal-updates/flash-info-maroc-le-nouveau-cadre-legislatif-de-la-protection-du-consommateur | non datée |
| S38 | Auto-entrepreneur : régime fiscal (Upsilon) | https://upsilon-consulting.com/auto-entrepreneur-ir-regime-fiscal-maroc/ | 27/04/2026 (rév. 06/11/2026) |
| S39 | KFST : Autobutler a enfreint le droit de la concurrence | https://en.kfst.dk/nyheder/kfst/english/decisions/20230628-the-danish-competition-council-autobutler-has-infringed-competition-law | 28/06/2023 |
| S40 | FDM : amende Autobutler | https://fdm.dk/nyheder/bilist/2025-01-autobutler-betaler-millionboede-aftalte-priser | 10/01/2025 |
| S41 | iDGarages vise 2 000 adhérents (L'argus) | https://www.largus.fr/pros/actualite-automobile/idgaragescom-vise-2000-adherents-en-2015-5956387.html | 16/02/2015 |
| S42 | Histoire de Vroomly (Siècle Digital) | https://siecledigital.fr/2022/11/23/histoire-start-up-vroomly/ | 23/11/2022 |
| S43 | ClickMechanic : frais | https://chat-help.clickmechanic.com/hc/en-gb/articles/7188013964829-Do-you-charge-any-fees | non datée |
| S44 | Fixter +200 % (PR Newswire) | https://www.prnewswire.co.uk/news-releases/online-car-servicing-and-maintenance-continues-to-grow-significantly-during-lockdown-as-fixter-uk-s-first-digital-provider-reports-200-revenue-growth-833172066.html | 25/02/2021 |
| S45 | Openbay launches (TechCrunch) | https://techcrunch.com/?p=905950 | 28/10/2013 |
| S46 | Wrench acquires YourMechanic (GeekWire) | https://www.geekwire.com/2022/mobile-car-repair-startup-wrench-acquires-another-competitor-swoops-up-yourmechanic/ | 2022 |
| S47 | GoMechanic acquired by Lifelong (TechCrunch) | https://techcrunch.com/2023/03/28/distressed-indian-startup-gomechanic-acquired-by-lifelong-group-led-consortium | 28/03/2023 |
| S48 | Pitstop (Inc42) | https://inc42.com/?p=117485 | 06/03/2018 |
| S49 | Carefer pre-Series A (Waya) | https://waya.media/carefer-raises-2-9m-in-a-pre-series-a-round/ | 13/02/2023 |
| S50 | Fixit45 lève 1,9 M$ (TechCabal) | https://techcabal.com/2023/09/21/fixit45-raises-1-9-million-to-expand/ | 21/09/2023 |
| S51 | 3atlana seed (Wamda) | https://www.wamda.com/en/2022/09/egyptian-car-service-app-3atlana-closes-seed-round | 09/2022 |
| S52 | FriendyM 2 M$ (Techpoint) | https://techpoint.africa/2024/01/15/egypts-friendym-funding-scale-nationwide/ | 15/01/2024 |
| S53 | FIX'N'GO lance son application (automobile.tn) | https://www.automobile.tn/fr/magazine/actu/2025-10-28-fixngo-lance-une-application-mobile-innovante-pour-les-automobilistes.html | 28/10/2025 |

### Non accessibles ou non vérifiés lors de cette veille
speedy.ma, eurorepar.ma, logicat.ma, pages Avito, fiches Google Play, groupes Facebook/WhatsApp, TelQuel 07/10/2026 (plafond 0,5 %), grilles tarifaires des prestataires de paiement, TVA sur services numériques.
