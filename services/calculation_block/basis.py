from fastapi import HTTPException
from models import BaseChemicalIndex, Chemical, Equation

def get_basis_chemical(eq: Equation, basis: BaseChemicalIndex) -> Chemical:
    # User wants total reaction mass
    if basis is None or basis.index == -1:
        return None

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
