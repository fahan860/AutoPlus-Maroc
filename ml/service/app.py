"""
Service ML AUTO+ (FastAPI) — interne : appelé par l'API Node, jamais directement par l'app.

Routes :
  GET  /health                          état du service et version du modèle
  POST /predict/vehicle-value           Modèle A : estimation du prix d'un véhicule d'occasion
  GET  /predict/vehicle-value/options   marques, modèles et villes connus du modèle (listes de l'app)
  POST /recommend/garages               Modèle B : garages adaptés à une panne décrite en texte libre

Documentation interactive : http://localhost:8000/docs
Lancement local : cd ml/service && ../venv/Scripts/uvicorn app:app --reload --port 8000
  (le Modèle B a besoin de DATABASE_URL : pannes et garages sont lus dans PostgreSQL)
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from predictor import PredicteurPrix
from schemas import DemandeEstimation, DemandeRecommandation, Estimation, Options, Recommandation

modeles = {}


@asynccontextmanager
async def cycle_de_vie(_app: FastAPI):
    # Chargés une seule fois au démarrage, puis gardés en mémoire pour toutes les requêtes
    try:
        modeles["prix"] = PredicteurPrix()
    except FileNotFoundError as err:
        print(f"Modèle A non chargé ({err}) — lancer ml/src/model_a/tune.py")

    url_base = os.environ.get("DATABASE_URL")
    if url_base:
        try:
            from recommandation import ServiceRecommandation  # import local : charge PyTorch (~10 s)

            modeles["garages"] = ServiceRecommandation(url_base)
        except Exception as err:  # base ou modèle e5 indisponible : le Modèle A reste servi
            print(f"Modèle B non chargé : {err}")
    else:
        print("Modèle B non chargé : DATABASE_URL absente")
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


def service_garages():
    if "garages" not in modeles:
        raise HTTPException(status_code=503, detail="Modèle de recommandation de garages non disponible")
    return modeles["garages"]


@app.get("/health")
def health():
    prix, garages = modeles.get("prix"), modeles.get("garages")
    return {
        "status": "ok" if prix and garages else "degrade",
        "modeles": {
            "vehicle_value": prix.version if prix else None,
            "garage_recommendation": garages.version if garages else None,
        },
    }


@app.post("/predict/vehicle-value", response_model=Estimation)
def estimer_prix(demande: DemandeEstimation) -> Estimation:
    return predicteur_prix().estimer(demande)


@app.get("/predict/vehicle-value/options", response_model=Options)
def options_prix() -> Options:
    return predicteur_prix().options()


@app.post("/recommend/garages", response_model=Recommandation)
def recommander_garages(demande: DemandeRecommandation) -> Recommandation:
    return service_garages().recommander(demande)
