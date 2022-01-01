from pydantic import BaseModel

class HMatrixColumn(BaseModel):
    flammability: str
    reactivity: str
    skinAbsorption: str
    skinContact: str
    eyeContact: str
    respiratory: str
    carcinogen: str
    reproductiveHazard: str
    sensitizer: str
    other: str
    ingestion: str
