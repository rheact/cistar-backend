from pydantic import BaseModel

class ReactionCalculation(BaseModel):
    adiabaticTemp: float
    finalTemp: float
    adiabaticPressure: float
