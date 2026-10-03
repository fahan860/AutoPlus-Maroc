"""Formats des requêtes et réponses du service ML (validation automatique par Pydantic)."""

from datetime import date
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Boite(str, Enum):
    manuelle = "manuelle"
    automatique = "automatique"


class Carburant(str, Enum):
    diesel = "diesel"
    essence = "essence"
    hybride = "hybride"
    electrique = "electrique"
    gpl = "gpl"


class Etat(str, Enum):
    neuf = "neuf"
    excellent = "excellent"
    tres_bon = "tres_bon"
    bon = "bon"
    correct = "correct"


class Origine(str, Enum):
    ww_maroc = "ww_maroc"
    dedouanee = "dedouanee"
    importee_neuve = "importee_neuve"
    non_dedouanee = "non_dedouanee"


class Equipement(str, Enum):
    vitres_electriques = "vitres_electriques"
    bluetooth = "bluetooth"
    jantes_alu = "jantes_alu"
    climatisation = "climatisation"
    airbags = "airbags"
    verrouillage_central = "verrouillage_central"
    camera_recul = "camera_recul"
    abs = "abs"
    sieges_cuir = "sieges_cuir"
    limiteur_vitesse = "limiteur_vitesse"
    regulateur_vitesse = "regulateur_vitesse"
    radar_recul = "radar_recul"
    ordinateur_bord = "ordinateur_bord"
    esp = "esp"
    gps = "gps"
    toit_ouvrant = "toit_ouvrant"


class DemandeEstimation(BaseModel):
    marque: str = Field(min_length=1, max_length=50, examples=["dacia"])
    modele: str = Field(min_length=1, max_length=80, examples=["logan"])
    annee: int = Field(ge=1980, examples=[2019])
    kilometrage: int | None = Field(default=None, ge=0, le=1_000_000, examples=[87000])
    boite: Boite
    carburant: Carburant
    puissance_fiscale: int | None = Field(default=None, ge=3, le=60, examples=[6])
    etat: Etat | None = None
    origine: Origine | None = None
    premiere_main: bool | None = None
    ville: str | None = Field(default=None, max_length=60, examples=["Casablanca"])
    nb_portes: Literal[3, 5] | None = None
    equipements: list[Equipement] = Field(default_factory=list, max_length=len(Equipement))

    @field_validator("annee")
    @classmethod
    def annee_pas_dans_le_futur(cls, annee: int) -> int:
        if annee > date.today().year + 1:
            raise ValueError(f"l'année ne peut pas dépasser {date.today().year + 1}")
        return annee


class Fourchette(BaseModel):
    min: int
    max: int


class Estimation(BaseModel):
    prix_estime: int = Field(description="Prix estimé en dirhams (niveau de prix des annonces 2024)")
    fourchette: Fourchette = Field(description="Contient le prix réel de ~80 % des annonces de test comparables")
    fiabilite: Literal["normale", "reduite"]
    avertissements: list[str]
    version_modele: str


class Options(BaseModel):
    marques: list[str]
    modeles_par_marque: dict[str, list[str]]
    villes: list[str]


# ─── Modèle B : recommandation de garages ────────────────────────────────────


class DemandeRecommandation(BaseModel):
    description: str = Field(min_length=3, max_length=500, examples=["ça grince quand je freine"])
    lat: float | None = Field(default=None, ge=-90, le=90, examples=[33.5822])
    lon: float | None = Field(default=None, ge=-180, le=180, examples=[-7.6327])
    nb_garages: int = Field(default=5, ge=1, le=20)


class CategorieProbable(BaseModel):
    categorie: str
    probabilite: float


class PanneProche(BaseModel):
    code: str
    titre: str
    categorie: str
    urgence: str | None
    cout_min_dh: float | None
    cout_max_dh: float | None


class GarageRecommande(BaseModel):
    id: int
    nom: str
    adresse: str | None
    telephone: str | None
    distance_km: float | None
    note: float | None
    nb_avis: int
    specialites: list[str]
    specialites_confirmees: bool = Field(description="False : spécialités supposées (mécanique générale)")
    score: float
    raisons: list[str] = Field(description="Pourquoi ce garage est proposé, à afficher tel quel")


class Recommandation(BaseModel):
    categories_probables: list[CategorieProbable]
    pannes_proches: list[PanneProche]
    garages: list[GarageRecommande]
    avertissements: list[str]
    version_modele: str


# ─── Modèle C : détection de faux avis ───────────────────────────────────────


class DemandeModeration(BaseModel):
    review_id: int = Field(ge=1, description="Avis déjà enregistré en base, à vérifier")


class DecisionModeration(BaseModel):
    review_id: int
    decision: Literal["publier", "verifier"]
    score: float = Field(description="Probabilité estimée de faux avis (0-1)")
    raisons: list[str] = Field(description="Pourquoi l'avis est à vérifier, pour l'admin")
    version_modele: str


# ─── Agent IA de diagnostic ──────────────────────────────────────────────────


class MessageConversation(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=1000)
    action: Literal["question", "diagnostic", "hors_sujet"] | None = Field(
        default=None, description="Pour les messages de l'assistant : sert à compter les questions déjà posées")


class VehiculeConversation(BaseModel):
    marque: str | None = Field(default=None, max_length=50)
    modele: str | None = Field(default=None, max_length=80)
    annee: int | None = Field(default=None, ge=1950, le=2100)
    kilometrage: int | None = Field(default=None, ge=0, le=2_000_000)


class DemandeAgent(BaseModel):
    messages: list[MessageConversation] = Field(min_length=1, max_length=20,
                                                description="Historique complet, le dernier message vient de l'utilisateur")
    vehicule: VehiculeConversation | None = None
    lat: float | None = Field(default=None, ge=-90, le=90)
    lon: float | None = Field(default=None, ge=-180, le=180)

    @field_validator("messages")
    @classmethod
    def dernier_message_utilisateur(cls, messages):
        if messages[-1].role != "user":
            raise ValueError("le dernier message doit venir de l'utilisateur")
        return messages


class CauseAgent(BaseModel):
    titre: str
    explication: str
    source: str


class SourceAgent(BaseModel):
    id: str
    titre: str


class ReponseAgent(BaseModel):
    action: Literal["question", "diagnostic", "hors_sujet"]
    langue: Literal["fr", "darija"]
    message: str
    suggestions: list[str] = Field(description="Réponses courtes proposées quand l'agent pose une question")
    causes: list[CauseAgent]
    verifications: list[str]
    gravite: Literal["faible", "moyenne", "elevee", "critique"] | None
    alerte_securite: bool
    consulter_garage: bool
    sources: list[SourceAgent]
    garages: list[GarageRecommande] = Field(description="Garages adaptés, après une analyse")
    description_reformulee: str
    duree_ms: int
    version_modele: str
