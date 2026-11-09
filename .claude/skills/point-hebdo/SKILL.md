---
name: point-hebdo
description: Faire le point hebdomadaire du projet AUTO+ — ce qui a été livré, ce qui bloque, les priorités de la semaine suivante — à partir de git, des PR et du rapport d'avancement. À utiliser chaque lundi ou avant un rendez-vous avec l'encadrant.
---
# Point hebdomadaire

Semaine du planning : S = nombre de semaines écoulées depuis le 30 juin 2026, + 1 (26 semaines au total).

1. Collecte (sans rien inventer) :
   - `git log --since="7 days ago" --all --format="%h %ad %an %s" --date=short`
   - branches non fusionnées : `git branch -a --no-merged main`
   - PR ouvertes et fusionnées de la semaine : `gh pr list --state all --limit 20` si `gh` est disponible.
   - fichiers modifiés non commités : `git status --short`.
2. Compare avec les « Priorités restantes » de `CLAUDE.md` et la section 4 de `RAPPORT_AVANCEMENT.md`.
3. Rends, en français :
   - **Livré cette semaine** (avec PR ou commit)
   - **En cours** et ce qui reste pour finir
   - **Bloqué** : cause et qui peut débloquer
   - **Priorités de la semaine prochaine** : 3 au maximum, chacune avec un résultat vérifiable
   - **Risques** qui ont changé
   - **Entrées pour le journal du cockpit** : une ligne par fait marquant, au format `AAAA-MM-JJ · Type · Texte`
4. Si l'utilisatrice le demande, mets à jour `RAPPORT_AVANCEMENT.md` (période couverte, sections 2 à 6) dans une branche `docs/point-sNN`.
