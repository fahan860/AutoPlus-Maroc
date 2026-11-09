---
name: evaluer-agent-ia
description: Évaluer l'agent IA de diagnostic AUTO+ sur un jeu fixe de conversations en français et en darija, avec des métriques chiffrées, avant un changement de LLM (Groq → Mistral) ou pour le rapport PFA.
---
# Évaluer l'agent IA

## Jeu d'évaluation
- Fichier `ml/eval/agent_cases.jsonl` (à créer s'il n'existe pas), ~20 cas : 10 en français, 10 en darija (lettres latines).
- Chaque cas : `id`, `langue`, `messages` (1 à 3 tours utilisateur), `panne_attendue` (catégorie de `base_pannes`), `gravite_attendue`, `doit_refuser` (hors sujet), `notes`.
- Couvrir : freins, moteur, batterie/électricité, climatisation, pneus, embrayage, voyants OBD, 2 cas hors sujet, 2 cas dangereux (alerte de sécurité attendue).

## Mesures (par cas, puis moyenne)
1. Bonne catégorie de panne (oui/non).
2. Gravité au moins égale à l'attendue (oui/non).
3. Réponse ancrée sur les sources récupérées, sans cause inventée (oui/non, vérifié à la main sur un échantillon).
4. Nombre de questions de précision ≤ 2 (oui/non).
5. Refus correct des cas hors sujet, alerte présente sur les cas dangereux.
6. Latence (s) et coût estimé par conversation.
7. Darija : note de 1 à 3 donnée par un locuteur natif (laisser vide si non évalué, ne pas noter soi-même).

## Lancer
- Service démarré (`docker compose up -d`), appels à `POST /agent/chat` via un script `ml/eval/run_agent_eval.py`.
- Même jeu, même configuration pour chaque LLM comparé. Fixer la température.

## Rendre
- `ml/reports/agent_evaluation.json` + un tableau par LLM, les 3 pires cas avec leur explication, et la ligne pour le rapport PFA. Ne jamais annoncer un chiffre qui n'a pas été mesuré.
