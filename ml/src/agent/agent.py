"""
Agent IA de diagnostic AUTO+ (V1, cf. ai/docs/V1_SCOPE.md).

À chaque message, l'agent :
  1. repère une situation dangereuse (fumée, freins qui lâchent, odeur d'essence...) ;
  2. cherche le contexte dans les deux bases, avec le même encodeur e5-large que le Modèle B :
     la Knowledge Base (kb_documents / kb_chunks, ai/) et les 50 pannes de base_pannes ;
  3. demande au LLM (Mistral ou Groq, voir FOURNISSEURS), en JSON, de POSER UNE QUESTION si l'information manque, ou de
     DONNER UNE ANALYSE prudente, uniquement à partir de ce contexte ;
  4. contrôle la réponse : sources citées existantes, gravité valide, au plus
     MAX_QUESTIONS questions avant de devoir répondre ;
  5. après une analyse, propose des garages (Modèle B).

L'agent est sans état : l'app renvoie l'historique de la conversation à chaque message.
Jamais de diagnostic certain : l'analyse est orientative et renvoie vers un professionnel.
"""

import json
import os
import re
import time
import unicodedata
from dataclasses import dataclass

import requests

# Fournisseurs de LLM, tous au format « chat completions » d'OpenAI : on passe de l'un à l'autre
# avec LLM_FOURNISSEUR dans .env, sans toucher au code.
#   mistral : retenu par l'équipe après le test darija (ai/scripts/test_darija_generation.py), API payante
#   groq    : gratuit (avec limites), utilisé pour les tests tant que l'API Mistral n'est pas activée
FOURNISSEURS = {
    "mistral": {"url": "https://api.mistral.ai/v1/chat/completions", "modele": "mistral-medium-latest",
                "cle": "MISTRAL_API_KEY"},
    "groq": {"url": "https://api.groq.com/openai/v1/chat/completions", "modele": "openai/gpt-oss-120b",
             "cle": "GROQ_API_KEY"},
}
LLM_TIMEOUT_S = 40

MAX_QUESTIONS = 2  # au-delà, l'agent doit donner son analyse avec ce qu'il sait
NB_KB, NB_PANNES = 4, 3  # passages de contexte transmis au LLM
# En dessous, le contexte trouvé n'est pas assez proche de la demande pour s'y fier
# (similarité cosinus e5). Mesuré sur 44 questions auto (dont darija) et 10 hors sujet : les
# deux groupes se chevauchent (« quel temps fait-il demain » 0,821 > darija 0,806), donc un seuil
# seul ne peut pas les séparer. 0,79 ne rejette aucune vraie question auto ; les hors-sujet qui
# passent (4/10) sont écartés par la consigne « hors_sujet » donnée au LLM.
SEUIL_PERTINENCE = 0.79
GRAVITES = ["faible", "moyenne", "elevee", "critique"]

# Situations où l'on dit d'abord de s'arrêter, avant toute analyse (français + darija)
DANGERS = [
    r"fum[ée]e.{0,30}(capot|moteur)", r"\bfeu\b", r"flamme", r"odeur d.?essence", r"fuite d.?essence",
    r"frein.{0,25}(lach|r[ée]pond plus|ne marche plus|ne freine)", r"p[ée]dale.{0,25}(au fond|plancher)",
    r"direction.{0,15}bloqu", r"voyant.{0,15}huile.{0,15}rouge", r"surchauffe.{0,30}(fum|bout)",
    r"\bdkhan\b", r"\bl3afia\b", r"fran.{0,15}ma\s?(kaychd|kayhbs|khdamch)", r"riht? (l)?(essence|lisans)",
]

