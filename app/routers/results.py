import math
import helpers.units.conversions as U
from fastapi import APIRouter
from models import Equation, RheactState, ReactionCalculation, HMatrixColumn, CameoTable, MOCHMatrix
from services.cameo import get_cameo
from services.calculation_block import get_final_calculations, get_calculated_cp, get_basis_chemical
from services.hmatrix import max_h_plot
from services.pac import calculate_pac_rating, liquid_vapor_pressure, liquid_density, liquidReleaseRate, getPACMolecularWeight, getBoilingPoint, getRASTLiqCp, getHOV
from services.heat_of_formation import calculate_heat_of_reaction
from services.moc import get_moc_hmatrix

router = APIRouter()

"""
    Calculate adiabatic_temp, final_temp, and adiabatic_pressure of the reaction
"""
@router.post('/calculate', response_model=ReactionCalculation)
def calculate(rstate: RheactState):
    params = rstate.operatingParams

    assert params.temperature != '', "Temperature is missing"
    assert params.pressure != '', "Pressure is missing"
    assert params.heatOfReaction != '', "Heat of Reaction is missing"

    # If base is None, that mean user wants to use total reaction mass
    base = get_basis_chemical(rstate.compound, rstate.operatingParams.basis)
    baseMw = None
    if base is not None:
        try:
            baseMw = float(base.molWt)
        except ValueError:
            raise AssertionError(f"Molecular weight of for {base.productName} heat of reaction is not a number. ")

    T = float(params.temperature)
    P = float(params.pressure)
    dH = float(params.heatOfReaction)

    # Standardise units
    T = U.std_T(T, params.temperatureUnit)
    assert T > -273.15, "Temperature is absolute zero!"
    P = U.std_P(P, params.pressureUnit)
    dH = U.std_dH(dH, params.heatOfReactionUnit, baseMw)

    # If user has not provided Cp mix, then we calculate it based on mol fractions and individual Cps
    Cp = math.nan
    if params.cp == '' or params.cp == None:
        Cp = get_calculated_cp(rstate.compound, base)
    else:
        Cp = float(params.cp)
        Cp = U.std_Cp(Cp, params.cpUnit, baseMw)
    assert Cp > 0, f"Mixture heat capacity is required to be greater than zero. The current value is {Cp} cal/g/C"

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

"""
    Generate one row for the hazard matrix based on the given list of h-indices
"""
@router.post('/graph', response_model=HMatrixColumn)
def matrix(hnums: str):
    return max_h_plot(hnums)

@router.post('/cameo', response_model=CameoTable)
def cameo(equation: Equation):
    data = [*equation.reactants, *equation.products, *equation.diluents]
    response = get_cameo(data)
    return response

@router.post('/heatOfFormation')
def heatOfFormation(casNo: str, phase: str, numberOfMoles: str):
    return calculate_heat_of_reaction(casNo, phase, numberOfMoles)

@router.post('/pac')
def pac(casNo: str, AQ: str, typeOfRelease: str, opTemp: str, opTempUnit: str, pressure: str, pressureUnit: str, diameter: str, molecularWeight: str, density: str, liquidHeight: str, boilingPoint: str, heatCapacity: str, HOV: str, vaporPressure: str, vaporPressureUnit: str, dikedArea: str, totalAmount: str):
    rating = calculate_pac_rating(casNo, AQ, typeOfRelease, opTemp, opTempUnit, pressure, pressureUnit, diameter, molecularWeight, density, liquidHeight, boilingPoint, heatCapacity, HOV, vaporPressure, vaporPressureUnit, dikedArea, totalAmount)
    roundedRating = round(rating, 3)
    return roundedRating

@router.post('/vaporPressure')
def vaporPressure(casNo: str, opTemp: str, opTempUnit: str, boilingPoint: str):
    return liquid_vapor_pressure(casNo, opTemp, opTempUnit, boilingPoint)

@router.post('/liquidDensity')
def liquidDensity(casNo: str, liquidTemp: str, liquidTempUnit: str):
    return liquid_density(casNo, liquidTemp, liquidTempUnit)

@router.post('/liquidReleaseRate')
def getLiquidReleaseRate(pressure: str, pressureUnit: str, density: str, liquidHeight: str, diameter: str):
    return liquidReleaseRate(float(pressure), pressureUnit, float(density), float(liquidHeight), float(diameter))

@router.post('/pacMW')
def getPACMW(casNo: str):
    return getPACMolecularWeight(casNo)

@router.post('/boilingPoint')
def getBP(casNo):
    return getBoilingPoint(casNo)

@router.post('/liqHeatCapacity')
def getLiqCp(casNo, opTemp, boilingPoint):
    return getRASTLiqCp(casNo, opTemp, boilingPoint)

@router.post('/liqHOV')
def getPACHOV(casNo, molecularWeight, boilingPoint):
    return getHOV(casNo, molecularWeight, boilingPoint)

@router.post('/mocHmatrix', response_model=MOCHMatrix)
def mocHmatrix(hNumsMap):
    return get_moc_hmatrix(hNumsMap)