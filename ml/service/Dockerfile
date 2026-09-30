# Service ML AUTO+ — contexte de build : le dossier ml/ (voir docker-compose.yml)
FROM python:3.10-slim

# libgomp : calcul parallèle d'XGBoost
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY service/requirements.txt service/requirements.txt
RUN pip install --no-cache-dir -r service/requirements.txt

# Même arborescence que dans le dépôt : predictor.py retrouve features.py et le modèle
COPY src/model_a/features.py src/model_a/features.py
COPY models/model_a models/model_a
COPY service service

WORKDIR /app/service
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
