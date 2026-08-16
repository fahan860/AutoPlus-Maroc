# V1_SCOPE.md — Agent IA de diagnostic AUTO+

**Phase 0 du plan de développement** — Livrable de cadrage avant tout code.

## Objectif de la V1

Permettre à un utilisateur AUTO+ de décrire un problème automobile en langage naturel, obtenir des
questions complémentaires si les informations sont insuffisantes, récupérer les connaissances
pertinentes via RAG (PostgreSQL + pgvector) et recevoir une analyse orientative — jamais un diagnostic
mécanique certain — structurée, prudente et sourcée.

## Ce que V1 doit faire (in scope)

- Recevoir une description libre d'une panne ou d'un symptôme (ex. "ma voiture cale au démarrage").
- Recueillir les informations véhicule minimales : marque, modèle, année, kilométrage approximatif.
- Poser des questions complémentaires ciblées quand l'information est insuffisante pour répondre
  correctement (agent, pas simple formulaire).
- Rechercher dans la Knowledge Base (RAG) les passages pertinents pour la situation décrite.
- Générer via LLM une réponse structurée : résumé, causes possibles, vérifications recommandées,
  niveau de gravité, recommandation de consulter un professionnel, sources utilisées.
- Journaliser les échanges et les décisions de sécurité pour permettre l'évaluation (Phase 15).
- Fonctionner de bout en bout : mobile (React Native) → Node/Express → service Python IA → réponse
  affichée à l'utilisateur.

## Ce que V1 NE fait PAS (hors périmètre)

- Lecture de codes OBD réels depuis un boîtier connecté au véhicule (V2+).
- Utilisation de données capteurs temps réel (V2+).
- Modèle ML de diagnostic entraîné sur des données propriétaires (V1 = RAG + LLM générique, pas de
  modèle prédictif custom).
- Analyse d'image (photo du moteur, du tableau de bord) ou analyse audio (bruit moteur) — évoqué comme
  piste future mais explicitement exclu de la V1.
- Réservation de garage ou paiement déclenchés automatiquement par l'agent (l'app AUTO+ gère déjà la
  prise de RDV séparément ; l'agent peut au mieux *recommander* de contacter un garage).
- Support multilingue complet day-1 : **recommandation** — démarrer en français uniquement pour la V1
  (prompt système, KB, évaluation), le darija étant un problème à part entière (peu de corpus
  disponible, transcription/mélange codique) à traiter comme un chantier V1.5/V2 dédié plutôt que de
  risquer de diluer la qualité du RAG et du LLM dès la V1. À trancher explicitement avec l'équipe avant
  la Phase 8.

## Critères de succès (parcours de bout en bout)

La V1 est considérée fonctionnelle quand ce parcours marche entièrement :

1. Utilisateur → décrit un problème automobile dans l'app mobile.
2. Agent → collecte/valide les informations importantes (véhicule + symptômes), pose des questions si besoin.
3. Agent → interroge la Knowledge Base.
4. RAG → récupère des passages pertinents depuis pgvector.
5. LLM → génère une analyse basée sur le contexte récupéré (jamais hors-contexte).
6. Agent → renvoie une réponse structurée (causes possibles, vérifications, gravité, sources).
7. App mobile → affiche clairement la réponse (nouvel écran de chat AUTO+ AI, cf. Phase 14).
8. Tests → qualité du retrieval, comportement de l'agent et sécurité mesurés (Phase 15).

## Contexte projet (pour rappel)

- Le reste du produit AUTO+ (API Node/Express, PostgreSQL/PostGIS, mobile Expo) est déjà en place et
  fonctionnel : garages, utilisateurs, véhicules, interventions, avis. L'agent IA est un **nouveau
  service** (`/ai`, Python + FastAPI) qui vient s'y greffer, pas une refonte de l'existant.
- Rien n'existe encore côté RAG/Agent/pgvector dans le dépôt à ce jour (16 août 2026) — on part de zéro
  sur ce périmètre, en suivant l'ordre exact de développement du plan (Phase 0 → Phase 16).
- Priorité immédiate selon le plan : **ne pas coder l'agent en premier**. Prochaine étape réelle =
  Phase 1 (schéma Knowledge Base) puis Phase 2 (sources) et un petit corpus propre pour valider
  ingestion → embeddings → pgvector → retrieval, avant d'intégrer le LLM.
