from helpers.errors import InputDataError
from models import BaseChemicalIndex, Chemical, Equation

def get_basis_chemical(eq: Equation, basisIdx: BaseChemicalIndex) -> Chemical:
    # User wants total reaction mass
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

def get_basis_molWtFraction(base: Chemical) -> float:
    assert base is not None, "Basis is total reaction mass"

    try:
        X_i = float(base.molWtFraction)
    except TypeError:
        raise InputDataError(f'Mol wt fraction of {base.productName} is not a float: {base.molWtFraction}')

    if X_i > 1:
        raise InputDataError(f'Mol wt fraction of {base.productName} is greater than 1: {base.molWtFraction}')
    
    return X_i
