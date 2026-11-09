## Quoi et pourquoi

<!-- Une ou deux phrases : la tâche du cockpit concernée et le problème résolu. -->

## Changements

-

## Comment c'est testé

- [ ] Tests du service ML (`pytest`) : _résultat_
- [ ] API démarrée, route appelée en vrai : _route et réponse_
- [ ] Testé sur téléphone (Expo Go) : _écran_

## À vérifier avant de fusionner

- [ ] Aucun secret ni fichier `.env` dans le diff
- [ ] Changement de schéma = nouvelle migration numérotée et idempotente (aucune migration existante modifiée)
- [ ] Données personnelles chiffrées (`api/src/crypto.js`), jamais loggées
- [ ] Nouvelle action utilisateur = événement émis (`api/src/events.js`)
- [ ] Textes utilisateur en français et en darija
- [ ] Données réelles / simulées indiquées pour tout chiffre ML

## Migrations à appliquer

<!-- Liste des fichiers api/migrations/NNN_*.sql à appliquer par chaque membre, ou « aucune ». -->
