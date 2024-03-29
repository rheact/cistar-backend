from helpers.errors import InputDataError
from models import BaseChemicalIndex, Chemical, Equation

"""
    Retrieve the Chemical object for which the user intends to use its molecular weight as the current basis for the Heat of Reaction calculation.
"""
def get_basis_chemical(eq: Equation, basisIdx: BaseChemicalIndex) -> Chemical:
    # User wants to use total reaction mass
    if basisIdx.index == -1:
        return None

    assert basisIdx.list in ['reactants', 'products', 'diluents'], f"List specified is not in equation: {basisIdx.list}"

    # reactants
    if(basisIdx.list == 'reactants'):
        assert basisIdx.index < len(eq.reactants), f'Index out of bound for list {basisIdx.list}: {basisIdx.index}'
        return eq.reactants[basisIdx.index]

    # products
    if(basisIdx.list == 'products'):
        assert basisIdx.index < len(eq.products), f'Index out of bound for list {basisIdx.list}: {basisIdx.index}'
        return eq.products[basisIdx.index]

    # diluents
    assert basisIdx.index < len(eq.diluents), f'Index out of bound for list {basisIdx.list}: {basisIdx.index}'
    return eq.diluents[basisIdx.index]

"""
    Retrieve the molecular weight fraction of the chemical that is selected as the basis
"""
def get_basis_molWtFraction(base: Chemical) -> float:
    assert base is not None, "Basis is total reaction mass"

    try:
        X_i = float(base.molWtFraction)
    except TypeError:
        raise InputDataError(f'Mass fraction of {base.productName} shoule be a float: {base.molWtFraction} was given')

    if X_i > 1:
        raise InputDataError(f'Mass fraction of {base.productName} shoule not exceed 1: {base.molWtFraction} was given')

    if X_i <= 0:
        raise InputDataError(f'Mass fraction of {base.productName} should be greater than 0: {base.molWtFraction} was given')
    
    return X_i
