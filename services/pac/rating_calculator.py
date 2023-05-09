import pandas as pd
import re
import math
import numbers
from helpers.errors import InputDataError
from helpers.units import conversions
    
pacDf = pd.read_excel("data/pac_database3.xlsx")
chemDf = pd.read_excel("data/chem_data.xlsx")
hovDf = pd.read_excel("data/thor_hov_database.xlsx")

def get_row(casNo, df):
    """
    Sees if the chemical with a given cas exists in the table.
    returns the row if it does otherwise returns None 
    """
    row = df[df['CASRN'] == casNo]
    if len(row) == 0:
        return None
    return row

# Step 1: Calculate PAC Toxicity Rating
def PACToxicityRating(AQ, row, molecularWeight=1):
    PAC2 = float(row['PAC-2'].values[0])
    # Convert ppm to mg/m3
    # (X ppm)(molecular weight)/ 24.45
    unit = row['Units'].values[0]
    print('AQ ', AQ)
    print('PAC2 ', PAC2)
    if unit == 'ppm':
        PAC2 = (PAC2 * float(molecularWeight)) / 24.45
    return 655.1 * math.sqrt(float(AQ) / PAC2), PAC2

# Step 2: Calculate Airborne quantity (gas release), AQ_G
"""
Parameters:
    - Diameter of hole, D [=] mm
    - Absolute pressure (of the gas being considered), Pa [=] kPa 
        (Absolute pressure = gauge pressure + atmospheric pressure)
    - PA = Pg + 101.3 kPa
    - Molecular weight (of the gas being considered), MW [=] mol/g
    - Temperature (of the gas being considered), T [=] ºC
"""
def AQGas(pressure, pressureUnit, tempDegC, diameter, molecularWeight):
    # Convert temp & pressure to desired units
    originalPressureUnit = pressureUnit
    pressureUnit = re.search('^(.+?)\s\(.+?', pressureUnit) # Extract the unit before (Absolute)/(Gauge)
    if pressureUnit:
        pressureUnit = pressureUnit.group(1)

    gaugePressure = re.search('^.+(Gauge)', originalPressureUnit)
    if pressureUnit == 'psi':
        pressureUnit += 'g' if gaugePressure else 'a'

    pressureBar = conversions.std_P(float(pressure), pressureUnit) # Convert whatever unit to bars
    pressureKPa = conversions.unstd_P(pressureBar, 'kPa') # Convert bars to kPa

    if gaugePressure:
        pressureKPa = pressureKPa + 101.3 # the formula requires absolute pressure

    calculatedAQ = 4.751*math.pow(10, -6)*(float(diameter)**2)*pressureKPa*math.sqrt(float(molecularWeight) / (float(tempDegC) + 273))
    return calculatedAQ

# Step 3: Total airborne quantity (liquid release) AQ_L
"""
Parameters:
    - AQFlash: Airbone quantity from flash, kg/s - Step 5
    - AQPoolEvaporation: Airbone quantity from pool evaporation, kg/s - Step 4
    - liquidReleaseRate: liquid release rate, kg/s - Step 10
"""
def AQLiquid(AQFlash, AQPoolEvaporation, liquidReleaseRate):
    AQL = min(liquidReleaseRate, AQFlash + AQPoolEvaporation)
    return AQL

# Step 4: Airborne quantity from pool evaporation, AQ_p
"""
Parameters:
    - Pool area, AP [=] m2
    - Molecular weight (of liquid evaporating), MW [=] g/mol
    - Vapor pressure of the liquid at the characteristic pool temperature, Pv [=] kPa
    - Characteristic pool temperature, T [=] ºC
"""
def vaporFromPool(poolArea, molecularWeight, vaporPressurekPa, poolTemp):
    return 9*math.pow(10, -4)*(float(poolArea)**0.95)*(float(molecularWeight)*float(vaporPressurekPa) / (float(poolTemp) + 273))


# Step 5: Airborne quantity from flash (if operating T is less than normal boiling point)
"""
Parameters:
    - flashed fraction of liquid
    - liquid release rate, kg/s
"""
def AQFlash(liquidFlashedFraction, liquidReleaseRate):
    AQF = liquidReleaseRate if liquidFlashedFraction >= 0.2 else 5*liquidFlashedFraction*liquidReleaseRate
    return AQF

# Step 6: Liquid pool area
"""
Parameters:
    - total mass of liquid entering pool, kg
    - liquid density: kg/m^3
"""
def liquidPoolArea(totalMass, liquidDensity):
    return 100 * (1.0 * totalMass) / liquidDensity

