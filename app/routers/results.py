import math
from fastapi import APIRouter, HTTPException
from models import Equation, RheactState, ReactionCalculation
from services.cameo.crawler import get_cameo
from services.calculation_block import get_final_calculations, get_calculated_cp
from services.cameo.model import CameoTable
from services.hmatrix import max_h_plot, HMatrixColumn

router = APIRouter()

@router.post('/calculate', response_model=ReactionCalculation)
def calculate(rstate: RheactState):
    operatingParams = rstate.operatingParams

    d_h = float(operatingParams.heatOfReaction)
    T = float(operatingParams.temperature)
    P = float(operatingParams.pressure)
    cp = math.nan

    # If user has not provided Cp mix, then we calculate based on mol fractions and individual Cps
    if operatingParams.cp == '' or operatingParams.cp == None:
        cp = get_calculated_cp(rstate.compound)
    else:
        cp = float(operatingParams.cp)

    # TODO: Standardise units
    # TODO: This is done by checking the rstate unit configurations

    calculation_block = get_final_calculations(T, P, d_h, cp, rstate.operatingParams.basis, rstate.compound)

    # TODO: Unstandardise units
    # TODO: This is reverse transformation of above steps

    return calculation_block

@router.post('/graph', response_model=HMatrixColumn)
def matrix(hnums: str):
    try:
        return max_h_plot(hnums)
    except Exception as e:
        raise HTTPException(500, 'Unable to create H-Matrix: ' + str(e))

@router.post('/cameo', response_model=CameoTable)
def cameo(compound: Equation):
    data = list()
    for cls in [compound.reactants, compound.products, compound.diluents]:
        for c in cls:
            data.append(c)
    
    try:
        response = get_cameo(data)
        return response
    except Exception as e:
        raise HTTPException(500, 'Unable to create Cameo Table: ' + str(e))
