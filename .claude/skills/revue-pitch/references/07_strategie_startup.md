# AUTO+ : stratégie startup (07)

> Rôles : Startup Strategist, Business Strategist, PMM (`11`). Sources internes : `docs/AutoPlus_Maroc_Dossier_Startup_2026_CORRIGE.pdf` (mai 2026), `docs/AutoPlus_Lean_BMC.pptx`, `docs/AutoPlus_Assumption_Matrix.xlsx`, `docs/AutoPlus_Analyse_CustomerDiscovery.docx`, dépôt GitHub (état au 2026-11-09). Marché et concurrence : `08`.
> Étiquettes : `[FAIT]`, `[ESTIMATION]`, `[HYPOTHÈSE]`. **Aucune hypothèse client n'est validée à ce jour : 0 entretien terrain réalisé.**
> Dernière mise à jour : 2026-11-16.

## 1. Vision, mission, promesse

- **Vision** : devenir la couche de confiance entre les automobilistes et les garages au Maroc.
- **Mission** : rendre l'entretien et la réparation auto simples, transparents et dignes de confiance, en français et en darija.
- **Promesse de marque** (voix AUTO+, 03) : « Le bon garage, près de chez toi, sans mauvaise surprise. »
- **Périmètre 2026** : pilote Casablanca, PFA (soutenance fin décembre 2026). Les phases nationales et Afrique francophone du dossier de mai 2026 sont des ambitions, pas un plan.

## 2. Problème

| Face | Problème supposé | Hypothèses (matrice) | Statut |
|---|---|---|---|
| Automobiliste | Trouver vite un garage de confiance ; peur de l'arnaque sur le prix ; ne pas comprendre la panne ; ne pas pouvoir vérifier la réparation | H1–H10 (H3 et H9 critiques) | `[HYPOTHÈSE]` toutes « à valider » |
| Garage | Clientèle limitée au bouche-à-oreille ; jours creux ; réputation invisible hors quartier ; litiges dus à la communication technique | H11–H20 (H15, H18, H20 critiques) | `[HYPOTHÈSE]` toutes « à valider » |
| Marché | Secteur largement informel et peu digitalisé | dossier §3 (« 60–70 % informel », attribué au GIPAM) | `[HYPOTHÈSE]` : **aucune source primaire** (le GIPAM représente la pièce de rechange), voir `08` §1 |

Alternatives actuelles : bouche-à-oreille, garage de quartier, concession, Google Maps, groupes Facebook/WhatsApp (voir `08` §4).

## 3. Segments, early adopters et personas

### Segments
| Segment | Description | Priorité pilote |
|---|---|---|
| B2C cœur | Propriétaires de voiture particulière à Casablanca, 25–45 ans, smartphone, voiture utilisée au quotidien | 1 |
| B2C early adopters | 25–35 ans, actifs sur Instagram, ont déjà vécu une mauvaise expérience de garage, cherchent sur Google/WhatsApp | 1 |
| B2B cœur | Garages indépendants de mécanique générale de Casablanca (123 en base, 91 géolocalisés) | 1 |
| B2B early adopters | Jeunes mécaniciens (profil OFPPT) qui veulent digitaliser leur atelier | 1 |
| B2B2C (plus tard) | Flottes d'entreprise, VTC/taxis, loueurs, assureurs | 3 — `[HYPOTHÈSE]` |

### Personas (archétypes de travail, non issus d'entretiens)
| Persona | Situation | Job-to-be-done | Ce qui le ferait adopter AUTO+ | Statut |
|---|---|---|---|---|
| **Salma, 29 ans, cadre, Maârif** | Citadine récente, pas de mécanicien attitré, peu de temps | « Faire réparer sans me faire avoir et sans perdre ma journée » | Avis vérifiés, RDV en 2 min, prix indicatif, explication claire | `[HYPOTHÈSE]` |
| **Youssef, 38 ans, commercial, Hay Hassani** | Voiture de 8–10 ans, gros kilométrage, budget serré | « Comprendre la panne avant d'aller au garage, comparer » | Agent IA en darija, estimation, garages proches | `[HYPOTHÈSE]` |
| **Hamid, 45 ans, garagiste indépendant, Derb Sultan** | Atelier de quartier, clients par bouche-à-oreille, jours creux | « Remplir l'agenda sans payer de pub » | Clients en plus, fiche visible, zéro paperasse, gratuit au départ | `[HYPOTHÈSE]` |
| **Anas, 26 ans, mécanicien OFPPT** | Vient d'ouvrir son atelier, à l'aise avec le téléphone | « Me faire connaître au-delà de ma rue » | Profil, avis, tableau de bord RDV | `[HYPOTHÈSE]` |