# Step 7: Total mass of liquid entering pool
"""
Parameters:
    - Total liquid released, WT [=] kg
    - Flashed fraction of liquid, Fv [=] unitless
"""
def totalMassPool(liquidReleased, flashedFractionLiquid):
    return liquidReleased * (1 - 5 * flashedFractionLiquid)

# Step 8: Total liquid released
"""
Parameters:
    - Liquid release rate, L [=] kg/s
"""
def totalLiquidReleased(liquidReleaseRate):
    return 900 * liquidReleaseRate

# Step 9: Flashed fraction of liquid
"""
Parameters:
    - Heat capacity of liquid, Cp [=] J/kg/ºC
    - Heat of vaporization of liquid, Hv [=] J/kg
    - Operating temperature of liquid, Ts [=] ºC
    - Normal (1 atm) boiling point of liquid, Tb [=] ºC
"""
def flashedFraction(casNo, operatingTempDegC, molecularWeight, heatCapacity, HOV, boilingPoint):
    # row = get_row(casNo, chemDf)
    # assert row is not None, f'Unable to find CAS number {casNo} in the database. Please enter heat capacity of the liquid manually.'
    # Heat Capacity
    hc = heatCapacity
    
    if not hc:
        row = get_row(casNo, chemDf)
        assert row is not None, f'Unable to find CAS number {casNo} in the database. Please enter heat capacity of the liquid manually.'
        hcA = row['LiqCp_A'].values[0]
        hcB = row['LiqCp_B'].values[0]
        try:
            hcA = float(hcA)
        except:
            hcA = math.nan
        
        try:
            hcB = float(hcB)
        except:
            hcB = math.nan

        assert not math.isnan(hcA) and not math.isnan(hcB), f'Unable to calculate heat capacity for {casNo}. Please enter heat capacity of the liquid manually.'
        hc = hcA + hcB * float(operatingTempDegC)
        # Unit conversion
        hc = hc * 4.1868 * 1000

    # Heat of vaporization
    hov = HOV
    if not hov:
        hovRow = get_row(casNo, hovDf)
        assert hovRow is not None, f"Unable to find CAS number {casNo} in the database. Please enter heat of vaporization of liquid manually."
        hov = hovRow['Heat of Vaporization'].values[0] # unit: kj/mol

        # Convert kj/mol to j/kg
        hov = 1000 * 1000 * (float(hov) / float(molecularWeight))
    
    tempDiff = float(operatingTempDegC) - float(boilingPoint)
    flashedFraction = (float(hc) / float(hov)) * tempDiff if tempDiff >= 0 else 0
    flashedFraction = min(flashedFraction, 1)
    return flashedFraction, hc, hov


# Step 10: Liquid release rate
"""
Parameters:
    - Gauge pressure (in volume where liquid is stored), Pg [=] kPa
    - Liquid density, p [=] kg/m3
    - Height of liquid above release point, ∆h [=] m
    - Diameter of hole liquid is releasing through, D [=] mm
"""
def liquidReleaseRate(pressure, pressureUnit, density, liquidHeight, diameter):
    # Convert pressure to desired units
    originalPressureUnit = pressureUnit
    pressureUnit = re.search('^(.+?)\s\(.+?', pressureUnit) # Extract the unit before (Absolute)/(Gauge)
    if pressureUnit:
        pressureUnit = pressureUnit.group(1)

    absPressure = re.search('^.+(Absolute)', originalPressureUnit)
    if pressureUnit == 'psi':
        pressureUnit += 'a' if absPressure else 'g'
    
    pressureBar = conversions.std_P(float(pressure), pressureUnit) # Convert whatever unit to bars
    pressureKPa = conversions.unstd_P(pressureBar, 'kPa') # Convert bars to kPa

    if absPressure:
        pressureKPa = pressureKPa - 101.3 # the formula requires gauge pressure
    
    liquidReleaseRate = 9.44*math.pow(10, -7)*(float(diameter)**2)*density*math.sqrt((1000 * float(pressureKPa)) / (density) + 9.8 * float(liquidHeight))
    return liquidReleaseRate


