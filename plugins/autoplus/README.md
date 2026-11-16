# Plugin Claude Code AUTO+ (`autoplus`)

Copilote business d'AUTO+ (marketplace garages ↔ automobilistes, pilote Casablanca, PFA ENSA Tétouan 2026).

## Contenu (v0.1.0)

| Type | Éléments |
|---|---|
| Sous-agents (10) | `startup-strategist`, `market-researcher`, `competitor-analyst`, `customer-researcher`, `business-strategist`, `pmm`, `growth-lead`, `garage-partnerships`, `gtm-strategist`, `pitch-coach` |
| Skills (9) | `autoplus-cso`, `validation-prix`, `design-experience`, `revue-pitch`, `revue-business-hebdo`, `autoplus-market-intel`, `autoplus-business-model`, `autoplus-gtm-growth`, `autoplus-brand-voice` |
| Commandes (3) | `/autoplus:cso <question>`, `/autoplus:semaine`, `/autoplus:verifier` |

Les sous-agents et skills techniques (`code-reviewer`, `ml-engineer`, `deploy-engineer`, `/livrer-tache`, `/nouvelle-migration`…) restent dans `.claude/` du dépôt : ils n'ont de sens que dans le code d'AUTO+.

## Installation

```bash
# depuis GitHub
claude plugin marketplace add fahan860/AutoPlus-Maroc
claude plugin install autoplus@autoplus-maroc

# ou depuis un clone local
claude plugin marketplace add ./AutoPlus-Maroc
claude plugin install autoplus@autoplus-maroc
```

Dans Claude Code : `/plugin` pour gérer, `/agents` pour voir les sous-agents (`autoplus:…`).

## Utilisation

- `/autoplus:cso Quel frais par RDV tester avec les garages pilotes ?` : orchestration complète (vagues parallèles, contre-vérification, contre-examen).
- `/autoplus:validation-prix`, `/autoplus:design-experience`, `/autoplus:revue-pitch` : procédures unitaires.
- `/autoplus:semaine` : point technique + revue business hebdomadaire.

## Limites connues

- **Skills : autonomes.** Chacun embarque ses documents de référence (`references/`, copies de `docs/business/` au 2026-11-16).
- **Sous-agents : prévus pour le dépôt.** Ils lisent d'abord `docs/business/*.md`. Hors du dépôt, passer par les skills (qui portent les références) ou ouvrir Claude Code dans le dépôt.
- **Dans le dépôt**, les mêmes agents et skills existent aussi sans préfixe (`.claude/`) : l'installation du plugin y est inutile.

## Maintenance

Le plugin est **généré** à partir de `.claude/` (source de vérité) : ne pas modifier `agents/` ni `skills/` ici.

```bash
python tools/sync_skill_references.py --write   # après un changement de docs/business/
python tools/build_plugin.py --write            # régénère le plugin
python tools/build_plugin.py --check            # contrôle (CI)
claude plugin validate plugins/autoplus         # validation officielle
```

Changer la version dans `.claude-plugin/plugin.json` et dans `.claude-plugin/marketplace.json` (racine du dépôt) à chaque publication.
