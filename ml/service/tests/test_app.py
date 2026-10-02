"""
Tests du service ML. Nécessitent le modèle entraîné (ml/models/model_a/).
Lancement : cd ml/service && ../venv/Scripts/python -m pytest tests -q
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import app  # noqa: E402

LOGAN = {
    "marque": "dacia", "modele": "logan", "annee": 2019, "kilometrage": 90000,
    "boite": "manuelle", "carburant": "diesel", "puissance_fiscale": 6,
    "etat": "tres_bon", "origine": "ww_maroc", "premiere_main": True, "ville": "Casablanca",
    "equipements": ["climatisation", "abs", "bluetooth"],
}


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # le "with" déclenche le chargement du modèle au démarrage
        yield c


def estimer(client, **modifs):
    reponse = client.post("/predict/vehicle-value", json={**LOGAN, **modifs})
    assert reponse.status_code == 200, reponse.text
    return reponse.json()


def test_health(client):
    # Le statut global dépend aussi du Modèle B (base de données) : on vérifie le Modèle A seul
    corps = client.get("/health").json()
    assert corps["modeles"]["vehicle_value"]


def test_prix_plausible_et_fourchette(client):
    r = estimer(client)
    # Logan diesel 2019, ~90 000 km : entre 60 000 et 160 000 DH sur le marché marocain
    assert 60_000 <= r["prix_estime"] <= 160_000
    assert r["fourchette"]["min"] <= r["prix_estime"] <= r["fourchette"]["max"]
    assert r["fiabilite"] == "normale"
    assert r["avertissements"] == []


def test_voiture_recente_vaut_plus(client):
    assert estimer(client, annee=2023, kilometrage=30000)["prix_estime"] > estimer(client, annee=2012, kilometrage=200000)["prix_estime"]


def test_kilometrage_eleve_vaut_moins(client):
    assert estimer(client, kilometrage=40000)["prix_estime"] > estimer(client, kilometrage=300000)["prix_estime"]


def test_gamme_superieure_vaut_plus(client):
    classe_c = estimer(client, marque="mercedes-benz", modele="classe c", boite="automatique", puissance_fiscale=8)
    assert classe_c["prix_estime"] > estimer(client)["prix_estime"]


def test_saisie_tolerante(client):
    """Majuscules, accents et espaces en trop donnent la même estimation."""
    normal = estimer(client, ville="Fès")["prix_estime"]
    assert estimer(client, marque="  DACIA ", modele="Logan", ville="fes")["prix_estime"] == normal


def test_modele_inconnu_fiabilite_reduite(client):
    r = estimer(client, modele="modele-qui-nexiste-pas")
    assert r["fiabilite"] == "reduite"
    assert any("Modèle peu présent" in a for a in r["avertissements"])


def test_champs_optionnels(client):
    minimal = {k: LOGAN[k] for k in ("marque", "modele", "annee", "boite", "carburant")}
    reponse = client.post("/predict/vehicle-value", json=minimal)
    assert reponse.status_code == 200
    assert any("Kilométrage" in a for a in reponse.json()["avertissements"])


@pytest.mark.parametrize("modifs", [
    {"annee": 3024},
    {"annee": 1950},
    {"kilometrage": -5},
    {"carburant": "charbon"},
    {"equipements": ["fusee"]},
    {"marque": ""},
])
def test_donnees_invalides_refusees(client, modifs):
    assert client.post("/predict/vehicle-value", json={**LOGAN, **modifs}).status_code == 422


def test_options(client):
    options = client.get("/predict/vehicle-value/options").json()
    assert "dacia" in options["marques"]
    assert "logan" in options["modeles_par_marque"]["dacia"]
    assert "Casablanca" in options["villes"]
