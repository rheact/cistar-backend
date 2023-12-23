from multiprocessing.sharedctypes import Value
from helpers.errors import InputDataError
from models import Equation, Chemical

"""
    Calculate heap capacity (Cp) of mixture
    Cp = sum^{components}_{j} X_j * Cp_j
    X_j: molecular weight fraction of chemical j
"""
def get_calculated_cp(equation: Equation, base: Chemical) -> float:
    cp_mix = 0
    X_total = 0

    concat_components = equation.reactants + equation.products + equation.diluents
    included_components = [c for c in concat_components if not c.neglected]
    if len(included_components) == 0:
        raise InputDataError("No Cp mixture entered and no components included for calculating Cp of mixture")

    # Check mass fraction of reactants separately
    totalMF = 0
    for reactant in equation.reactants:
        cp_j: str = reactant.cp
        X_j: str = reactant.molWtFraction

        try: X_j = float(reactant.molWtFraction)
        except ValueError: raise InputDataError(f"Mass fraction is not numeric for {reactant.productName}")
        assert X_j > 0 and X_j <= 1, f"Mass fraction of a reactant must be in range (0, 1]! Error for {reactant.productName}"
        totalMF += X_j

        if not reactant.neglected:
            try: cp_j = float(reactant.cp)
            except ValueError: raise InputDataError(f"Cp is not numeric for {reactant.productName}")
            assert cp_j > 0, f"Component heat capacities are required to be greater than zero. Error for {reactant.productName}."

            cp_mix += cp_j * X_j
            X_total += X_j


    # Check if mass fraction of all components sum up to one
    # Also check if mass fraction of products & diluents is valid
    for component in equation.products + equation.diluents:
        cp_j: str = component.cp
        X_j: str = component.molWtFraction

        try: X_j = float(component.molWtFraction)
        except ValueError: raise InputDataError(f"Mass fraction is not numeric for {component.productName}")
        assert X_j >= 0 and X_j <= 1, f"Mass fraction of a product/diluent must be in range [0, 1]! Error for {component.productName}"
        totalMF += X_j

        if not component.neglected:
            try: cp_j = float(component.cp)
            except ValueError: raise InputDataError(f"Cp is not numeric for {component.productName}")
            assert cp_j > 0, f"Component heat capacities are required to be greater than zero. Error for {component.productName}."

            cp_mix += cp_j * X_j
            X_total += X_j



    # Only add components that aren't neglected
    # for component in included_components:
    #     cp_j: str = component.cp
    #     X_j: str = component.molWtFraction

    #     try: cp_j = float(component.cp)
    #     except ValueError: raise InputDataError(f"Cp is not numeric for {component.productName}")
    #     assert cp_j > 0, f"Component heat capacities are required to be greater than zero. Error for {component.productName}."

    #     # X_j = float(component.molWtFraction)
    #     try: X_j = float(component.molWtFraction)
    #     except ValueError: raise InputDataError(f"Mass fraction is not numeric for {component.productName}")
    #     assert X_j > 0, f"Mass fraction must be in range[0, 1]! Error for {component.productName}"

    #     cp_mix += cp_j * X_j
    #     X_total += X_j
    
    assert X_total <= 1 or X_total >= 0.95, f"Total mass fraction must be in range [0.95, 1]!"

    # Rescaling
    cp_mix /= X_total

    return cp_mix
