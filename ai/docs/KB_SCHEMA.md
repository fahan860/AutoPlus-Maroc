# Schéma de la Knowledge Base — Agent IA AUTO+

**Phase 1 du plan de développement.**

## Catégories

Reprises du plan, adaptées au parc automobile marocain (Dacia, Renault, Peugeot, Volkswagen, Hyundai,
Fiat très représentés — utile pour prioriser la collecte en Phase 2) :

| Code catégorie | Libellé | Exemples de symptômes couverts |
|---|---|---|
| `obd_dtc` | OBD / DTC | Codes P0xxx, description standardisée, causes associées |
| `moteur` | Moteur | Calage, ratés d'allumage, perte de puissance, voyant moteur |
| `transmission` | Transmission | Boîte auto/manuelle, à-coups, difficulté à passer les vitesses |
| `freins` | Freins | Bruit au freinage, pédale molle, distance de freinage anormale |
| `electrique` | Électrique | Batterie, alternateur, démarreur, voyants tableau de bord |
| `refroidissement` | Refroidissement | Surchauffe, fuite liquide, ventilateur |
| `carburant` | Carburant | Consommation anormale, injection, panne sèche récurrente |
| `demarrage` | Démarrage | Ne démarre pas, démarre difficilement, cale au démarrage |
| `surchauffe` | Surchauffe | Cas transversal moteur/refroidissement — regroupé par fréquence |
| `perte_puissance` | Perte de puissance | Accélération faible, à-coups en charge |
| `bruit_vibration` | Bruit / vibration | Bruits suspects, vibrations volant/pédale/carrosserie |
| `maintenance` | Maintenance | Entretien préventif, vidange, révisions, usure normale |

*Une entrée peut appartenir à plusieurs catégories (ex. un code DTC lié à la surchauffe) — prévoir un
champ multi-valué plutôt qu'une catégorie unique stricte.*

## Champs principaux (par entrée / document de la KB)

| Champ | Type | Description | Obligatoire |
|---|---|---|---|
| `id` | UUID | Identifiant unique de l'entrée | ✅ |
| `symptome` | text | Description du symptôme en langage utilisateur (ex. "voiture cale au ralenti") | ✅ |
| `vehicule` | text / structuré | Marque, modèle, plage d'années concernées (`*` si générique) | ✅ |
| `systeme` | enum | Une ou plusieurs catégories ci-dessus | ✅ |
| `cause` | text | Cause probable associée au symptôme | ✅ |
| `explication` | text | Explication technique compréhensible (niveau utilisateur, pas jargon pur atelier) | ✅ |
| `verification` | text | Vérification(s) recommandée(s) avant d'aller au garage | ✅ |
| `gravite` | enum (`faible`, `moyenne`, `elevee`, `critique`) | Urgence / risque associé | ✅ |
| `source` | text (clé vers `sources.md`) | D'où vient l'information | ✅ |
| `langue` | enum (`fr`, `ar`, `darija`) | Langue du contenu original | ✅ |
| `date_maj` | date | Dernière mise à jour de l'entrée | ✅ |
| `dtc_code` | text (nullable) | Code DTC associé si applicable (ex. `P0301`) | optionnel |
| `page_source` | text/int (nullable) | Page ou section dans le document source | optionnel |
| `tags` | text[] | Mots-clés libres pour affiner le retrieval par filtre métadonnées | optionnel |

## Ce que ça donnera en base (aperçu — détail complet en Phase 4)

Chaque entrée de la KB devient, après chunking (Phase 3) et embedding (Phase 5) :

- **1 ligne `documents`** : métadonnées ci-dessus (source, catégorie, véhicule, langue, gravité...).
- **N lignes `chunks`** : fragments de texte issus de `explication` + `verification` (taille adaptée au
  RAG, ex. 200-400 tokens).
- **N vecteurs `embeddings`** liés aux chunks, indexés avec pgvector, filtrables par les métadonnées
  ci-dessus (`systeme`, `vehicule`, `langue`, `gravite`) pour combiner recherche vectorielle et filtres
  structurés (cf. Phase 6).

## Recommandation

Démarrer avec un schéma volontairement simple (les champs ci-dessus, pas plus) et un format de saisie
unique (ex. un fichier YAML ou CSV par catégorie) pour permettre de remplir rapidement un premier
corpus test (Phase 2-3) sans construire d'outillage complexe avant d'avoir validé que le pipeline
ingestion → retrieval fonctionne.
