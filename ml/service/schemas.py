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