Les personas sont à remplacer par des profils issus de `synthese-interviews` (12) dès 5 entretiens par segment.

## 4. Statut réel des fonctionnalités

Source : dépôt `fahan860/AutoPlus-Maroc` (dernier commit 2026-11-09), `06_RAPPORT_AVANCEMENT.md`.

| Fonctionnalité | Statut |
|---|---|
| Inscription / connexion (téléphone ou e-mail), rôles automobiliste / mécanicien, données personnelles chiffrées | ✅ Implémenté |
| Liste et carte des garages (tri par distance), fiche garage | ✅ Implémenté |
| Prise de RDV et cycle de vie (demande → confirmé → en cours → terminé/annulé), « Mes RDV » | ✅ Implémenté |
| Mes véhicules | ✅ Implémenté |
| Avis + modération des faux avis (modèle C, entraîné sur données **simulées**) | ✅ Implémenté |
| Estimation du prix d'un véhicule d'occasion (modèle A, données réelles) | ✅ Implémenté |
| « Quel est le problème ? » → garages conseillés (modèle B, collaboratif sur données simulées) | ✅ Implémenté |
| Agent IA de diagnostic FR/darija + historique | ✅ Implémenté (évaluation chiffrée non faite ; LLM de test Groq) |
| Espace garagiste : création/revendication de garage, tableau de bord, véhicules, avis | ✅ Implémenté |
| Journalisation d'événements Redis → Parquet | ✅ Implémenté (événements de funnel manquants, `10` §2) |
| Déploiement en ligne, migrations automatiques, CI/CD, build Android | 🟡 En développement (priorités 1–4 de `01`) |
| Événements de funnel (ouverture, début RDV, parrainage) | 🟡 En développement |
| Passage à Mistral, évaluation de l'agent | 🟡 En développement |
| Vérification d'e-mail en production (SMTP) | 🟡 Codé, désactivé |
| Notifications / confirmation WhatsApp | ⚪ Planifié |
| Paiement en ligne (CMI, wallets), devis digital, garantie de service | ⚪ Planifié — **aucun code** |
| Rappels d'entretien, historique d'entretien du véhicule | ⚪ Planifié |
| SaaS garage avancé (facturation, stock, CRM) | ⚪ Planifié |
| Diagnostic par boîtier OBD-II | ⚪ Planifié (base de 3 071 codes en place, pas de lecture de boîtier) |
| Marketplace pièces, publicité locale, certification « Auto+ Partner » / EV | 💡 Hypothèse business |
| Parrainage | 💡 Hypothèse (événement prévu) |

Règle PMM : un message public ne promet que des lignes ✅.

## 5. Proposition de valeur

| | Automobiliste | Garage |
|---|---|---|
| Gains | Trouver un garage proche et noté ; comprendre sa panne en darija ; réserver sans appeler ; estimer la valeur de sa voiture | Clients en plus pendant les jours creux ; réputation visible au-delà du quartier ; demandes de RDV organisées |
| Douleurs soulagées | Peur de l'arnaque (avis vérifiés, modération) ; incertitude sur la panne (agent IA) ; temps perdu à chercher | Clients qui arrivent sans comprendre la panne (pré-diagnostic) ; dépendance au bouche-à-oreille |
| Produits | App mobile : carte, fiche, RDV, agent IA, estimation | Espace garagiste dans la même app |
| **Différenciateur** | **Diagnostic IA en darija relié à une recommandation de garage** — à vérifier face aux concurrents (`08` §5) | Gratuit pendant le pilote, aucun outil à installer en plus |

UVP proposée : **« Explique ta panne en darija, trouve le bon garage près de chez toi. »** `[HYPOTHÈSE]` — à tester (EXP-03).

## 6. Business Model Canvas (mis à jour au 2026-11-16)

Base : Lean BMC de mai 2026. Changements : statut réel des fonctionnalités, ajout des risques paiement et cold start.

