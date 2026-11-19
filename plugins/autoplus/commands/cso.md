---
description: Poser une question business AUTO+ au CSO (sous-agents en parallèle, contre-vérification croisée, contre-examen, décision proposée)
argument-hint: <question business, ex. « quel frais par RDV tester avec les garages pilotes ? »>
---
Applique le skill `autoplus-cso` à la question suivante, dans cette session (tu es le CSO, pas un sous-agent) :

$ARGUMENTS

Déroulé obligatoire :
1. Montre d'abord le plan d'exécution (sous-questions, sous-agent, dépendances, vague) et la liste des affirmations qui seront contre-vérifiées.
2. Lance chaque vague en parallèle (un appel Agent par sous-question indépendante), avec le brief type du skill.
3. Fais vérifier les affirmations importantes par le vérificateur de la matrice, jamais par leur producteur.
4. Fais contre-examiner ta recommandation par un contradicteur qui n'a produit aucune affirmation importante.
5. Rends le tableau de confrontation, la recommandation (« proposée »), les réponses aux objections, la ligne de journal et ce qui reste à valider.

Si la question est vide, demande-la en une phrase. Si l'outil Agent n'est pas disponible, exécute les rôles un par un et indique « exécution séquentielle, même modèle ».