def liquid_density(casNo, operatingTemp, operatingTempUnit):
    pacRow = get_row(casNo, pacDf)

    pacDensity = None
    if pacRow is not None:
        specificGravity = pacRow['Specific Gravity'].values[0]

        if specificGravity and ((isinstance(specificGravity, float) and not math.isnan(specificGravity)) or isinstance(specificGravity, str)):
            state = pacRow['State'].values[0]
            pacDensity = "According to PAC database Rev 29A, state at 25°C is "+str(state)+", specific gravity at 25°C unless indicated is "+str(specificGravity)
            # Specific Gravity @25C unless indicated
            # sg = str(specificGravity).split('@')[0] # extract the number before '@'
            # sg = re.findall(r'\d+.?\d*', sg)[0]
            # pacDensity = float(sg) * 997
    
    # Calculate density using the formula in chem_data
    chemDensity = None
    chemRow = get_row(casNo, chemDf)
    if chemRow is not None:
        denA = chemRow['LiqDen_A'].values[0]
        denB = chemRow['LiqDen_B'].values[0]
        try:
            denA = float(denA)
        except:
            denA = math.nan
        
        try:
            denB = float(denB)
        except:
            denB = math.nan

        if not math.isnan(denA) and not math.isnan(denB):
            try:
                operatingTemp = float(operatingTemp)
                operatingTempDegC = conversions.std_T(operatingTemp, operatingTempUnit)
                chemDensity = (denA - denB * operatingTempDegC) * 1000
            except:
                chemDensity = None

    if chemDensity is not None:
        chemDensity = str(chemDesity)
        chemDensity = "Liquid density calculted based on RAST Chem Table: "+chemDensity+" kg/m3"     

    # density = ''
    # source = ''
    # if pacDensity is not None:
    #     density = str(pacDensity)
    #     source = "Liquid density from PAC database: "+density+" kg/m3"
    # else:
    #     if chemDensity is not None:
    #         density = str(chemDesity)
    #         source = "Liquid density calculted RAST Chem Table: "+density+" kg/m3"
    if (pacDensity is not None and chemDensity is not None):
        return pacDensity, chemDensity
    
    return pacDensity or chemDensity


def liquid_vapor_pressure(casNo, vaporTemplateSDS, operatingTemp, operatingTempUnit):
    row = get_row(casNo, pacDf)
    assert row is not None, f'No record in the database.'
    
    vaporPressure = row['Vapor  Pressure'].values[0]
    vaporPressureTemp = row['Vapor  Pressure Temperature'].values[0]
    vaporTemplate = 'No record in the database.'

    try:
        vaporPressure = float(vaporPressure)
    except:
        vaporPressure = math.nan
    
    try:
        vaporPressureTemp = float(vaporPressureTemp)
    except:
        vaporPressureTemp = math.nan

    if math.isnan(vaporPressure) or math.isnan(vaporPressureTemp):
        # Calculate from chem_data.xlsx
        row = get_row(casNo, chemDf)
        assert row is not None and operatingTemp, 'No record in the database.'
        
        operatingTempDegC = conversions.std_T(float(operatingTemp), operatingTempUnit)
        vpA = row['VP_A'].values[0]
        vpB = row['VP_B'].values[0]
        vpC = row['VP_C'].values[0]
        try:
            vpA = float(vpA)
        except:
            vpA = math.nan
        
        try:
            vpB = float(vpB)
        except:
            vpB = math.nan

        try:
            vpC = float(vpC)
        except:
            vpC = math.nan
        assert not math.isnan(vpA) and not math.isnan(vpB) and not math.isnan(vpC), 'No record in the database.'
        vp = math.exp(float(vpA) - float(vpB) / (float(operatingTempDegC) + 273.16 - float(vpC))) # unit is atm
        # Convert vp in atm to bars
        vpBars = conversions.std_P(vp, 'atm')
        # Convert vp in bars to kPa
        vpkPa = conversions.unstd_P(vpBars, 'kPa')
        vaporTemplate = f'Vapor pressure is {vpkPa} kPa at {operatingTempDegC} degree(s) Celsius.'
    else:
        vaporTemplate = f'Vapor pressure is {vaporPressure} mmHg at {vaporPressureTemp} degree(s) Celsius.'
    
    return vaporTemplate


