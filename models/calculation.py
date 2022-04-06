from pydantic import BaseModel

class ReactionCalculation(BaseModel):
    adiabaticTemp: float
    finalTemp: float
    adiabaticPressure: float
    adiabaticTempDisplay: float = -999999.99
    finalTempDisplay: float = -999999.99
    adiabaticPressureDisplay: str = -999999.99
