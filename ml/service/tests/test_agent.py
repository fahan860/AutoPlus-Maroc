"""
Tests de l'agent IA : garde-fous appliqués à la réponse du LLM.

Le LLM est simulé (réponses JSON fixées) : ces tests vérifient ce que l'agent fait de la
réponse, quel que soit le LLM — sources inventées retirées, gravité jamais sous celle des
sources, nombre de questions limité, alerte de sécurité. La qualité des réponses réelles de
Mistral est mesurée à part (ml/src/agent/evaluate_agent.py).
Nécessitent la base PostgreSQL et le modèle e5-large.
"""

import json
import os
import sys
from pathlib import Path

import pytest
from dotenv import dotenv_values

SERVICE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICE_DIR))
sys.path.insert(0, str(SERVICE_DIR.parent / "src" / "agent"))


@pytest.fixture(scope="module")
def service_garages():
    url = os.environ.get("DATABASE_URL") or dotenv_values(SERVICE_DIR.parents[1] / "api" / ".env").get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL introuvable")
    from recommandation import ServiceRecommandation

    return ServiceRecommandation(url), url


def agent_avec(service_garages, reponse_llm: dict):
    """Agent dont le LLM renvoie toujours `reponse_llm` ; garde les messages reçus (le dernier appel
    est la réponse, le premier la reformulation, ici sans description : recherche sur le texte brut)."""
    from agent import AgentDiagnostic

    service, url = service_garages
    recus = []

    def faux_llm(messages):
        recus.append(messages)
        return json.dumps(reponse_llm)

    return AgentDiagnostic(url, service, appel_llm=faux_llm), recus


FREINS = [{"role": "user", "content": "ça grince fort quand je freine depuis hier"}]


def test_source_inventee_retiree(service_garages):
    agent, _ = agent_avec(service_garages, {
        "action": "diagnostic", "langue": "fr", "message": "Plusieurs pistes possibles.",
        "causes": [{"titre": "Plaquettes usées", "explication": "...", "source": "FRE-01"},
                   {"titre": "Cause inventée", "explication": "...", "source": "SOURCE-QUI-NEXISTE-PAS"}],
        "verifications": ["Écouter si le bruit change"], "gravite": "moyenne", "consulter_garage": True})
    r = agent.repondre(FREINS)
    assert [c["source"] for c in r["causes"]] == ["FRE-01"]
    assert r["sources"][0]["id"] == "FRE-01"


def test_gravite_jamais_sous_celle_des_sources(service_garages):
    # FRE-01 a une urgence « elevee » dans base_pannes : le LLM ne peut pas la minimiser
    agent, _ = agent_avec(service_garages, {
        "action": "diagnostic", "langue": "fr", "message": "Rien de grave.",
        "causes": [{"titre": "Plaquettes", "explication": "...", "source": "FRE-01"}],
        "verifications": [], "gravite": "faible", "consulter_garage": False})
    r = agent.repondre(FREINS)
    assert r["gravite"] == "elevee"
    assert r["consulter_garage"]


def test_question_avec_suggestions(service_garages):
    agent, _ = agent_avec(service_garages, {
        "action": "question", "langue": "fr", "message": "Le bruit arrive-t-il seulement au freinage ?",
        "suggestions": ["Oui, au freinage", "Tout le temps", "Je ne sais pas"]})
    r = agent.repondre([{"role": "user", "content": "ma voiture fait un bruit"}])
    assert r["action"] == "question"
    assert len(r["suggestions"]) == 3
    assert r["causes"] == [] and r["gravite"] is None


def test_au_plus_deux_questions(service_garages):
    agent, recus = agent_avec(service_garages, {
        "action": "question", "langue": "fr", "message": "Encore une question ?", "suggestions": ["Oui"]})
    historique = [
        {"role": "user", "content": "ma voiture fait un bruit"},
        {"role": "assistant", "content": "Quand ?", "action": "question"},
        {"role": "user", "content": "quand je freine"},
        {"role": "assistant", "content": "Quel bruit ?", "action": "question"},
        {"role": "user", "content": "un grincement"},
    ]
    r = agent.repondre(historique)
    assert r["action"] == "diagnostic"
    assert "déjà posé 2 questions" in recus[-1][0]["content"]


def test_alerte_securite(service_garages):
    agent, recus = agent_avec(service_garages, {
        "action": "question", "langue": "fr", "message": "Arrêtez-vous en sécurité.", "suggestions": ["ok"],
        "causes": [], "verifications": [], "gravite": "faible", "consulter_garage": False})
    r = agent.repondre([{"role": "user", "content": "il y a de la fumée qui sort du capot"}])
    assert r["alerte_securite"]
    assert r["action"] == "diagnostic" and r["gravite"] == "critique"
    assert "SITUATION POTENTIELLEMENT DANGEREUSE" in recus[-1][0]["content"]


def test_alerte_securite_en_darija(service_garages):
    agent, _ = agent_avec(service_garages, {"action": "diagnostic", "langue": "darija", "message": "Wqef.",
                                            "gravite": "faible"})
    assert agent.repondre([{"role": "user", "content": "kayn dkhan kaykhrej mn lmotor"}])["alerte_securite"]


def test_hors_sujet_sans_contexte(service_garages):
    agent, recus = agent_avec(service_garages, {
        "action": "diagnostic", "langue": "fr", "message": "Rabat.", "causes": [], "gravite": "faible"})
    r = agent.repondre([{"role": "user", "content": "quelle est la capitale du Maroc ?"}])
    assert r["action"] == "hors_sujet"
    assert "AUCUN CONTEXTE FIABLE" in recus[-1][0]["content"]


def test_contexte_transmis_au_llm(service_garages):
    agent, recus = agent_avec(service_garages, {"action": "question", "langue": "fr", "message": "?",
                                                "suggestions": ["a"]})
    agent.repondre(FREINS, vehicule={"marque": "Dacia", "modele": "Logan", "annee": 2019})
    systeme = recus[-1][0]["content"]
    assert "[FRE-01]" in systeme
    assert "VÉHICULE : marque : Dacia" in systeme
