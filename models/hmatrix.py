from pydantic import BaseModel

class HMatrixColumn(BaseModel):
    skinAbsorption: str
    skinContact: str
    eyeContact: str
    respiratory: str
    ingestion: str
    sensitizer: str
    carcinogen: str
    reproductiveHazard: str
    organToxicity: str
    flammability: str
    reactivityOrExplosivity: str
