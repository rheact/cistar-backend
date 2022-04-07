from models import Chemical, ReactionCalculation
from .basis import get_basis_molWtFraction

def get_final_calculations(ini_T: float, ini_P: float, dH: float, Cp_mix: float, base: Chemical) -> ReactionCalculation:
    """
    Inputs:
    - T in degC
    - P in bar
    - Delta H in cal/g/
    - C_p mix in cal/g/degC
    
    Calculates
    - Adiabatic temperature change
    - Final temperature
    - Adiabatic pressure change
    """

    X_i = 1
    if base is not None:
        X_i = get_basis_molWtFraction(base)

    # ADIABATIC TEMPERATURE CHANGE
    # - Multiply heat of reaction by -1 for exo/endothermic reactions
    # - unit: degC
    ad_T = (-dH / Cp_mix) *  X_i

    # FINAL TEMPERATURE
    # - unit: degC
    final_T = ad_T + ini_T

    # ADIABATIC PRESSURE CHANGE
    # TODO: Fix.
    # kelvin_ini_T = ini_T + 273.15 # TODO: Change
    # ad_P = (kelvin_ini_T/final_T)**(__G) * ini_P

    calcs = {
        'adiabaticTemp': ad_T,
        'finalTemp': final_T,
        'adiabaticPressure': 0, 
    }

    return ReactionCalculation(**calcs)
    