| Bloc | Contenu | Statut |
|---|---|---|
| Segments | Automobilistes Casablanca 25–45 ans ; garages indépendants de Casablanca | ✓ marché existe / segments à qualifier |
| Proposition de valeur | Garage de confiance + diagnostic IA darija + gestion RDV | `[HYPOTHÈSE]` |
| Canaux | Terrain (garages), garages → clients (QR, parrainage), Instagram/TikTok/Facebook, WhatsApp | `[HYPOTHÈSE]` (`09`) |
| Relation client | Self-service + support WhatsApp humain pendant le pilote (concierge) | `[HYPOTHÈSE]` |
| Revenus | Pilote gratuit ; ensuite commission par RDV honoré et/ou abonnement garage ; premium B2C plus tard | `[HYPOTHÈSE]` (§7) |
| Ressources clés | 123 garages en base, 4 composants IA, base de pannes (50) + 3 071 codes OBD, équipe Big Data & IA | `[FAIT]` (dépôt) |
| Activités clés | Recrutement et animation des garages, acquisition locale, qualité des avis, IA | — |
| Partenaires clés | Garages pilotes ; OFPPT ; plus tard assureurs, distributeurs de lubrifiants/pièces, incubateurs | `[HYPOTHÈSE]` — aucun accord |
| Coûts | Hébergement (offres gratuites visées), API LLM (Groq gratuit / Mistral payant), Google Maps (clé requise pour build), terrain, contenu | `[ESTIMATION]` à chiffrer (`09` §8) |
| Métriques | NSM : RDV terminés / semaine (`10`) | proposé |
| Avantage injuste | Données propriétaires (garages qualifiés, pannes, avis vérifiés) — n'existe qu'après le pilote | `[HYPOTHÈSE]` |

## 7. Sources de revenus évaluées

Grille : faisabilité au Maroc (paiement cash, statut juridique), dépendance à la liquidité, preuve existante, horizon.

### B2C (automobilistes)
| Option | Mécanisme | Avantages | Risques | Verdict |
|---|---|---|---|---|
| Gratuit | — | Lève la barrière d'adoption, nécessaire au cold start | 0 revenu | **Pilote et lancement** |
| Premium (49–99 MAD/mois, dossier) | Assistant illimité, rappels, historique | Récurrent | WTP B2C faible probable dans un marché cash ; promesse dépend de fonctions ⚪ | Tester tard (après rétention mesurée) |
| Frais de service par RDV | X MAD par réservation | Simple | Pousse à appeler le garage en direct (désintermédiation) | À éviter au départ |
| Paiement in-app avec garantie | Marge sur paiement + garantie | Confiance, fidélisation | Aucun code de paiement ; agrément et coûts du prestataire ; habitude du cash | Phase 2, après entretiens H9 + question paiement |

### B2B (garages)
| Option | Mécanisme | Avantages | Risques | Verdict |
|---|---|---|---|---|
| Commission sur ticket (5–10 %, dossier) | % du montant payé | Aligne le prix sur la valeur | Impossible à contrôler sans paiement in-app ; ticket déclaré par le garage | Phase 2 |
| **Frais fixe par RDV honoré** | ex. X MAD par RDV `termine`, confirmé par un code/QR échangé au garage | Mesurable dès aujourd'hui (NSM) ; pas besoin de paiement in-app (facture mensuelle) ; même logique « payer au succès » que iDGarages (10 %), Openbay (10 %), ClickMechanic (20 %) (`08` §7) | Litiges sur RDV « non venus » ; statut juridique requis pour facturer (`08` §6) | **Candidat n°1 à tester** (EXP-01) |
| Abonnement SaaS (299–799 MAD/mois, dossier) | Forfait mensuel | Récurrent, prévisible | Valeur faible tant que peu de clients arrivent ; outils SaaS (facturation, stock) ⚪ | Après liquidité, en paliers |
| Mise en avant (99–299 MAD/mois, dossier) | Position prioritaire | Simple | Contredit la promesse de confiance si mal signalé ; besoin de demande | Phase 2, étiquetée « sponsorisé » |

### Revenus additionnels (tous `[HYPOTHÈSE]`, horizon 2027+)
| Option | Logique | Prérequis |
|---|---|---|
| Leads assurance / assistance | Orienter des automobilistes vers un assureur ou un réseau agréé | Volume d'utilisateurs, accord partenaire, cadre réglementaire de l'intermédiation en assurance à vérifier |
| Partenariats marques (lubrifiants, pneus, pièces) | Offres co-marquées, garages équipés | Réseau de garages actifs |
| Estimation véhicule → leads VO | Le modèle A ✅ peut alimenter des vendeurs / reprises | Partenaire VO |
| Flottes d'entreprise (B2B2C) | Gestion de l'entretien d'une flotte via le réseau | Réseau fiable + facturation |
| Données agrégées anonymisées | Prix, pannes, demande par quartier | Volume ; conformité loi 09-08 / CNDP |
| Marketplace pièces | Commission sur pièces | Logistique, concurrence e-commerce pièces (`08`) |

