from fastapi import HTTPException
from models import BaseChemicalIndex, Chemical, Equation, ReactionCalculation

__GAMMA = 1.67
__G = __GAMMA/(1 - __GAMMA)

def get_basis_chemical(eq: Equation, basis: BaseChemicalIndex) -> Chemical:
    # User wants total reaction mass
    if basis is None or basis.index == -1:
        return None

    assert type(basis) == BaseChemicalIndex, "Passed object is not a base chemical index"
    assert basis.list in ['reactants', 'products', 'diluents'], f"List specified is not in equation: {basis.list}"

    # reactants
    if(basis.list == 'reactants'):
        assert basis.index < len(eq.reactants), f'Index out of bound for list {basis.list}: {basis.index}'
        return eq.reactants[basis.index]

    # products
    if(basis.list == 'products'):
        assert basis.index < len(eq.products), f'Index out of bound for list {basis.list}: {basis.index}'
        return eq.products[basis.index]

    # diluents
    assert basis.index < len(eq.diluents), f'Index out of bound for list {basis.list}: {basis.index}'
    return eq.diluents[basis.index]

def get_basis_molWtFraction(base: Chemical) -> float:
    assert base is not None, "Basis is total reaction mass"

    try:
        X_i = float(base.molWtFraction)
    except TypeError:
        raise HTTPException(400, f'Mol wt fraction of {base.productName} is not a float: {base.molWtFraction}')

    if X_i > 1:
        raise HTTPException(400, f'Mol wt fraction of {base.productName} is greater than 1: {base.molWtFraction}')
    
    return X_i

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
    kelvin_ini_T = ini_T + 273.15 # TODO: Change
    ad_P = (kelvin_ini_T/final_T)**(__G) * ini_P

    calcs = {
        'adiabaticTemp': ad_T,
        'finalTemp': final_T,
        'adiabaticPressure': ad_P, 
    }

    return **calcs
    

def get_calculated_cp(equation: Equation) -> float:
    """
    Calculates Cp of mixture
    Cp = sum^{components}_{j} X_j Cp_j
    """
    cp_mix = 0

    concat_components = equation.reactants + equation.products + equation.diluents

    for component in concat_components:
        cp_j: str = component.cp
        X_j: str = component.molWtFraction

        try:
            cp_j = float(component.cp)
        except ValueError:
            raise HTTPException(400, f"Cp is not numeric for {component.productName}")

        try:
            X_j = float(component.molWtFraction)
        except ValueError:
            raise HTTPException(400, f"molWtFraction is not numeric for {component.productName}")
        
        cp_mix += cp_j * X_j
        
    return cp_mix
