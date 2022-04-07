from pydantic import BaseModel

class ReactionCalculation(BaseModel):
    adiabaticTemp: float
    finalTemp: float
    adiabaticPressure: float
    adiabaticTempDisplay: str = ''
    finalTempDisplay: str = ''
    adiabaticPressureDisplay: str = ''
