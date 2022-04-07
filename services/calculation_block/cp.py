from fastapi import HTTPException
from models import Equation

def get_calculated_cp(equation: Equation) -> float:
    """
    Calculates Cp of mixture
    Cp = sum^{components}_{j} X_j Cp_j
    """
    cp_mix = 0
    X_total = 0
    concat_components = equation.reactants + equation.products + equation.diluents
    included_components = (c for c in concat_components if not c.neglected)

    # Only add components that aren't neglected
    for component in included_components:
        cp_j: str = component.cp
        X_j: str = component.molWtFraction

        try: cp_j = float(component.cp)
        except ValueError: raise HTTPException(400, f"Cp is not numeric for {component.productName}")

        try: X_j = float(component.molWtFraction)
        except ValueError: raise HTTPException(400, f"molWtFraction is not numeric for {component.productName}")

        cp_mix += cp_j * X_j
        X_total += X_j

    # Rescaling
    cp_mix /= X_total

    return cp_mix
