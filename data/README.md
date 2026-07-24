# Data Lake — AUTO+

Stockage local des events applicatifs, en Parquet, partitionnés par date :

```
data/events/year=2026/month=07/day=07/*.parquet
```

## Pipeline d'ingestion

1. **Logging** : chaque action utilisateur (recherche garage, inscription, connexion,
   RDV, avis...) est loggée en JSON dans la liste Redis `events:queue` via
   `api/src/events.js` (`logEvent(type, payload, userId)`), appelé depuis les routes
   de `/api/src/routes`.
2. **Flush vers Parquet** : le script `data/pipeline/flush_events_to_parquet.py` vide
   la queue Redis, regroupe les events par date et écrit un fichier Parquet par
   partition dans `data/events/year=/month=/day=/`.

### Lancer le flush manuellement (dev)

```powershell
docker compose up -d          # redis doit tourner
cd ml
.\venv\Scripts\pip install -r requirements.txt   # ajoute pyarrow + redis
.\venv\Scripts\python ..\data\pipeline\flush_events_to_parquet.py
```

En prod, ce script est prévu pour tourner sur un cron (ex : toutes les 15 min).

Ce dossier n'est pas versionné dans Git (voir `.gitignore`) — seule la structure (`events/.gitkeep`) est conservée.
