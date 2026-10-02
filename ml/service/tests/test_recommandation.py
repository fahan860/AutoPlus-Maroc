"""
Tests du Modèle B (recommandation de garages) dans le service ML.
Nécessitent la base PostgreSQL (docker compose up -d db) et le modèle e5-large.
Lancement : cd ml/service && ../venv/Scripts/python -m pytest tests -q
"""

import os
import sys
from pathlib import Path

import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient

SERVICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_DIR))

MAARIF = {"lat": 33.5822, "lon": -7.6327}


@pytest.fixture(scope="module")
def client():
    url = os.environ.get("DATABASE_URL") or dotenv_values(SERVICE_DIR.parents[1] / "api" / ".env").get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL introuvable : base nécessaire pour le Modèle B")
    os.environ["DATABASE_URL"] = url
    from app import app

    with TestClient(app) as c:
        if "garage_recommendation" not in str(c.get("/health").json()) or \
                not c.get("/health").json()["modeles"]["garage_recommendation"]:
            pytest.skip("Modèle B non chargé (base ou modèle e5 indisponible)")
        yield c
    os.environ.pop("DATABASE_URL", None)


def recommander(client, description, **extra):
    reponse = client.post("/recommend/garages", json={"description": description, **MAARIF, **extra})
    assert reponse.status_code == 200, reponse.text
    return reponse.json()


def test_panne_de_freins(client):
    r = recommander(client, "ça grince fort quand je freine")
    assert r["categories_probables"][0]["categorie"] == "freins"
    assert r["pannes_proches"][0]["categorie"] == "freins"
    assert len(r["garages"]) == 5
    for g in r["garages"]:
        assert "freins" in g["specialites"]
        assert g["raisons"]


def test_carrosserie_oriente_vers_un_carrossier(client):
    r = recommander(client, "ma portière est enfoncée après un accrochage")
    assert r["categories_probables"][0]["categorie"] == "carrosserie"
    assert all("carrosserie" in g["specialites"] for g in r["garages"])
    assert r["garages"][0]["specialites_confirmees"]


def test_garages_tries_par_score_et_proches(client):
    r = recommander(client, "je dois faire la vidange")
    scores = [g["score"] for g in r["garages"]]
    assert scores == sorted(scores, reverse=True)
    assert r["garages"][0]["distance_km"] < 5


def test_sans_position(client):
    r = client.post("/recommend/garages", json={"description": "la clim ne refroidit plus"}).json()
    assert r["garages"]
    assert any("Position inconnue" in a for a in r["avertissements"])


def test_nombre_de_garages(client):
    assert len(recommander(client, "voyant moteur allumé", nb_garages=3)["garages"]) == 3


@pytest.mark.parametrize("corps", [
    {"description": "ok"},
    {"description": "x" * 501},
    {"description": "frein", "lat": 200},
    {"description": "frein", "nb_garages": 0},
])
def test_donnees_invalides_refusees(client, corps):
    assert client.post("/recommend/garages", json=corps).status_code == 422