# Étape 1 : reformuler la conversation en une phrase française avant la recherche. La base est en
# français : chercher directement avec un message en darija trouvait de mauvais contextes
# (« tomobil dyali katsfer mli kanfrani », un sifflement au freinage, donnait « filtre à air »).
PROMPT_REFORMULATION = """Tu reçois une conversation entre un automobiliste au Maroc (en français ou en darija, écrite en lettres latines ou arabes) et un assistant.
Réécris le problème de la voiture en UNE phrase en français simple, avec les symptômes décrits (bruit, voyant, odeur, fumée, moment où ça arrive...). N'ajoute aucune cause ni interprétation.
Aide darija : tomobil / tonobil / karhba = voiture ; frana / kanfrani = frein / je freine ; katsfer = siffle ; katzgi / kat3yet = grince ; lmotor = le moteur ; kaysakhn = chauffe ; dkhan = fumée ; ma bghatch tkhdem / ma katdemarrich = ne démarre pas ; batri = batterie ; dwaw = voyant / phares ; lclim = la climatisation ; kat9tel / katmout = cale ; bzaf = beaucoup.
Réponds UNIQUEMENT en JSON : {"description_fr": "...", "langue": "fr" ou "darija", "hors_sujet": true ou false}
langue = la langue dans laquelle l'automobiliste écrit. hors_sujet = true si la demande ne concerne pas une voiture."""

PROMPT_SYSTEME = """Tu es l'assistant de diagnostic automobile de l'application AUTO+, pour des automobilistes au Maroc.

LANGUE : réponds dans la langue de l'utilisateur. S'il écrit en darija (lettres latines ou arabes), réponds en darija marocaine naturelle écrite en lettres latines, comme sur WhatsApp. Sinon, réponds en français simple.

RÈGLES :
- Base-toi UNIQUEMENT sur le CONTEXTE fourni (base de connaissance vérifiée). N'invente jamais une cause, un prix ou un conseil absent du contexte.
- Ne donne JAMAIS un diagnostic certain : présente des pistes possibles et recommande de faire vérifier par un garage.
- Si la description est trop vague pour choisir entre les pistes du contexte, pose UNE seule question courte et utile (bruit ? voyant ? quand ça arrive ?), avec 2 à 4 réponses courtes proposées.
- Si le contexte ne correspond pas à la demande, ou si la demande ne concerne pas une voiture, réponds avec l'action "hors_sujet" et un message bref.
- Ton calme et rassurant, sans minimiser un problème grave. Phrases courtes.
- Les vérifications proposées doivent être sans danger : jamais sous le capot moteur chaud, jamais ouvrir le bouchon du radiateur ou du vase d'expansion à chaud, jamais rouler pour « tester » un frein ou une direction douteux.

FORMAT : réponds UNIQUEMENT avec un objet JSON :
{
  "action": "question" | "diagnostic" | "hors_sujet",
  "langue": "fr" | "darija",
  "message": "texte principal affiché à l'utilisateur (2 à 4 phrases)",
  "suggestions": ["réponses courtes proposées, seulement si action = question"],
  "causes": [{"titre": "cause possible", "explication": "1 phrase simple", "source": "identifiant exact du contexte"}],
  "verifications": ["ce que l'utilisateur peut observer ou vérifier sans risque"],
  "gravite": "faible" | "moyenne" | "elevee" | "critique",
  "consulter_garage": true | false
}
Pour "question" et "hors_sujet", laisse causes et verifications vides. Les identifiants de source sont ceux entre crochets dans le contexte."""


@dataclass
class Passage:
    id: str
    titre: str
    texte: str
    gravite: str | None
    similarite: float
    categorie: str | None = None


def normaliser(texte: str) -> str:
    return unicodedata.normalize("NFKD", texte or "").encode("ascii", "ignore").decode().lower()


def danger(texte: str) -> bool:
    t = (texte or "").lower()
    return any(re.search(motif, t) or re.search(motif, normaliser(t)) for motif in DANGERS)


