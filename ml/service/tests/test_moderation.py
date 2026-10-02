"""
Tests du Modèle C (détection de faux avis) dans le service ML.
Créent de vrais avis de test en base (préfixe TEST_MODERATION), puis les suppriment.
Nécessitent la base PostgreSQL avec la migration 008.
Lancement : cd ml/service && ../venv/Scripts/python -m pytest tests -q
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import psycopg2
import pytest
from dotenv import dotenv_values
from fastapi.testclient import TestClient

SERVICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_DIR))
PREFIXE = "TEST_MODERATION"


@pytest.fixture(scope="module")
def url_base():
    url = os.environ.get("DATABASE_URL") or dotenv_values(SERVICE_DIR.parents[1] / "api" / ".env").get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL introuvable : base nécessaire pour le Modèle C")
    return url


@pytest.fixture(scope="module")
def base(url_base):
    conn = psycopg2.connect(url_base)
    conn.autocommit = True
    yield conn
    with conn.cursor() as cur:  # nettoyage, dans l'ordre des clés étrangères
        cur.execute(f"DELETE FROM reviews WHERE user_id IN (SELECT id FROM users WHERE nom LIKE '{PREFIXE}%')")
        cur.execute(f"DELETE FROM interventions WHERE user_id IN (SELECT id FROM users WHERE nom LIKE '{PREFIXE}%')")
        cur.execute(f"DELETE FROM vehicles WHERE user_id IN (SELECT id FROM users WHERE nom LIKE '{PREFIXE}%')")
        cur.execute(f"DELETE FROM users WHERE nom LIKE '{PREFIXE}%'")
    conn.close()


@pytest.fixture(scope="module")
def client(url_base, base):
    os.environ["DATABASE_URL"] = url_base
    from app import app

    with TestClient(app) as c:
        if not c.get("/health").json()["modeles"].get("review_moderation"):
            pytest.skip("Modèle C non chargé")
        yield c
    os.environ.pop("DATABASE_URL", None)


def creer_avis(base, *, age_compte, note, commentaire, statut_rdv=None, garage_id=1):
    maintenant = datetime.now(timezone.utc)
    with base.cursor() as cur:
        cur.execute(
            "INSERT INTO users (nom, telephone, role, created_at) VALUES (%s, %s, 'automobiliste', %s) RETURNING id",
            (f"{PREFIXE} {commentaire[:20]}", f"test-{maintenant.timestamp()}", maintenant - age_compte),
        )
        user_id = cur.fetchone()[0]
        intervention_id = None
        if statut_rdv:
            cur.execute("INSERT INTO vehicles (user_id, plaque) VALUES (%s, %s) RETURNING id",
                        (user_id, f"TEST-{user_id}"))
            cur.execute("INSERT INTO interventions (vehicle_id, garage_id, user_id, statut) VALUES (%s, %s, %s, %s) RETURNING id",
                        (cur.fetchone()[0], garage_id, user_id, statut_rdv))
            intervention_id = cur.fetchone()[0]
        cur.execute("INSERT INTO reviews (garage_id, user_id, intervention_id, note, commentaire) "
                    "VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (garage_id, user_id, intervention_id, note, commentaire))
        return cur.fetchone()[0]


def moderer(client, review_id):
    reponse = client.post("/moderation/review", json={"review_id": review_id})
    assert reponse.status_code == 200, reponse.text
    return reponse.json()


def test_vrai_client_publie(client, base):
    rid = creer_avis(base, age_compte=timedelta(days=200), note=4, statut_rdv="termine",
                     commentaire="Plaquettes de frein changées sur ma Logan en une demi-journée, 600 DH comme le devis.")
    r = moderer(client, rid)
    assert r["decision"] == "publier"
    assert r["raisons"] == []


def test_auto_promotion_a_verifier(client, base):
    rid = creer_avis(base, age_compte=timedelta(hours=3), note=5,
                     commentaire="Le meilleur garage de Casablanca !!! Parfait, allez-y les yeux fermés !!!")
    r = moderer(client, rid)
    assert r["decision"] == "verifier"
    assert "Compte créé il y a moins de 24 h" in r["raisons"]
    assert any("superlatifs" in raison for raison in r["raisons"])


def test_denigrement_a_verifier(client, base):
    rid = creer_avis(base, age_compte=timedelta(hours=10), note=1, commentaire="Arnaque totale, des voleurs, fuyez !!!")
    assert moderer(client, rid)["decision"] == "verifier"


def test_avis_sur_rdv_annule(client, base):
    rid = creer_avis(base, age_compte=timedelta(days=300), note=4, statut_rdv="annule",
                     commentaire="Bon accueil, devis clair pour la vidange de ma Clio, 450 DH.")
    r = moderer(client, rid)
    assert r["decision"] == "verifier"
    assert "Avis sur un RDV annulé" in r["raisons"]


def test_avis_introuvable(client):
    assert client.post("/moderation/review", json={"review_id": 999_999_999}).status_code == 404
