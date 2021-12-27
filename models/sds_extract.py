from pydantic import BaseModel
from typing import Dict, List, Optional, TypedDict

PPESectionsT = TypedDict('PPESectionsT', {
    "Appropriate Engineering Controls": str,
    "Eye/face protection": str,
    "Skin protection": str,
    "Body protection": str,
    "Respiratory protection": str,
    "Control of environmental exposure": str,
})

class SDSExtraction(BaseModel):
    productName: str
    molWt: str
    casNo: str
    ph: str
    boilingPt: str
    flashPt: str
    vapourPressure: str
    vapourDensity: str
    relDensity: str
    autoIgnitionTemp: str
    decompositionTemp: str
    viscosity: str
    upperExplosionLim: str
    lowerExplosionLim: str
    hNumbers: str
    hStatements: str
    cp: float
    ppe_pages: Optional[List[int]]
    ppe_sections: PPESectionsT
