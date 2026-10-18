# Base AUTO+ : PostgreSQL 16 + pgvector (RAG de l'agent IA, Modele B) + PostGIS (garages).
# On part de l'image officielle pgvector (Debian 12 bookworm, maintenue) et on y ajoute PostGIS
# depuis le depot PostgreSQL deja configure dans l'image. L'inverse (postgis/postgis:16-*,
# base Debian 11 bullseye, fin de support) ne permet plus d'installer pgvector avec apt.
# Meme version majeure (16) que l'ancienne image : le volume postgres-data existant est reutilise.
FROM pgvector/pgvector:pg16-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-16-postgis-3 postgresql-16-postgis-3-scripts \
    && rm -rf /var/lib/apt/lists/*
