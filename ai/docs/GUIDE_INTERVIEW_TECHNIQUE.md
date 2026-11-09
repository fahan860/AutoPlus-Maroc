# Guide d'interview technique — Enrichissement Knowledge Base

**Objectif : différent du guide "customer discovery" existant.** Ici on ne cherche pas le parcours
client ou le prix payé, mais des **cas techniques concrets** exploitables directement dans le format
`KB_SCHEMA.md`, à mener avec des mécaniciens.

Durée estimée : 20-30 min, format libre autour de 4-5 pannes fréquentes que le mécanicien rencontre.

## Déroulé

1. **Introduction courte** : "Je construis une base de connaissances pour aider les automobilistes à
   comprendre un problème avant de venir au garage — pas pour remplacer un diagnostic, juste pour
   mieux orienter. Je vais vous demander de me décrire 4-5 pannes fréquentes que vous voyez souvent."

2. **Pour chaque panne évoquée, poser ces questions dans l'ordre** (remplir directement une ligne du
   corpus au format `kb_corpus_v0.csv`) :

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
   la provenance dans `sources.md`.

## Bonnes pratiques

- Privilégier des mécaniciens généralistes (pas hyper-spécialisés) pour couvrir un maximum de
  catégories en peu d'interviews.
- 3-4 mécaniciens suffisent pour un premier enrichissement notable (15-20 cas de plus).
- Combiner avec les visites déjà prévues au planning (Semaine 3, garages Sidi Maarouf) plutôt que
  d'organiser des visites dédiées supplémentaires.
