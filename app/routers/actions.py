from fastapi import APIRouter
from helpers.errors import InputDataError
from helpers.units import conversions
from services.database import estimate_cp_from_database

router = APIRouter()

@router.post('/estimate_cp')
async def estimate_cp(temperature: str, unit: str, cas_no: str):
    """
    Temperature is required to caluclate Cp of the compound.
    """
    if unit is None:
        raise InputDataError("No unit passed for temperature")

    try:
        temperature = float(temperature)
    except ValueError:
        raise InputDataError("Temperature is not a number")

    # Standardise temperature
    temperature = conversions.std_T(temperature, unit)

    # Check temperature bounds
    assert temperature > -273.15, "Temperature is absolute zero!"

    cp = estimate_cp_from_database(cas_no, temperature)
    return cp
