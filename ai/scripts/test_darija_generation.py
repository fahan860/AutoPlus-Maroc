"""
Test de generation en darija (ebauche Phase 8) : recupere le contexte via
search_kb() (retrieval Phase 6, deja fonctionnel) puis genere une reponse en
darija avec Mistral, pour juger la qualite avant d'arreter un choix de LLM.

Les questions de test sont en francais (tirees de formulations client
realistes) : c'est la SORTIE generee par le modele qui doit etre en darija,
pas les questions elles-memes -- on ne veut pas inventer du darija cote
question, seulement juger celui que Mistral produit.

Usage : python ai/scripts/test_darija_generation.py
Necessite MISTRAL_API_KEY dans l'environnement (voir api/.env).
"""

import os
import sys
from pathlib import Path

import truststore

truststore.inject_into_ssl()

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
load_dotenv(ROOT / "api" / ".env")

sys.path.insert(0, str(HERE))
from query_kb import search_kb  # reutilise le retrieval Phase 6

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
MISTRAL_MODEL = "mistral-medium-latest"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"

SYSTEM_PROMPT = """Tu es l'assistant de diagnostic automobile AUTO+, pour des automobilistes au Maroc.
Reponds TOUJOURS en darija marocaine naturelle (ecrite en caracteres latins, comme les Marocains ecrivent sur WhatsApp), jamais en arabe standard ni en francais.
Base-toi UNIQUEMENT sur les informations du contexte fourni ci-dessous (extraites d'une base de connaissance verifiee) : n'invente jamais une cause ou un conseil qui n'y figure pas.
Ne donne JAMAIS un diagnostic certain : presente des pistes possibles, precise le niveau d'urgence si le contexte le donne, et recommande de consulter un garage/professionnel pour confirmer.
Reste bref (3 a 5 phrases), clair, et rassurant sans minimiser un probleme grave."""

# Questions realistes en francais, choisies pour couvrir differents niveaux
# d'urgence (moyenne / elevee / critique) deja presents dans kb_corpus_v1.
TEST_QUERIES = [
    "ma voiture cale au demarrage le matin",
    "il y a un bruit de grincement quand je freine",
    "la pedale de frein devient molle, j'ai peur",
]


def build_context_block(results):
    if not results:
        return "Aucune information pertinente trouvee dans la base de connaissance."
    lines = []
    for r in results:
        lines.append(
            f"- Symptome: {r['symptome']}\n"
            f"  Cause probable: {r['cause']}\n"
            f"  A verifier: {r['verification']}\n"
            f"  Urgence: {r['gravite']}"
        )
    return "\n".join(lines)


def call_mistral(prompt):
    import requests

    payload = {
        "model": MISTRAL_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    }
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}"}
    resp = requests.post(MISTRAL_URL, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


def main():
    if not MISTRAL_API_KEY:
        print(
            "MISTRAL_API_KEY introuvable (attendu dans api/.env). "
            "Je ne devine jamais des identifiants : merci de le renseigner puis relancer.",
            file=sys.stderr,
        )
        sys.exit(1)

    for query in TEST_QUERIES:
        print(f"\n{'=' * 70}\nQuestion utilisateur (FR) : {query}\n{'=' * 70}")

        results = search_kb(query, top_k=3)
        context = build_context_block(results)
        print(f"\n--- Contexte recupere (retrieval, deja valide) ---\n{context}")

        prompt = f"Contexte:\n{context}\n\nQuestion de l'utilisateur : {query}\n\nReponse (en darija) :"
        try:
            answer = call_mistral(prompt)
        except Exception as err:
            answer = f"[ERREUR appel Mistral : {err}]"
        print(f"\n--- Reponse generee par Mistral (a juger : qualite du darija) ---\n{answer}")


if __name__ == "__main__":
    main()
