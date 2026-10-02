# Service ML AUTO+ — contexte de build : le dossier ml/ (voir docker-compose.yml)
FROM python:3.10-slim

# libgomp : calcul parallèle d'XGBoost
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# PyTorch CPU d'abord (index dédié, version "+cpu" épinglée) : sinon pip installe la version
# CUDA, ~2 Go inutiles. PyPI reste accessible pour les dépendances de torch.
RUN pip install --no-cache-dir "torch==2.13.0+cpu" \
    --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple
COPY service/requirements.txt service/requirements.txt
RUN pip install --no-cache-dir -r service/requirements.txt

# Même arborescence que dans le dépôt : predictor.py retrouve features.py et le modèle,
# recommandation.py retrouve recommandeur.py
COPY src/model_a/features.py src/model_a/features.py
COPY src/model_b/recommandeur.py src/model_b/recommandeur.py
COPY src/model_c/signaux.py src/model_c/signaux.py
COPY models/model_a models/model_a
COPY models/model_c models/model_c
COPY service service

WORKDIR /app/service
RUN useradd --create-home appuser
USER appuser
# Modèle e5-large (~2,2 Go) : téléchargé au 1er démarrage dans le volume hf-cache, puis réutilisé
ENV HF_HOME=/home/appuser/.cache/huggingface

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
