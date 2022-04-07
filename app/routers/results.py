import math
from fastapi import APIRouter
import helpers.units.conversions as U
from models import Equation, RheactState, ReactionCalculation, HMatrixColumn, CameoTable
from services.cameo import get_cameo
from services.calculation_block import get_final_calculations, get_calculated_cp, get_basis_chemical
from services.hmatrix import max_h_plot

router = APIRouter()

@router.post('/calculate', response_model=ReactionCalculation)
def calculate(rstate: RheactState):
    params = rstate.operatingParams
    assert params.temperature != '', "Temperature is missting"
    assert params.pressure != '', "Pressure is missting"
    assert params.heatOfReaction != '', "Heat of Reaction is missting"

    base = get_basis_chemical(rstate.compound, rstate.operatingParams.basis)
    baseMw = None
    if base is not None:
        baseMw = float(base.molWt)

    T = float(params.temperature)
    P = float(params.pressure)
    dH = float(params.heatOfReaction)

    # Standardise units
    T = U.std_T(T, params.temperatureUnit)
    P = U.std_P(P, params.pressureUnit)
    dH = U.std_dH(dH, params.heatOfReactionUnit, baseMw)

    # If user has not provided Cp mix, then we calculate based on mol fractions and individual Cps
    Cp = math.nan
    if params.cp == '' or params.cp == None:
        Cp = get_calculated_cp(rstate.compound)
    else:
        Cp = float(params.cp)
        Cp = U.std_Cp(Cp, params.cpUnit, baseMw)

    # Perform calculations
    res = get_final_calculations(T, P, dH, Cp, base) 
    
    # Display strings of results
    display_final_T = round(U.unstd_T(res.finalTemp, params.temperatureUnit), 3)
    res.finalTempDisplay = f"{display_final_T} {params.temperatureUnit}"

    display_ad_P = round(U.unstd_P(res.adiabaticPressure, params.pressureUnit), 3)
    res.adiabaticPressureDisplay = f"{display_ad_P} {params.pressureUnit}"

    if params.temperatureUnit == '°F':
        display_ad_T = 1.8 * res.adiabaticTemp
    else:
        display_ad_T = res.adiabaticTemp
    display_ad_T = round(display_ad_T, 3)
    
    res.adiabaticTempDisplay = f"{display_ad_T} {params.temperatureUnit}"

    return res

@router.post('/graph', response_model=HMatrixColumn)
def matrix(hnums: str):
    return max_h_plot(hnums)

@router.post('/cameo', response_model=CameoTable)
def cameo(equation: Equation):
    data = [*equation.reactants, *equation.products, *equation.diluents]
    response = get_cameo(data)
    return response
