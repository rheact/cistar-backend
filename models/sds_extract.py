from pydantic import BaseModel
from typing import Any, List, Optional, TypedDict

PPESections = TypedDict('PPESections', {
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
    hStatements: Optional[str]
    cp: str
    ppe_pages: Optional[Any]
    ppe_pagerange: Optional[List[int]]
