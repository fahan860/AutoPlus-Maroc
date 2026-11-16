# AUTO+ : go-to-market et lancement à Casablanca (09)

> Rôles : GTM Strategist (propriétaire), Garage Partnerships Manager, Growth Lead, PMM (`11`). Procédures : `plan-campagne`, `design-experience` (12).
> Point de départ réel (2026-11-16) : application non déployée, pas de build installable, 0 garage pilote engagé, 0 entretien réalisé. Le calendrier du dossier de mai 2026 (Phase 0 au T3 2026 avec 50 garages pilotes) n'a pas été tenu et est remplacé par celui-ci.
> Dernière mise à jour : 2026-11-16.

## 1. Marché initial

| Choix | Décision | Justification |
|---|---|---|
| Ville | Casablanca | 123 garages en base (91 géolocalisés) `[FAIT]` ; Casablanca-Settat = 35 % du parc national `[FAIT]` (08 §1) |
| Zone de lancement | **2 à 3 quartiers contigus**, choisis là où la densité de garages géolocalisés est la plus forte | Une marketplace locale doit offrir un choix réel à moins de ~3 km (distance moyenne recommandée par le modèle B : 2,6 km) `[FAIT]` |
| Services | Mécanique générale, vidange/entretien, freins, diagnostic | Spécialités les plus fréquentes en base ; 104/123 garages « mécanique générale » `[HYPOTHÈSE]` à confirmer |
| Plateforme | Android d'abord | Priorité 4 de `01` ; part d'Android au Maroc `[À COMPLÉTER : non recherchée lors de la veille du 2026-11-16]` |

Action préalable (1 journée) : requête sur `data/scraping/garages_clean.csv` → nombre de garages géolocalisés par quartier → choix des quartiers.

## 2. Séquence de lancement

| Phase | Période (proposée) | Objectif | Critère de sortie |
|---|---|---|---|
| **P0 — Préparation** | 16 nov. → 20 déc. 2026 | App en ligne + APK bêta ; audit Google Maps des 123 garages (EXP-04) ; 10 visites garages ; 15 entretiens automobilistes | API en ligne (`/health`), APK installable, ≥ 5 garages d'accord pour le pilote, ≥ 10 entretiens synthétisés |
| **Soutenance** | fin déc. 2026 | Démo en ligne + premiers résultats terrain réels | — |
| **P1 — Pilote fermé** | janv. → fév. 2027 | 5–10 garages actifs, 50–100 automobilistes invités | ≥ 70 % des RDV confirmés sous 24 h ; ≥ 20 RDV terminés au total `[HYPOTHÈSE]` |
| **P2 — Bêta ouverte** | mars → mai 2027 | 20–30 garages, Play Store, acquisition locale payante testée | NSM en croissance 4 semaines de suite ; CAC mesuré par canal |
| **P3 — Lancement public Casablanca** | à partir de juin 2027 | Ensemble de Casablanca, première monétisation garage | LTV/CAC estimé ≥ 3 sur au moins un canal |

Risque de calendrier : disponibilité de l'équipe après la soutenance (stages de fin d'études possibles à partir de février 2027) `[À COMPLÉTER : disponibilité réelle de chaque membre]`. Si elle est réduite, P1 se fait en mode concierge minimal (3–5 garages, un quartier).

## 3. Résoudre le cold start (marketplace bi-face)

Ordre : **offre avant demande**, dans une zone dense.

| Levier | Mise en œuvre AUTO+ | Statut |
|---|---|---|
| Valeur « solo » sans réseau | Agent IA de diagnostic en darija et estimation du prix du véhicule : utiles même avec peu de garages | ✅ fonctionnalités existantes |
| Pré-remplir l'offre | 123 fiches scrapées existent déjà ; les garages peuvent revendiquer leur fiche | ✅ (revendication implémentée) |
| Concentration géographique | 2–3 quartiers seulement en P1 | plan |
| Concierge | L'équipe confirme chaque RDV par WhatsApp/téléphone avec le garage pendant le pilote, et relance le client la veille | plan (EXP-05) |
| L'offre amène la demande | QR code et carte « Réserve chez moi via AUTO+ » au comptoir de chaque garage pilote ; avis demandés aux clients habituels | plan (EXP-06, événements parrainage à créer) |
| Garantie de flux pour le garage | **Ne rien promettre en volume** ; offrir gratuité + visibilité + fiche soignée (photos, spécialités confirmées) | règle |
| Communautés existantes | Groupes Facebook/WhatsApp de quartier et d'automobilistes : contenu utile (conseils entretien), pas de spam | plan |
| Qualité avant quantité | Garages pilotes choisis sur note Google/visite ; modération des avis active | ✅ modération |

## 4. Acquisition et onboarding des garages

