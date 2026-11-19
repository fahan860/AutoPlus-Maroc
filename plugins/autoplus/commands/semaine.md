---
description: Bilan de la semaine AUTO+ — point technique (si disponible) puis revue business hebdomadaire et lignes pour le journal du cockpit
argument-hint: "[semaine, ex. S21 — par défaut la semaine en cours]"
---
Fais le bilan de la semaine AUTO+ ($ARGUMENTS, par défaut la semaine en cours) :

1. **Technique** : si le skill `point-hebdo` est disponible (dépôt AUTO+ ouvert), applique-le. Sinon, écris « point technique non fait : dépôt non disponible » et passe à l'étape 2.
2. **Business** : applique le skill `revue-business-hebdo`. Les chiffres viennent uniquement de sources citées (requêtes du sous-agent `marketing-analyst` quand il est disponible, synthèses anonymisées, `docs/business/10`). Toute donnée absente est écrite « non mesuré » ou `[À COMPLÉTER]`.
3. Termine par les lignes du journal du cockpit (`AAAA-MM-JJ · Type · Texte`) et les 3 priorités de la semaine suivante, chacune avec un résultat vérifiable.
