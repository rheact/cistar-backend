"""
RHEACT JSON v3 STANDARD
Drafted by: Vikrant Gajria
"""

from numpy import number
from pydantic import BaseModel
from typing import List, Optional, Any

from models.sds import SDSExtraction

class Chemical(SDSExtraction):
    """
    Chemical represents data extracted from SDS,
    Plus the molecular weight fraction added by user.
    """
    molWtFraction: Optional[str]

class BaseChemicalIndex(BaseModel):
    """
    An index for base chemical for /mol units
    """
    list: str
    index: int

class Equation(BaseModel):
    """
    Equation represents chemicals involved in a reaction.
    """
    numReactants: int
    numProducts: int
    numDiluents: int
    reactants: List[Chemical]
    products: List[Chemical]
    diluents: List[Chemical]

class SideReaction(BaseModel):
    """
    SideReactions are additional data in the report.
    """
    tempOnset: str
    pressureOnset: str
    details: str

class OperatingParams(BaseModel):
    """
    OperatingParams represent data used in calulation.
    """
    temperature: str
    temperatureUnit: Optional[str]
    pressure: str
    pressureUnit: Optional[str]
    heatOfReaction: str
    heatOfReactionUnit: Optional[str]
    cp: Optional[str]
    cpUnit: Optional[str]
    basis: Optional[BaseChemicalIndex]
    physicalState: Optional[str]
    reactionClass: Optional[str]
    reactionScale: Optional[str]
    keyReactantQuantity: Optional[str]
    numSideReactions: int
    sideReactions: List[SideReaction]

class HazardRow(BaseModel):
    """
    Hazard Matrix
    """
    carcinogen: str
    eyeContact: str
    flammability: str
    ingestion: str
    other: str
    reactivity: str
    reproductiveHazard: str
    respiratory: str
    sensitizer: str
    skinAbsorption: str
    skinContact: str

class Results(BaseModel):
    """
    Results returned by server
    """
    adiabaticPressure: Optional[str]
    adiabaticTemp: Optional[str]
    finalTemp: Optional[str]
    cameoMatrix: Optional[Any] # TODO: Specify
    hazardMatrix: Optional[List[Any]] #TODO: Specify
    hNums: Optional[Any] # TODO: Specify

class RheactState(BaseModel):
    """
    RheactState is the root state of Rheact's user input.
    """
    type: Optional[str]
    nameOfResearcher: Optional[str]
    projectTitle: Optional[str]
    labLocation: Optional[str]
    principalInvestigator: Optional[str]
    organization: Optional[str]
    chemicalScheme: Optional[str]
    description: Optional[str]
    compound: Equation
    operatingParams: OperatingParams
    results: Optional[Results]