1. **Ciblage** : garages des quartiers retenus ; priorité aux ateliers avec ≥ 1 critère d'ouverture au digital (WhatsApp Business, fiche Google, mécanicien jeune).
2. **Visite** (20 min) : d'abord l'entretien mécanicien (guide V2, sans parler du produit), puis démonstration de 3 min sur téléphone, puis proposition pilote.
3. **Offre pilote** : gratuit pendant le pilote ; en échange, le garage répond aux demandes sous 24 h et met à jour le statut des RDV. Lettre d'intention simple pour tester le futur frais par RDV honoré (EXP-01).
4. **Onboarding (30 min, sur place)** : revendication de la fiche, photos, horaires, spécialités confirmées, test d'un RDV fictif de bout en bout, ajout dans un groupe WhatsApp « garages pilotes ».
5. **Animation** : appel hebdomadaire ; récapitulatif mensuel (demandes reçues, RDV terminés, avis).
6. **Pipeline** (suivi local, non versionné s'il contient des noms/numéros) : à contacter → visité → intéressé → onboardé → actif → perdu (raison).

Messages garage (voix de marque, sans jargon « marketplace/SaaS ») : clients en plus pendant les jours creux, réputation visible au-delà du quartier, demandes organisées.

## 5. Acquisition des automobilistes

| Canal | Usage pilote | Mesure | Statut |
|---|---|---|---|
| Garages pilotes (QR, comptoir) | Canal n°1 en P1 | code par garage | plan |
| Bouche-à-oreille / parrainage | Invitation par les premiers utilisateurs | `parrainage_*` (à créer) | plan |
| Réseau de l'équipe (ENSA, famille, amis à Casablanca) | Premiers testeurs, signalés comme biaisés | source à l'inscription | plan |
| Instagram / TikTok / Facebook (organique) | Reels « l'IA explique ta panne en darija », conseils entretien | UTM → store | plan (EXP-03) |
| Groupes Facebook / WhatsApp de quartier | Contenu utile, réponse aux questions de pannes | UTM | plan |
| Google Ads (recherche « mécanicien Casablanca », « vidange ») | Test plafonné en P2 seulement | CAC par mot-clé | P2 |
| Meta Ads ciblées quartier | Test plafonné en P2 | CAC | P2 |
| Stations-service, parkings, lavages | Flyers QR, en P2 | code par lieu | P2 |

## 6. Partenariats

| Partenaire | Intérêt pour lui | Intérêt pour AUTO+ | Horizon | Statut |
|---|---|---|---|---|
| OFPPT (centres de formation mécanique) | Insertion des lauréats, digitalisation | Vivier de jeunes mécaniciens early adopters | P2 | `[HYPOTHÈSE]`, aucun contact |
| Incubateurs / programmes (UM6P Explorer, autres) | Pipeline de startups | Accompagnement, réseau, crédits cloud | en cours | `[À COMPLÉTER : statut des candidatures]` |
| Distributeurs de lubrifiants / pneus / pièces | Accès aux garages indépendants | Offres pour garages, cofinancement ; modèle iDGarages/Autodistribution (08 §7) | P2–P3 | `[HYPOTHÈSE]` |
| Centres d'entretien de marque (Piassaty, Speedy, Shell Helix…) | RDV en ligne qu'ils n'affichent pas | Offre crédible dès le pilote | P2 | `[HYPOTHÈSE]` |
| Loueurs de voitures / flottes | Entretien groupé | Revenu récurrent (leçon Pitstop, Carefer, Fixit45) | P3 | `[HYPOTHÈSE]` |
| Assureurs / assistance | Réseau de réparation, réduction de la fraude | Flux de clients, revenus de leads | P3 | `[HYPOTHÈSE]` |
| Lavages / parkings / stations | Service en plus pour leurs clients | Points de distribution physiques | P2 | `[HYPOTHÈSE]` |

## 7. Bêta et lancement public : check-list

**Avant P1** : API déployée et surveillée ; migrations automatiques ; APK signé ; clé Google Maps du build ; Mistral ou Groq configuré avec plafond ; vérification e-mail (SMTP) ou désactivation assumée ; événements de funnel ajoutés ; mentions légales, politique de confidentialité et conditions d'utilisation `[À COMPLÉTER]` ; déclaration CNDP préparée (`08` §6 : régime de déclaration, amende en cas de traitement non déclaré) ; prix affichés comme « indicatifs », jamais fixés par AUTO+ (risque concurrence, `08` §6) ; numéro WhatsApp support.
**Avant P2** : fiche Play Store (FR + darija), visuels, politique d'avis publiée, procédure de litige client/garage.
**Avant P3** : statut juridique pour facturer, contrat garage, moyen de paiement choisi.

## 8. Budget de lancement (hypothèses)

Aucune dépense n'a été engagée à ce jour. Montants en MAD, tous `[HYPOTHÈSE]` ou `[ESTIMATION]` à remplacer par des devis/réels.

| Poste | P0–P1 (déc.–fév.) | P2 (mars–mai) | Base |
|---|---|---|---|
| Hébergement API + base + ML | 0 – [À COMPLÉTER] | [À COMPLÉTER] | Offres gratuites visées (`deploy-engineer`) ; e5-large demande de la mémoire, peut imposer un plan payant |
| LLM (Mistral) | [À COMPLÉTER : coût/conversation × volume] | idem | mesurer avec `evaluer-agent-ia` |
| Compte développeur Google Play | frais unique [À COMPLÉTER : vérifier le montant actuel] | — | — |
| Domaine | ~100 MAD/an | — | `docs/AutoPlus_Plan_Organisation_PreDev.docx` |
| Impression QR / cartes comptoir | [ESTIMATION] quelques centaines de MAD | idem | devis imprimeur |
| Déplacements terrain Casablanca | [À COMPLÉTER] | [À COMPLÉTER] | nombre de visites × coût |
| Publicité test (Meta + Google) | 0 | plafond de test [HYPOTHÈSE : 1 000–2 000 MAD/mois] | le dossier proposait 5 000–10 000 MAD/mois, trop tôt sans conversion mesurée |
| Contenu vidéo | 0 (fait par l'équipe) | 0 | — |

Règle : toute dépense publicitaire passe par `design-experience` avec un CAC cible fixé à l'avance.

## 9. Indicateurs de passage de phase

Voir `10_kpi_experiences.md` §1–3. Décision de passage prise en `revue-business-hebdo` et inscrite au journal (`10` §7).
