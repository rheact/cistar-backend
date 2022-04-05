from models import BaseChemicalIndex, Chemical, Equation, ReactionCalculation

__GAMMA = 1.67
__G = __GAMMA/(1 - __GAMMA)

def get_basis(eq: Equation, basis: BaseChemicalIndex) -> Chemical:
    assert type(basis) == BaseChemicalIndex, "Passed object is not a base chemical index"
    assert basis.list in ['reactants', 'products', 'diluents'], f"List specified is not in equation: {basis.list}"

    if(basis.list == 'reactants'):
        assert basis.index < len(eq.reactants), f'Index out of bound for list {basis.list}: {basis.index}'
        return eq.reactants[basis.index]

    if(basis.list == 'products'):
        assert basis.index < len(eq.products), f'Index out of bound for list {basis.list}: {basis.index}'
        return eq.products[basis.index]

    assert basis.index < len(eq.diluents), f'Index out of bound for list {basis.list}: {basis.index}'
    return eq.diluents[basis.index]

def get_final_calculations(ini_T: float, ini_P: float, d_h: float, cp_mix: float, baseIndex: BaseChemicalIndex, eq: Equation) -> ReactionCalculation:
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

    base = get_basis(eq, baseIndex)
    try:
        X_i = float(base.molWtFraction)
    except ValueError:
        raise Exception(f'Mol wt fraction of {base.productName} is not a float: {base.molWtFraction}')

    if X_i > 1:
        raise Exception(f'Mol wt fraction of {base.productName} is greater than 1: {base.molWtFraction}')

    print('BASE CHEMICAL WT FRACTION ' + str(X_i))

    # ADIABATIC TEMPERATURE CHANGE
    # - Multiply heat of reaction by -1 for exo/endothermic reactions
    # - unit: degC
    ad_T = (-d_h / cp_mix) *  X_i

    # FINAL TEMPERATURE
    # - unit: degC
    final_T = ad_T + ini_T

    # ADIABATIC PRESSURE CHANGE
    # TODO: Fix.
    kelvin_ini_T = ini_T + 273.15 # TODO: Change
    ad_P = (kelvin_ini_T/final_T)**(__G) * ini_P

    return {
        'adiabaticTemp': ad_T,
        'finalTemp': final_T,
        'adiabaticPressure': ad_P, 
    }
    

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
            raise Exception(f"Cp is not numeric for {component.productName}")

        try:
            X_j = float(component.molWtFraction)
        except ValueError:
            raise Exception(f"molWtFraction is not numeric for {component.productName}")
        
        cp_mix += cp_j * X_j
        
    return cp_mix
