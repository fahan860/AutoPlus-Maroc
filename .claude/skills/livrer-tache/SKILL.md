---
name: livrer-tache
description: Mener une tâche AUTO+ de bout en bout selon la règle « une tâche = une branche = une PR » — plan, branche, code, tests, relecture, commit, Pull Request. À utiliser quand on démarre une tâche du cockpit ou de la liste des priorités.
---
# Livrer une tâche

## 1. Cadrer
- Reformule la tâche en une phrase et le résultat attendu vérifiable (« l'API répond 200 sur /health en ligne », « 37 tests passent »).
- Tâche non triviale : propose un plan court (fichiers touchés, migrations, tests) et attends l'accord avant de coder.

## 2. Brancher
- Pars de `main` à jour : `git checkout main; git pull --ff-only; git checkout -b <type>/<sujet>`.
- Types : `feature/`, `fix/`, `chore/`, `docs/`, `ml/`. Sujet en kebab-case, ex. `feature/funnel-events`.

## 3. Faire
- Respecte `CLAUDE.md` (migrations, chiffrement, événements, `.env` jamais lu).
- Schéma modifié : utilise le skill `nouvelle-migration`.
- Action utilisateur nouvelle : émets un événement via `api/src/events.js`.
- Texte visible par l'utilisateur : skill `autoplus-brand-voice`, français + darija.

## 4. Vérifier
- Service ML touché : `cd ml/service; ..\venv\Scripts\python -m pytest tests -q`.
- API touchée : `docker compose up -d --build api` puis `docker compose logs api` sans erreur, et un appel réel à la route.
- Lance le sous-agent `code-reviewer` et corrige les points « Bloquant ».

## 5. Livrer
- Commits petits, au présent, préfixés (`feat:`, `fix:`, `docs:`, `chore:`, `ml:`), en français.
- `git push -u origin <branche>` puis ouvre la PR avec le modèle `.github/pull_request_template.md` (avec `gh pr create` si disponible).
- Donne à l'utilisatrice : le lien de la PR, ce qui a été testé, et la ligne à ajouter au journal du cockpit AUTO+.
