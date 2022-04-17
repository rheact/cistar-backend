from multiprocessing.sharedctypes import Value
from helpers.errors import InputDataError
from models import Equation

def get_calculated_cp(equation: Equation) -> float:
    """
    Calculates Cp of mixture
    Cp = sum^{components}_{j} X_j Cp_j
    """
    cp_mix = 0
    X_total = 0
    concat_components = equation.reactants + equation.products + equation.diluents
    included_components = [c for c in concat_components if not c.neglected]
    if len(included_components) == 0:
        raise InputDataError("No Cp mixture entered and no components included for calculating Cp of mixture")

    # Only add components that aren't neglected
    for component in included_components:
        cp_j: str = component.cp
        X_j: str = component.molWtFraction

        try: cp_j = float(component.cp)
        except ValueError: raise InputDataError(f"Cp is not numeric for {component.productName}")
        assert cp_j > 0, f"Cp must be non-zero, non-positive! Error for {component.productName}"

        try: X_j = float(component.molWtFraction)
        except ValueError: raise InputDataError(f"molWtFraction is not numeric for {component.productName}")
        assert X_j > 0, f"Mass fraction must be non-zero, non-positive! Error for {component.productName}"

        cp_mix += cp_j * X_j
        X_total += X_j

    # Rescaling
    cp_mix /= X_total

    return cp_mix
