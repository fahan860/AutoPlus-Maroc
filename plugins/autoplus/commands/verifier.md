---
description: Vérifier la cohérence des agents, skills et du plugin AUTO+ (à lancer dans le dépôt avant une PR)
allowed-tools: Bash(python tools/sync_skill_references.py --check), Bash(python tools/check_orchestration.py), Bash(python tools/build_plugin.py --check), Bash(python3 tools/sync_skill_references.py --check), Bash(python3 tools/check_orchestration.py), Bash(python3 tools/build_plugin.py --check)
---
Dans le dépôt AUTO+ (dossier contenant `tools/`), lance ces trois contrôles et rends leur sortie telle quelle :

1. `python tools/sync_skill_references.py --check` : copies `references/` et procédures identiques à `docs/business/`, une seule brand-voice.
2. `python tools/check_orchestration.py` : routage CSO, matrice de vérification (producteur ≠ vérificateur), aucun sous-agent capable d'en lancer d'autres.
3. `python tools/build_plugin.py --check` : le plugin `plugins/autoplus/` est identique à `.claude/`.

Si `tools/` est absent, réponds que cette commande ne fonctionne que dans le dépôt AUTO+. Si un contrôle échoue, liste les erreurs et la commande de correction (`--write` pour les deux scripts de synchronisation). Ne modifie aucun fichier sans accord.
