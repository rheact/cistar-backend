from fastapi import APIRouter, HTTPException
from models.rheact_state import RheactState
from services.cameo.crawler import get_cameo
from services.calculation_block import calculate_cp_mix, calculate_without_cp_mix, ReactionCalculation
from services.cameo.model import CameoTable
from services.hmatrix import max_h_plot, HMatrixColumn

router = APIRouter()

@router.post('/calculate', response_model=ReactionCalculation)
def calculate(rstate: RheactState):
    operatingParams = rstate.operatingParams
    reactants = rstate.compound.reactants
    products = rstate.compound.products
    heat_of_reaction = float(operatingParams.heatOfReaction)
    temperature = float(operatingParams.temperature)
    pressure = float(operatingParams.pressure)
    try:
        if operatingParams.cp != '':
            cp = float(operatingParams.cp)
            calculation_block = calculate_cp_mix(heat_of_reaction, cp, temperature, pressure)
        else:
            calculation_block = calculate_without_cp_mix(reactants, products, heat_of_reaction, temperature, pressure)
    except Exception as e:
        raise HTTPException(500, 'Unable to compute calculation block: ' + str(e))

    return calculation_block

@router.post('/graph', response_model=HMatrixColumn)
def matrix(hnums: str):
    try:
        return max_h_plot(hnums)
    except Exception as e:
        raise HTTPException(500, 'Unable to create H-Matrix: ' + str(e))

@router.post('/cameo', response_model=CameoTable)
def cameo(rstate: RheactState):
    data = list()
    for cls in [rstate.compound.reactants, rstate.compound.products, rstate.compound.diluents]:
        for c in cls:
            data.append(c)
    
    try:
        response = get_cameo(data)
        return response
    except Exception as e:
        raise HTTPException(500, 'Unable to create Cameo Table: ' + str(e))
