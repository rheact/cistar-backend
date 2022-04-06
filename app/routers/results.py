import math
from fastapi import APIRouter
from helpers.units import conversions
from models import Equation, RheactState, ReactionCalculation, HMatrixColumn, CameoTable
from services.calculation_block.calculation_block import get_basis_molWtFraction
from services.cameo import get_cameo
from services.calculation_block import get_final_calculations, get_calculated_cp, get_basis_chemical
from services.hmatrix import max_h_plot

router = APIRouter()

@router.post('/calculate', response_model=ReactionCalculation)
def calculate(rstate: RheactState):
    operatingParams = rstate.operatingParams
    base = get_basis_chemical(rstate.compound, rstate.operatingParams.basis)
    baseMw = None
    if base is not None:
        baseMw = float(base.molWt)

    T = float(operatingParams.temperature)
    P = float(operatingParams.pressure)
    dH = float(operatingParams.heatOfReaction)

    # Standardise units
    T = conversions.std_T(T, operatingParams.temperatureUnit)
    P = conversions.std_P(P, operatingParams.pressureUnit)
    dH = conversions.std_dH(dH, operatingParams.heatOfReactionUnit, baseMw)

    # If user has not provided Cp mix, then we calculate based on mol fractions and individual Cps
    Cp = math.nan
    if operatingParams.cp == '' or operatingParams.cp == None:
        Cp = get_calculated_cp(rstate.compound)
    else:
        Cp = float(operatingParams.cp)
        # TODO: Unit conversions

    # Perform calculations
    cb = get_final_calculations(T, P, dH, Cp, base) 

    # Unstandardise units
    cb.adiabaticTemp = conversions.unstd_T(cb.adiabaticTemp, operatingParams.temperatureUnit)
    cb.finalTemp = conversions.unstd_T(cb.finalTemp, operatingParams.temperatureUnit)
    cb.adiabaticPressure = conversions.unstd_P(cb.adiabaticPressure, operatingParams.pressureUnit)
    return cb

@router.post('/graph', response_model=HMatrixColumn)
def matrix(hnums: str):
    return max_h_plot(hnums)

@router.post('/cameo', response_model=CameoTable)
def cameo(equation: Equation):
    data = [*equation.reactants, *equation.products, *equation.diluents]
    response = get_cameo(data)
    return response
