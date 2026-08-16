# sources.md — Sources de la Knowledge Base (Agent IA AUTO+)

**Phase 2 du plan de développement.** Trois familles de départ, à documenter systématiquement
(origine, licence, format, date, catégorie, conditions de réutilisation) avant toute ingestion.

> **Correction (16 août 2026)** : la version précédente de ce document proposait d'utiliser
> `AutoPlus_Guide_Interview_Terrain.docx` / `AutoPlus_Guide_Interview_V2.docx` comme source de
> connaissance experte. Vérification faite : ce sont des **questionnaires vides de type "customer
> discovery"** (parcours client, prix payé, canal de découverte du mécanicien) — aucune interview
> technique n'a encore été menée, et même menées, ces guides ne visent pas à collecter des cas
> techniques (symptôme → cause → vérification). Cette source est donc repoussée (voir famille 3
> révisée ci-dessous) et remplacée pour le démarrage par une source disponible immédiatement.

## 1. Données OBD / DTC

| Champ | Détail |
|---|---|
| **Origine** | Codes génériques SAE J2012 / ISO 15031-6 (`P0xxx`, standardisés, indépendants du constructeur). |
| **Licence** | Codes = standard technique, réutilisable. Descriptions détaillées d'un site tiers = à reformuler, jamais copier verbatim. |
| **Format** | CSV/YAML structuré : code, libellé, système, causes typiques. |
| **Date** | Standard stable. |
| **Catégorie** | `obd_dtc`, croisée avec les autres catégories. |
| **Conditions de réutilisation** | Codes libres ; contenu reformulé par l'équipe. |
| **Statut** | ✅ Utilisé pour le corpus V1 (voir `ai/data/processed/kb_corpus_v1.csv`). |

## 2. Documentation technique légalement réutilisable

| Champ | Détail |
|---|---|
| **Origine** | Notices utilisateur constructeur en accès libre, contenus sous licence ouverte (CC-BY-SA avec attribution). |
| **Licence** | À vérifier au cas par cas — jamais de manuel d'atelier propriétaire sans licence explicite. |
| **Format** | PDF, HTML → extraction texte (Phase 3). |
| **Date** | À tracer par document. |
| **Catégorie** | Toutes, selon le document. |
| **Conditions de réutilisation** | Risque juridique réel si mal géré (produit commercial) — reporté après validation du pipeline. |
| **Statut** | ⏳ Non démarré, volontairement reporté. |

## 3. Connaissances / cas structurés d'experts (révisé)

| Champ | Détail |
|---|---|
| **Origine** | **3a. Connaissances techniques génériques rédigées par l'équipe** (savoir automobile courant et non-propriétaire — pannes fréquentes, bien documentées publiquement, reformulées en français clair) : utilisées pour le corpus V1. **3b. Interviews techniques terrain** (futur) : à mener avec 1-2 mécaniciens dès que possible pour enrichir la base avec des cas réels marocains — format décrit ci-dessous, pas de document séparé. |
| **Licence** | 3a : propriété AUTO+ (rédigé par l'équipe). 3b : idem une fois collecté, avec accord des mécaniciens interviewés. |
| **Format** | CSV/YAML au format `KB_SCHEMA.md`. |
| **Date** | 3a : 16 août 2026. 3b : à venir. |
| **Catégorie** | Toutes. |
| **Conditions de réutilisation** | Aucune contrainte externe. |
| **Statut** | 3a ✅ fait (corpus V1). 3b ⏳ planifié, format prêt à l'emploi ci-dessous dès qu'un mécanicien est disponible. |

### Format des interviews techniques (3b)

Différent du guide "customer discovery" existant (`AutoPlus_Guide_Interview_Terrain.docx` /
`AutoPlus_Guide_Interview_V2.docx`) : ici on ne cherche pas le parcours client ou le prix payé, mais
des **cas techniques concrets** exploitables directement dans le format `KB_SCHEMA.md`.

Durée estimée : 20-30 min, format libre autour de 4-5 pannes fréquentes que le mécanicien rencontre.

**Déroulé** :

1. **Introduction courte** : "Je construis une base de connaissances pour aider les automobilistes à
   comprendre un problème avant de venir au garage — pas pour remplacer un diagnostic, juste pour
   mieux orienter. Je vais vous demander de me décrire 4-5 pannes fréquentes que vous voyez souvent."

2. **Pour chaque panne évoquée, poser ces questions dans l'ordre** (remplir directement une ligne du
   corpus au format `kb_corpus_v1.csv`) :

   | Question posée au mécanicien | Champ KB rempli |
   |---|---|
   | "Quel symptôme le client vous décrit en premier ?" | `symptome` |
   | "Sur quel(s) type(s) de véhicule vous voyez ça le plus souvent ici ?" | `vehicule` |
   | "C'est plutôt lié à quelle partie de la voiture ?" | `systeme` |
   | "Une fois que vous ouvrez le capot, c'est généralement dû à quoi ?" | `cause` |
   | "Vous expliqueriez ça comment à un client qui n'y connaît rien ?" | `explication` |
   | "Avant de venir au garage, qu'est-ce que le client pourrait vérifier lui-même sans risque ?" | `verification` |
   | "Sur une échelle faible / moyenne / élevée / critique, c'est urgent comment ?" | `gravite` |
   | "Vous avez déjà vu un cas où quelqu'un a roulé trop longtemps avec ça et ça a empiré ?" | contexte pour `gravite` + note libre |

3. **Après l'interview** : reformuler les notes dans le CSV/YAML du corpus, ne jamais copier les mots
   exacts du mécanicien tels quels s'il a mentionné un client ou un garage concurrent nommément
   (anonymiser).

4. **Remercier et noter la source** : `source = interview_technique_[nom_ou_id]_[date]` pour tracer
   la provenance ici même, dans ce fichier.

**Bonnes pratiques** :

- Privilégier des mécaniciens généralistes (pas hyper-spécialisés) pour couvrir un maximum de
  catégories en peu d'interviews.
- 3-4 mécaniciens suffisent pour un premier enrichissement notable (15-20 cas de plus).
- Combiner avec les visites déjà prévues au planning (Semaine 3, garages Sidi Maarouf) plutôt que
  d'organiser des visites dédiées supplémentaires.

## Sources à ajouter progressivement (hors démarrage V1)

- NHTSA (base de données de plaintes/rappels US — pertinence à valider pour le marché marocain).
- Datasets de recherche académique sur le diagnostic automobile (à évaluer licence par licence).
- Interviews techniques terrain (3b) une fois menées.
- Nouveaux cas réels remontés via l'usage de l'app une fois en production (boucle de feedback V1.5+).

## Recommandation de démarrage (mise à jour)

Corpus V1 = codes DTC génériques (famille 1) + connaissances techniques génériques rédigées par
l'équipe (famille 3a) — permet de valider dès maintenant ingestion → embeddings → pgvector → retrieval
sans dépendance externe. Les interviews techniques terrain (3b, format ci-dessus) et la documentation
sous licence (famille 2) viendront enrichir la base une fois le pipeline validé.