def calculate_pac_rating(casNo, AQ, typeOfRelease, temp, tempUnit, pressure, pressureUnit, diameter, MW, liquidDensity, liquidHeight, userBoilingPoint, heatCapacity, HOV, vaporPressure, vaporPressureUnit, dikedArea, totalAmount):
    row = get_row(casNo, pacDf)
    assert row is not None, f'Unable to find CAS number {casNo} in the database.'
    
    # Try to get molecular weight from PAC. If not available, use molecular weight from SDS or user provided.
    molecularWeight = row['Molecular Weight'].values[0]
    try:
        molecularWeight = float(molecularWeight)
    except:
        molecularWeight = math.nan

    if math.isnan(molecularWeight):
        molecularWeight = MW

    assert molecularWeight, f'Unable to find molecular weight for {casNo} in the database. Please enter its molecular weight manually.'

    # Known AQ -> Step 1
    if AQ:
        rating, pac2 = PACToxicityRating(AQ, row, molecularWeight)
        return rating, pac2, molecularWeight, 'N/A', 'N/A', 'N/A'

    tempDegC = conversions.std_T(float(temp), tempUnit) # Convert whatever unit to degC

    # Unknown AQ -> Type of Release 'Gas' -> Step 2: Calculate AQ_G -> Step 1
    if typeOfRelease == 'Gas':
        AQ_G = AQGas(pressure, pressureUnit, tempDegC, diameter, molecularWeight)
        rating, pac2 = PACToxicityRating(AQ_G, row, molecularWeight)
        return rating, pac2, molecularWeight, 'N/A', 'N/A', 'N/A'

    # Unknown AQ -> Type of Release 'Liquid'
    if typeOfRelease == 'Liquid':
    
        assert liquidDensity, f'Please enter the liquid density.'
        # Step 10: liquid release rate
        releaseRate = liquidReleaseRate(pressure, pressureUnit, float(liquidDensity), liquidHeight, diameter)

        liquidReleased = None
        if totalAmount:
            liquidReleased = float(totalAmount) # the release took less than 15mins, so we use total amount of liquid in the container
        else:
            # Step 8: Total liquid released
            liquidReleased = totalLiquidReleased(releaseRate)

        # Boiling Point
        # check PAC
        boilingPoint = None
        bpPAC = row['Boiling Point'].values[0]
            
        if (isinstance(bpPAC, numbers.Number) and math.isnan(bpPAC)) or (isinstance(bpPAC, str) and bpPAC.includes('@')):
            # check SDS
            boilingPoint = userBoilingPoint
        else:
            # range
            bps = re.findall(r'(-?\d+.?\d*)-(-?\d+.?\d*)', str(bpPAC))
            if len(bps) == 2:
                boilingPoint = bps[1] # use the bigger value
            else:
                # single value
                boilingPoint = re.findall(r'-?\d+.?\d*', str(bpPAC))[0]
                
        assert boilingPoint, f'Please enter boiling point of the liquid.'

        if tempDegC < float(boilingPoint):
            
            # Step 7: Total mass
            totalMass = totalMassPool(liquidReleased, 0)

            # Step 6: Pool area
            poolArea = dikedArea if dikedArea else liquidPoolArea(totalMass, float(liquidDensity))

            # Step 4: AQ_P
            # Convert vapor pressure to bars
            vaporPressureBars = conversions.std_P(float(vaporPressure), vaporPressureUnit)

            # Convert vapor pressure in bars to kPa
            vaporPressurekPa = conversions.unstd_P(vaporPressureBars, 'kPa')
            poolTempDegC = float(boilingPoint) if float(tempDegC) > float(boilingPoint) else tempDegC
            AQPool = vaporFromPool(poolArea, molecularWeight, vaporPressurekPa, poolTempDegC)

            # Step 3: AQ_L
            AQ_L = AQLiquid(0, AQPool, releaseRate)
            rating, pac2 = PACToxicityRating(AQ_L, row, molecularWeight)
            return rating, pac2, molecularWeight, boilingPoint, 'N/A', 'N/A'
        
        else:

            # Step 9: Flashed fraction of the liquid
            flashedFractionLiquid, heatCapacity, HOV = flashedFraction(casNo, tempDegC, molecularWeight, heatCapacity, HOV, boilingPoint)

            # Step 5: AQ_F
            AQ_F = AQFlash(flashedFractionLiquid, releaseRate)

            if flashedFractionLiquid < 0.02:
                # Not all liquid flashed
                # Step 7: Total mass
                totalMass = totalMassPool(liquidReleased, flashedFractionLiquid)

                # Step 6: Pool area
                poolArea = dikedArea if dikedArea else liquidPoolArea(totalMass, float(liquidDensity))

                # Step 4: AQ_P
                # Convert vapor pressure to bars
                vaporPressureBars = conversions.std_P(float(vaporPressure), vaporPressureUnit)

                # Convert vapor pressure in bars to kPa
                vaporPressurekPa = conversions.unstd_P(vaporPressureBars, 'kPa')
                poolTempDegC = float(boilingPoint) if float(tempDegC) > float(boilingPoint) else tempDegC
                AQPool = vaporFromPool(poolArea, molecularWeight, vaporPressurekPa, poolTempDegC)

                # Step 3: AQ_L
                AQ_L = AQLiquid(AQ_F, AQPool, releaseRate)
                rating, pac2 = PACToxicityRating(AQ_L, row, molecularWeight)
                return rating, pac2, molecularWeight, boilingPoint, heatCapacity, HOV

            else:
                rating, pac2 = PACToxicityRating(AQ_F, row, molecularWeight)
                return rating, pac2, molecularWeight, boilingPoint, heatCapacity, HOV
