# Data Lake — AUTO+

Stockage local des events applicatifs, en Parquet, partitionnés par date :

```
data/events/year=2026/month=07/day=07/*.parquet
```

Chaque action utilisateur (recherche, RDV, avis, etc.) est loggée en JSON dans Redis
puis vidée périodiquement vers ce dossier au format Parquet (voir pipeline d'ingestion dans `/api`).

Ce dossier n'est pas versionné dans Git (voir `.gitignore`) — seule la structure (`events/.gitkeep`) est conservée.
