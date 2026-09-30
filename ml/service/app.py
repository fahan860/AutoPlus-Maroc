"""
Service ML AUTO+ (FastAPI) — interne : appelé par l'API Node, jamais directement par l'app.

Routes :
  GET  /health                          état du service et version du modèle
  POST /predict/vehicle-value           Modèle A : estimation du prix d'un véhicule d'occasion
  GET  /predict/vehicle-value/options   marques, modèles et villes connus du modèle (listes de l'app)

Documentation interactive : http://localhost:8000/docs
Lancement local : cd ml/service && ../venv/Scripts/uvicorn app:app --reload --port 8000
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from predictor import PredicteurPrix
from schemas import DemandeEstimation, Estimation, Options

modeles = {}


@asynccontextmanager
async def cycle_de_vie(_app: FastAPI):
    # Chargé une seule fois au démarrage (~1 s), puis gardé en mémoire pour toutes les requêtes
    try:
        modeles["prix"] = PredicteurPrix()
    except FileNotFoundError as err:
        print(f"Modèle A non chargé ({err}) — lancer ml/src/model_a/tune.py")
    yield
    modeles.clear()


app = FastAPI(
    title="AUTO+ — Service ML",
    description="Modèles de machine learning d'AUTO+ (usage interne, derrière l'API Node).",
    version="1.0.0",
    lifespan=cycle_de_vie,
)


def predicteur_prix() -> PredicteurPrix:
    if "prix" not in modeles:
        raise HTTPException(status_code=503, detail="Modèle d'estimation de prix non disponible")
    return modeles["prix"]


@app.get("/health")
def health():
    prix = modeles.get("prix")
    return {
        "status": "ok" if prix else "degrade",
        "modeles": {"vehicle_value": prix.version if prix else None},
    }


@app.post("/predict/vehicle-value", response_model=Estimation)
def estimer_prix(demande: DemandeEstimation) -> Estimation:
    return predicteur_prix().estimer(demande)


@app.get("/predict/vehicle-value/options", response_model=Options)
def options_prix() -> Options:
    return predicteur_prix().options()