class AgentDiagnostic:
    """service_garages : le ServiceRecommandation du Modèle B (encodeur e5, classifieur de
    pannes, recommandation de garages), partagé pour ne charger e5-large qu'une fois."""

    def __init__(self, url_base: str, service_garages, fournisseur: str | None = None, cle: str | None = None,
                 appel_llm=None):
        self.url_base = url_base
        self.garages = service_garages
        self.classifieur = service_garages.classifieur
        nom = fournisseur or os.environ.get("LLM_FOURNISSEUR", "mistral")
        if nom not in FOURNISSEURS:
            raise RuntimeError(f"LLM_FOURNISSEUR inconnu : {nom} (choix : {', '.join(FOURNISSEURS)})")
        self.llm = FOURNISSEURS[nom]
        self.cle = cle or os.environ.get(self.llm["cle"])
        self.appel_llm = appel_llm or self._appeler_llm  # remplaçable dans les tests
        if not self.cle and appel_llm is None:
            raise RuntimeError(f"{self.llm['cle']} absente (LLM_FOURNISSEUR={nom})")
        self.version = f"agent-v1-{nom}-{self.llm['modele']}"

    # ─── Recherche du contexte ──────────────────────────────────────────────

    def _kb(self, vecteur) -> list[Passage]:
        import psycopg2

        litteral = "[" + ",".join(f"{x:.6f}" for x in vecteur) + "]"
        with psycopg2.connect(self.url_base) as conn, conn.cursor() as cur:
            cur.execute(
                """SELECT DISTINCT ON (d.id) d.id, d.symptome, d.cause, d.explication, d.verification, d.gravite,
                          1 - (c.embedding <=> %(v)s::vector) AS sim
                   FROM kb_chunks c JOIN kb_documents d ON d.id = c.document_id
                   ORDER BY d.id, c.embedding <=> %(v)s::vector""",
                {"v": litteral},
            )
            lignes = sorted(cur.fetchall(), key=lambda r: -r[6])[:NB_KB]
        return [Passage(id=r[0], titre=r[1], gravite=r[5], similarite=float(r[6]),
                        texte=f"Symptôme : {r[1]}. Cause probable : {r[2]}. Explication : {r[3]} "
                              f"À vérifier : {r[4]} Urgence : {r[5]}.")
                for r in lignes]

    def _pannes(self, vecteur) -> list[Passage]:
        sims = self.classifieur.vecteurs @ vecteur
        passages = []
        for i in sims.argsort()[::-1][:NB_PANNES]:
            p = self.classifieur.pannes[i]
            cout = (f" Coût indicatif : {p.cout_min_dh:.0f} à {p.cout_max_dh:.0f} DH."
                    if p.cout_min_dh is not None and p.cout_max_dh is not None else "")
            passages.append(Passage(id=p.code, titre=p.titre, gravite=p.urgence, similarite=float(sims[i]),
                                    categorie=p.categorie, texte=f"{p.texte}. Urgence : {p.urgence}.{cout}"))
        return passages

    # ─── LLM ────────────────────────────────────────────────────────────────

    def _appeler_llm(self, messages: list[dict]) -> str:
        reponse = requests.post(
            self.llm["url"],
            headers={"Authorization": f"Bearer {self.cle}"},
            json={"model": self.llm["modele"], "messages": messages, "temperature": 0.2,
                  "response_format": {"type": "json_object"}},
            timeout=LLM_TIMEOUT_S,
        )
        reponse.raise_for_status()
        return reponse.json()["choices"][0]["message"]["content"]

    # ─── Un tour de conversation ────────────────────────────────────────────

    def repondre(self, historique: list[dict], vehicule: dict | None = None,
                 lat: float | None = None, lon: float | None = None) -> dict:
        debut = time.monotonic()
        messages_user = [m["content"] for m in historique if m["role"] == "user"]
        nb_questions = sum(1 for m in historique if m["role"] == "assistant" and m.get("action") == "question")
        reformulation = self._reformuler(historique)
        description = str(reformulation.get("description_fr") or "").strip()
        texte_recherche = description or " ".join(messages_user[-3:])
        langue = "darija" if reformulation.get("langue") == "darija" else "fr"
        alerte = danger(" ".join(messages_user)) or danger(description)

        vecteur = self.classifieur.encodeur.requetes([texte_recherche])[0]
        kb, pannes = self._kb(vecteur), self._pannes(vecteur)
        passages = sorted(kb + pannes, key=lambda p: -p.similarite)
        fiables = [p for p in passages if p.similarite >= SEUIL_PERTINENCE]

        contexte = "\n".join(f"[{p.id}] {p.texte}" for p in fiables) or "AUCUN CONTEXTE FIABLE TROUVÉ."
        consignes = [f"CONTEXTE :\n{contexte}", f"PROBLÈME DÉCRIT (reformulé) : {texte_recherche}",
                     "LANGUE DE LA RÉPONSE : " + ("darija marocaine en lettres latines" if langue == "darija" else "français")]
        if vehicule:
            consignes.append("VÉHICULE : " + ", ".join(f"{k} : {v}" for k, v in vehicule.items() if v))
        if alerte:
            consignes.append("ATTENTION : SITUATION POTENTIELLEMENT DANGEREUSE. Commence le message par dire de "
                             "s'arrêter dès que possible en sécurité et de ne pas continuer à rouler. "
                             "Ne propose aucune vérification sous le capot avant que le moteur ait refroidi, et dis-le. "
                             "Gravité \"critique\". Ne pose pas de question.")
        if nb_questions >= MAX_QUESTIONS:
            consignes.append(f"Tu as déjà posé {nb_questions} questions : donne maintenant ton analyse (action "
                             "\"diagnostic\") avec les informations disponibles, sans nouvelle question.")
        if not fiables:
            consignes.append("Aucun contexte fiable : n'analyse pas. Si la demande concerne une voiture, propose de "
                             "reformuler ou de consulter un garage ; sinon action \"hors_sujet\".")

        messages = [{"role": "system", "content": PROMPT_SYSTEME + "\n\n" + "\n\n".join(consignes)}]
        for m in historique[-8:]:
            messages.append({"role": m["role"], "content": m["content"]})

        brut = json.loads(self.appel_llm(messages))
        sortie = self._controler(brut, fiables, alerte, nb_questions)

        if sortie["action"] == "diagnostic" and fiables:
            sortie["categorie"] = next((p.categorie for p in fiables if p.categorie), None)
        sortie["duree_ms"] = int((time.monotonic() - debut) * 1000)
        sortie["version_modele"] = self.version
        sortie["description_reformulee"] = texte_recherche
        sortie["_probas"] = self.classifieur.probabilites(vecteur)  # pour la recommandation de garages
        return sortie

    def _reformuler(self, historique: list[dict]) -> dict:
        """Une phrase française décrivant le problème, pour la recherche. En cas d'échec, {} :
        la recherche se fait alors sur les messages bruts."""
        transcription = "\n".join(f"{'Automobiliste' if m['role'] == 'user' else 'Assistant'} : {m['content']}"
                                  for m in historique[-8:])
        try:
            reponse = json.loads(self.appel_llm([{"role": "system", "content": PROMPT_REFORMULATION},
                                                 {"role": "user", "content": transcription}]))
            return reponse if isinstance(reponse, dict) else {}
        except (ValueError, requests.RequestException):
            return {}

    @staticmethod
    def _controler(brut: dict, fiables: list[Passage], alerte: bool, nb_questions: int) -> dict:
        """Ce que le LLM renvoie n'est jamais affiché tel quel : on garde seulement ce qui respecte
        le format et les sources réellement fournies."""
        connus = {p.id: p for p in fiables}
        action = brut.get("action") if brut.get("action") in ("question", "diagnostic", "hors_sujet") else "diagnostic"
        if action == "question" and (alerte or nb_questions >= MAX_QUESTIONS):
            action = "diagnostic"
        if not fiables and action == "diagnostic":
            action = "hors_sujet"

        causes = [
            {"titre": str(c.get("titre", ""))[:150], "explication": str(c.get("explication", ""))[:300],
             "source": c.get("source")}
            for c in brut.get("causes") or [] if isinstance(c, dict) and c.get("source") in connus
        ][:4]
        gravite = brut.get("gravite") if brut.get("gravite") in GRAVITES else "moyenne"
        # La gravité ne descend jamais sous celle des sources citées (le LLM ne doit pas rassurer à tort)
        citees = [connus[c["source"]].gravite for c in causes if connus[c["source"]].gravite in GRAVITES]
        if citees:
            gravite = max([gravite, *citees], key=GRAVITES.index)
        if alerte:
            gravite = "critique"

        diagnostic = action == "diagnostic"
        return {
            "action": action,
            "langue": "darija" if brut.get("langue") == "darija" else "fr",
            "message": str(brut.get("message", "")).strip()[:1200],
            "suggestions": [str(s)[:60] for s in (brut.get("suggestions") or [])][:4] if action == "question" else [],
            "causes": causes if diagnostic else [],
            "verifications": [str(v)[:250] for v in (brut.get("verifications") or [])][:5] if diagnostic else [],
            "gravite": gravite if diagnostic else None,
            "alerte_securite": alerte,
            "consulter_garage": diagnostic or alerte,
            "sources": [{"id": c["source"], "titre": connus[c["source"]].titre} for c in causes],
        }