### Séquence recommandée
1. **Pilote (déc. 2026 – T1 2027)** : gratuit des deux côtés ; mesurer la NSM ; lettres d'intention des garages sur un frais par RDV honoré.
2. **Lancement payant garage** : frais par RDV honoré facturé mensuellement, plafonné ; premiers mois offerts.
3. **Ensuite** : abonnement en paliers (gratuit / pro) quand les outils garage existent ; paiement in-app si les entretiens montrent une acceptation.

## 8. Hypothèses de prix et contraintes de paiement

| Hypothèse | Valeur de travail | Test |
|---|---|---|
| Frais par RDV honoré | [À COMPLÉTER] ; ancrage : vidange « à partir de 370 MAD » (national, AutoActu 01/2026) → un frais de 5–10 % correspondrait à ~20–40 MAD `[ESTIMATION]`, à confirmer par relevé terrain Casablanca (`08` §5) | `validation-prix`, EXP-01 |
| Abonnement garage | 299–799 MAD/mois (dossier) | Van Westendorp + engagement réel |
| Premium B2C | 49–99 MAD/mois (dossier) | après rétention mesurée |

Contraintes (détail et sources : `08` §2 et §6) :
- Économie très cash (≈ 491–513 MMDH de cash en circulation en 2025) et < 5 % des commerçants équipés d'un TPE → pas de paiement in-app au pilote.
- Fin du monopole CMI (mai 2025), 11 opérateurs agréés → options de paiement à comparer en phase 2.
- Auto-entrepreneur possible au départ (IR 1 %, hors TVA) mais retenue de 30 % au-delà de 80 000 MAD avec une même société → SARL (AU) à l'échelle.
- Loi 09-08 : déclaration CNDP avant de traiter les données des utilisateurs réels.
- Loi 31-08 : information sur les prix, CGU ; **AUTO+ n'impose jamais de prix aux garages** (précédent Autobutler, `08` §6).

## 9. Positionnement concurrentiel

Déclaration de positionnement `[HYPOTHÈSE]` :
> Pour les automobilistes de Casablanca qui ont peur de se faire avoir chez le garagiste, AUTO+ est l'application qui explique la panne en darija et oriente vers des garages proches et notés. Contrairement aux annuaires et aux réseaux de centres auto, AUTO+ part du problème du client et couvre les garages indépendants du quartier.

Matrice et sources : `08` §5. Constat de la veille du 2026-11-16 : aucune plateforme B2C de garages de quartier trouvée ; concurrents les plus proches = ReparTrust (B2B sinistres), Carabas (mécanique à domicile), centres d'entretien de marque à Casablanca (Piassaty, Speedy, Shell Helix). Défensibilité visée : densité locale de garages qualifiés + avis vérifiés + données de pannes — aucune n'existe encore à l'échelle.

## 10. Cold start (résumé)

Stratégie détaillée : `09` §3. Principes : **offre d'abord** (garages), **zone restreinte** (2–3 quartiers), **concierge** (WhatsApp manuel), **usage solo** utile sans réseau (agent IA, estimation de prix), **les garages amènent leurs clients** (QR, parrainage).

## 11. Risques business

| Risque | Impact | Mitigation |
|---|---|---|
| Aucune WTP validée (H9, H18) | Modèle de revenus caduc | EXP-01 avant toute annonce de prix |
| Désintermédiation (client et garage se recontactent hors app) | Pas de revenu récurrent | Valeur continue (historique, rappels, avis), frais faible par RDV |
| Cold start : trop peu de garages actifs | Mauvaise première expérience | Concentration géographique, concierge |
| Concurrence de Google Maps / WhatsApp (gratuits, déjà utilisés) | Faible adoption | Différenciation diagnostic darija + avis vérifiés |
| Arrivée d'un acteur financé (ReparTrust, 7,5 MDH, réseau noté + IA en B2B) sur le B2C | Perte de l'avance | Veille trimestrielle (`analyse-concurrent`), vitesse sur la densité locale |
| Prix fixés ou « recommandés » par la plateforme | Risque droit de la concurrence | Fourchettes indicatives uniquement (modèle A/B), devis par le garage |
| Chiffres de marché non vérifiés dans le dossier | Crédibilité au jury / aux investisseurs | Vérification `08` §1 |
| Coût LLM (Mistral payant) | Coût variable par conversation | Mesurer (`evaluer-agent-ia`), limites d'usage |
| Équipe étudiante à temps partiel | Exécution terrain lente | Périmètre pilote réduit, `revue-business-hebdo` |
