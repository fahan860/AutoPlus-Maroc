"""
Service ML AUTO+ (FastAPI) — interne : appelé par l'API Node, jamais directement par l'app.

Routes :
  GET  /health                          état du service et version du modèle
  POST /predict/vehicle-value           Modèle A : estimation du prix d'un véhicule d'occasion
  GET  /predict/vehicle-value/options   marques, modèles et villes connus du modèle (listes de l'app)
  POST /recommend/garages               Modèle B : garages adaptés à une panne décrite en texte libre
  POST /moderation/review               Modèle C : un avis qui vient d'être publié est-il suspect ?
  POST /agent/chat                      Agent IA de diagnostic : un tour de conversation (RAG + LLM)

Documentation interactive : http://localhost:8000/docs
Lancement local : cd ml/service && ../venv/Scripts/uvicorn app:app --reload --port 8000
  (le Modèle B a besoin de DATABASE_URL : pannes et garages sont lus dans PostgreSQL)
"""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import truststore

# Magasin de certificats du système pour les appels HTTPS sortants (LLM) : indispensable sur un
# poste dont l'antivirus intercepte le TLS (Avast), sans effet ailleurs
truststore.inject_into_ssl()
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src" / "agent"))

from fastapi import FastAPI, HTTPException

from predictor import PredicteurPrix
from schemas import (
    DecisionModeration, DemandeAgent, DemandeEstimation, DemandeModeration, DemandeRecommandation, Estimation,
    Options, Recommandation, ReponseAgent,
)

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
        if "garages" in modeles:
            try:
                from agent import AgentDiagnostic  # partage e5-large et les garages du Modèle B

                modeles["agent"] = AgentDiagnostic(url_base, modeles["garages"])
            except Exception as err:  # clé du LLM absente : le reste du service fonctionne
                print(f"Agent IA non chargé : {err}")
        try:
            from moderation import ServiceModeration

            modeles["avis"] = ServiceModeration(url_base)
        except Exception as err:
            print(f"Modèle C non chargé : {err}")
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
    prix, garages, avis, agent = (modeles.get(k) for k in ("prix", "garages", "avis", "agent"))
    return {
        "status": "ok" if prix and garages and avis and agent else "degrade",
        "modeles": {
            "vehicle_value": prix.version if prix else None,
            "garage_recommendation": garages.version if garages else None,
            "review_moderation": avis.version if avis else None,
            "diagnostic_agent": agent.version if agent else None,
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


@app.post("/moderation/review", response_model=DecisionModeration)
def moderer_avis(demande: DemandeModeration) -> DecisionModeration:
    if "avis" not in modeles:
        raise HTTPException(status_code=503, detail="Modèle de détection de faux avis non disponible")
    try:
        return modeles["avis"].evaluer(demande.review_id)
    except LookupError as err:
        raise HTTPException(status_code=404, detail=str(err)) from err


@app.post("/agent/chat", response_model=ReponseAgent)
def agent_chat(demande: DemandeAgent) -> ReponseAgent:
    if "agent" not in modeles:
        raise HTTPException(status_code=503, detail="Agent IA non disponible")
    vehicule = demande.vehicule.model_dump(exclude_none=True) if demande.vehicule else None
    try:
        sortie = modeles["agent"].repondre([m.model_dump() for m in demande.messages], vehicule, demande.lat, demande.lon)
    except Exception as err:  # LLM indisponible, quota dépassé, réponse illisible
        print(f"Agent IA : échec du tour de conversation : {err}")
        raise HTTPException(status_code=503, detail="L'assistant est momentanément indisponible") from err
    probas = sortie.pop("_probas")
    sortie.pop("categorie", None)
    garages = modeles["garages"].garages_pour(probas, demande.lat, demande.lon, k=3) if sortie["action"] == "diagnostic" else []
    return ReponseAgent(**sortie, garages=garages)
