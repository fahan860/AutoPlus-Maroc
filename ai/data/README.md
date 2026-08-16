# ai/data/ — Knowledge Base AUTO+

Ce dossier contient le corpus de connaissances utilisé pour le RAG de l'agent IA AUTO+ (cf.
`ai/docs/V1_SCOPE.md`, `ai/docs/KB_SCHEMA.md`, `ai/docs/sources.md`).

## Structure

```
ai/data/
├── raw/          # Extraits bruts non retravaillés de futures sources (ex. PDF/HTML de doc
│                 #  constructeur, notes brutes d'interviews terrain une fois menées).
│                 #  Vide pour l'instant : aucune source de ce type n'a encore été traitée.
├── processed/    # Corpus prêt à l'emploi, conforme à ai/docs/KB_SCHEMA.md, validé par
│                 #  ai/scripts/validate_knowledge_base.py.
│   └── kb_corpus_v1.csv
└── README.md     # ce fichier
```

## Pipeline prévu (Phase 3+, pas encore implémenté)

```
raw/ (sources brutes)
   ↓ extraction / nettoyage
processed/*.csv (conforme KB_SCHEMA.md)
   ↓ chunking
chunks
   ↓ embeddings
vecteurs
   ↓ indexation pgvector
retrieval
```

Seule la première partie (constitution d'un corpus `processed/` propre et validé) est réalisée à ce
stade. Chunking, embeddings, pgvector et retrieval sont hors périmètre de cette phase (cf.
`ai/docs/V1_SCOPE.md`).

## Corpus actuel : `processed/kb_corpus_v1.csv`

- 22 entrées, rédigées par l'équipe à partir de deux sources autorisées uniquement :
  - `dtc_generique_saeJ2012_iso15031` : nomenclature de codes DTC génériques (SAE J2012 / ISO
    15031-6), reformulée, jamais copiée verbatim d'un site tiers.
  - `connaissances_generiques_equipe` : savoir automobile courant, non-propriétaire, rédigé par
    l'équipe.
- Aucune entrée ne provient d'une interview mécanicien : les interviews terrain (source 3b dans
  `ai/docs/sources.md`) n'ont pas encore été réalisées. Voir
  `ai/docs/GUIDE_INTERVIEW_TECHNIQUE.md` pour le format prévu de collecte future.
- Validé par `ai/scripts/validate_knowledge_base.py` (0 erreur, 0 avertissement au moment de la
  création).

## Historique

`kb_corpus_v0.csv` (première version, 18 entrées) a été retiré et déplacé dans
`_to_delete/` (à supprimer manuellement) à la demande explicite de recréer le corpus. Son contenu a
été entièrement réécrit dans `kb_corpus_v1.csv`, en gardant les mêmes sources autorisées et le même
schéma.
