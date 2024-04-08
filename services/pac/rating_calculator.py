import pandas as pd
import re
import math
import numbers
from helpers.units import conversions
    
pacDf = pd.read_excel("data/pac_database3.xlsx")
chemDf = pd.read_excel("data/chem_data.xlsx")
hovDf = pd.read_excel("data/thor_hov_database.xlsx")

"""
    Checks if the chemical with a given cas exists in the table.
    returns the row if it does otherwise returns None 
"""
def get_row(casNo, df):
    row = df[df['CASRN'] == casNo]
    if len(row) == 0:
        return None
    return row

# Step 1: Calculate PAC Toxicity Rating
"""
Parameters:
    - Airborne quantity, AQ (kg/s)
        - Airborne quantity has two sources:
            - Gas release (AQ_G) (Step 2)
            - Gas from (pool) evaporation (AQ_P) (Steps 3 through 9)
    - Corresponding row from the database
    - Molecular weight (default value is 1)

Outputs:
    - PAC
    - PAC-2
"""
def PACToxicityRating(AQ, row, molecularWeight=1):
    PAC2 = float(row['PAC-2'].values[0])

    unit = row['Units'].values[0]

    # Convert PAC-2 from ppm to mg/m3
    # (X ppm)*(molecular weight)/ 24.45
    if unit == 'ppm':
        PAC2 = (PAC2 * float(molecularWeight)) / 24.45

    return round(655.1 * math.sqrt(float(AQ) / PAC2))

# Step 2: Calculate airborne quantity (gas release), AQ_G
"""
Parameters:
    - Diameter of hole (mm) - User Input
    - Absolute pressure (of the gas being considered) (kPa) - User Input
        (Absolute pressure (Pa) = gauge pressure (Pg) + atmospheric pressure)
        Pa = Pg + 101.3 kPa
    - Molecular weight (of the gas being considered), MW (mol/g)
    - Temperature (of the gas being considered) (ºC)

Output:
    - AQ_G (kg/s)
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

# Step 3: Calculate total airborne quantity (liquid release) AQ_L
"""
Parameters:
    - AQFlash: Airbone quantity from flash (AQ_F) (kg/s) - Step 5
    - AQPoolEvaporation: Airbone quantity from pool evaporation,(AQ_P) (kg/s) - Step 4
    - liquidReleaseRate: liquid release rate (kg/s) - Step 10

Output:
    - Airborne quantity (liquid release) AQ_L (kg/s)
"""
def AQLiquid(AQFlash, AQPoolEvaporation, liquidReleaseRate):
    AQL = min(liquidReleaseRate, AQFlash + AQPoolEvaporation)
    return AQL

# Step 4: Calculate airborne quantity from pool evaporation, AQ_p
"""
Parameters:
    - Pool area, AP [=] m2
    - Molecular weight (of liquid evaporating), MW [=] g/mol
    - Vapor pressure of the liquid at the characteristic pool temperature, Pv [=] kPa
    - Characteristic pool temperature, T [=] ºC
"""
def vaporFromPool(poolArea, molecularWeight, vaporPressurekPa, poolTemp):
    return 9*math.pow(10, -4)*(float(poolArea)**0.95)*(float(molecularWeight)*float(vaporPressurekPa) / (float(poolTemp) + 273))


# Step 5: Calculate airborne quantity from flash (if operating temperature is less than normal boiling point)
"""
Parameters:
    - Flashed fraction of liquid
    - Liquid release rate (kg/s)

Output:
    - Airborne quantity from flash, AQ_F (kg/s)
"""
def AQFlash(liquidFlashedFraction, liquidReleaseRate):
    AQF = liquidReleaseRate if liquidFlashedFraction >= 0.2 else 5*liquidFlashedFraction*liquidReleaseRate
    return AQF

# Step 6: Calcualte liquid pool area
"""
Parameters:
    - total mass of liquid entering pool (kg)
    - liquid density (kg/m^3)

Output:
    - Liquid pool area (m^2)
"""
def liquidPoolArea(totalMass, liquidDensity):
    return 100 * (1.0 * totalMass) / liquidDensity

# Step 7: Calcualte total mass of liquid entering pool
"""
Parameters:
    - Total liquid released (kg)
    - Flashed fraction of liquid

Output:
    - Total mass of liquid entering pool (kg)
"""
def totalMassPool(liquidReleased, flashedFractionLiquid):
    return liquidReleased * (1 - 5 * flashedFractionLiquid)

# Step 8: Calculate total liquid released
"""
Parameters:
    - Liquid release rate (kg/s)

Output:
    - Total liquid released (kg)
"""
def totalLiquidReleased(liquidReleaseRate):
    return 900 * liquidReleaseRate

# Step 9: Flashed fraction of liquid
"""
Parameters:
    - Heat capacity of liquid (J/kg/ºC)
    - Heat of vaporization of liquid (J/kg)
    - Operating temperature of liquid (ºC)
    - Normal (1 atm) boiling point of liquid (ºC)

Output:
    - Flashed fraction of liquid (unitless)
"""
def flashedFraction(operatingTempDegC, heatCapacity, HOV, boilingPoint):
    ratio = 0.005
    if heatCapacity and HOV:
        ratio = float(heatCapacity) / float(HOV)

    tempDiff = float(operatingTempDegC) - float(boilingPoint)
    flashedFraction = ratio * tempDiff if tempDiff >= 0 else 0
    flashedFraction = min(flashedFraction, 1)

    return flashedFraction


# Step 10: Calcualte liquid release rate
"""
Parameters:
    - Gauge pressure (in volume where liquid is stored) (kPa)
    - Liquid density (kg/m3)
    - Height of liquid above release point (m)
    - Diameter of hole liquid is releasing through (mm)

Output:
    - Liquid release rate (kg/s)
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

    # If user provides absolute pressure, then needs to convert it to gauge pressure
    # Absolute pressure (Pa) = gauge pressure (Pg) + atmospheric pressure
    if absPressure:
        pressureKPa = pressureKPa - 101.3 
    
    liquidReleaseRate = 9.44*math.pow(10, -7)*(float(diameter)**2)*float(density)*math.sqrt((1000 * float(pressureKPa)) / float(density) + 9.8 * float(liquidHeight))
    return liquidReleaseRate

"""
    Fetch liquid density from both PAC and CHEM databases
"""
def liquid_density(casNo, operatingTemp, operatingTempUnit):
    # Calculate density using specific gravity from PAC database
    pacRow = get_row(casNo, pacDf)

    pacDensity = None
    if pacRow is not None:
        specificGravity = pacRow['Specific Gravity'].values[0]

        if specificGravity and ((isinstance(specificGravity, float) and not math.isnan(specificGravity)) or isinstance(specificGravity, str)):
            state = pacRow['State'].values[0]
            pacDensity = "According to PAC database Rev 29A, state at 25°C is "+str(state)+", specific gravity at 25°C unless indicated is "+str(specificGravity)
    
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
        chemDensity = str(chemDensity)
        chemDensity = chemDensity+" kg/m3"     

    if (pacDensity is not None and chemDensity is not None):
        return pacDensity, chemDensity
    
    return pacDensity or chemDensity

"""
    Fetch liquid vapor pressure from PAC or CHEM database
"""
def liquid_vapor_pressure(casNo, operatingTemp, operatingTempUnit, boilingPoint):

    # Get the liquid vapor pressure from the PAC database
    pacRow = get_row(casNo, pacDf)
    rastRow = get_row(casNo, chemDf)
    
    pacVP = "No record in the database."
    pacVPTemp = ''
    rastVP = "No record in the database."
    rastVPTemp = ''
    
    if pacRow is not None:
        pacVP = pacRow['Vapor  Pressure'].values[0]
        pacVPTemp = pacRow['Vapor  Pressure Temperature'].values[0]
    
    if rastRow is not None:
        operatingTempDegC = conversions.std_T(float(operatingTemp), operatingTempUnit)
        boilingPoint = float(boilingPoint)
        poolTemp = operatingTempDegC if operatingTempDegC <= boilingPoint else boilingPoint
        vpA = rastRow['VP_A'].values[0]
        vpB = rastRow['VP_B'].values[0]
        vpC = rastRow['VP_C'].values[0]

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
        
        if not math.isnan(vpA) and not math.isnan(vpB) and not math.isnan(vpC):
            rastVP = math.exp(float(vpA) - float(vpB) / (float(poolTemp) + 273.16 - float(vpC))) # unit is atm
            rastVP = conversions.std_P(rastVP, 'atm') # Convert vp in atm to bars
            rastVP = conversions.unstd_P(rastVP, 'kPa') # Convert vp in bars to kPa
            rastVPTemp = poolTemp

    return pacVP, pacVPTemp, round(rastVP, 1), rastVPTemp

def getPACMolecularWeight(casNo):
    row = get_row(casNo, pacDf)
    if row is None:
        return "Unable to find the chemical in PAC database"
    
    PAC2 = float(row['PAC-2'].values[0])

    molecularWeight = row['Molecular Weight'].values[0]

    unit = row['Units'].values[0]

    # Convert PAC-2 from ppm to mg/m3
    # (X ppm)*(molecular weight)/ 24.45
    # if unit == 'ppm':
    #     PAC2 = (PAC2 * float(molecularWeight)) / 24.45

    return molecularWeight, PAC2, unit

def getBoilingPoint(casNo):
    rowPAC = get_row(casNo, pacDf)
    rowRAST = get_row(casNo, chemDf)

    bpPAC = "Unable to find the chemical in PAC database"
    bpRAST = "Unable to find the chemical in RAST database"
    if rowPAC is not None:
        bpPAC = rowPAC['Boiling Point'].values[0]
        if not (isinstance(bpPAC, numbers.Number) and math.isnan(bpPAC)) or (isinstance(bpPAC, str) and bpPAC.includes('@')):
            # deal with range
            bps = re.findall(r'(-?\d+.?\d*)-(-?\d+.?\d*)', str(bpPAC))
            if len(bps) == 2:
                bpPAC = bps[1] # use the bigger value in the range
            else:
                # single value
                bpPAC = re.findall(r'-?\d+.?\d*', str(bpPAC))[0]

    if rowRAST is not None:
        bpRAST = rowRAST['Boiling Point (deg C)'].values[0]
        # bpRAST = round(float(bpRAST), 1)

    return bpPAC, bpRAST

def getRASTLiqCp(casNo, opTemp, boilingPoint):
    row = get_row(casNo, chemDf)
    if row is None:
        return "Unable to calculate heat capacity from RAST."
    
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

    if math.isnan(hcA) or math.isnan(hcB):
        return "Unable to calculate heat capacity from RAST."
    
    temp = (float(opTemp) + float(boilingPoint)) / 2
    hc = hcA + hcB * temp
    # Unit conversion
    hc = hc * 4184 # J/kg/C
    return round(hc)

def getHOV(casNo, molecularWeight, boilingPoint):
    hovRow = get_row(casNo, hovDf)
    rastRow = get_row(casNo, chemDf)
    hovHOV = "Unable to calculate HOV"
    rastHOV = "Unable to calculate HOV"
    if hovRow is not None:
        hovHOV = hovRow['Heat of Vaporization'].values[0] # unit: kj/mol
        hovHOV = 1000000 * (float(hovHOV) / float(molecularWeight))  # Convert kj/mol to j/kg
    if rastRow is not None:
        hovA = rastRow['dHv_A'].values[0]
        hovB = rastRow['dHv_B'].values[0]
        hovC = rastRow['dHv_C'].values[0]
        if (isinstance(hovA, numbers.Number) and math.isnan(hovA)) or (isinstance(hovB, numbers.Number) and math.isnan(hovB)) or (isinstance(hovC, numbers.Number) and math.isnan(hovC)):
            return hovHOV, rastHOV
        boilingPoint = float(boilingPoint)
        rastHOV = float(hovA) - float(hovB) * boilingPoint - float(hovC) * boilingPoint * boilingPoint
        rastHOV = rastHOV * 4184

    return round(hovHOV, 1), round(rastHOV, 1)


"""
Parameters:
    - CAS number
    - Airborne quantity
    - Type of release
    - Operating temperature
    - Operating pressure
    - Diameter of hole liquid is releasing through
    - Molecular weight
    - Liquid density
    - Height of liquid above release point
    - Boiling point
    - Heat capacity
    - Heat of vaporization
    - Vapor pressure
    - Diked area
    - Total amount of liquid in the container

Outputs:
    - PAC toxicity rating
    # - PAC-2
    # - Molecular weight (g/mol)
    # - Boiling point (ºC) 
    # - Heat capacity (j/kg/ºC)
    # - Heat of vaporization (j/kg)
"""
def calculate_pac_rating(casNo, AQ, typeOfRelease, opTemp, opTempUnit, pressure, pressureUnit, diameter, molecularWeight, liquidDensity, liquidHeight, boilingPoint, heatCapacity, HOV, vaporPressure, vaporPressureUnit, dikedArea, totalAmount):
    row = get_row(casNo, pacDf)
    assert row is not None, f'Unable to find CAS number {casNo} in the database.'
    
    molecularWeight = float(molecularWeight)
    # Known AQ -> Step 1: Calculate PAC toxicity rating
    if AQ:
        rating = PACToxicityRating(AQ, row, molecularWeight)
        return rating
    
    opTempDegC = conversions.std_T(float(opTemp), opTempUnit) # Convert whatever unit to degC

    # Unknown AQ -> Type of Release 'Gas' -> Step 2: Calculate AQ_G -> Step 1: Calculate PAC toxicity rating
    if typeOfRelease == 'Gas':
        AQ_G = AQGas(pressure, pressureUnit, opTempDegC, diameter, molecularWeight)
        rating = PACToxicityRating(AQ_G, row, molecularWeight)
        return rating

    # Unknown AQ -> Type of Release 'Liquid'
    if typeOfRelease == 'Liquid':

        # Step 10: Calcualte liquid release rate
        releaseRate = liquidReleaseRate(pressure, pressureUnit, liquidDensity, liquidHeight, diameter)

        liquidReleased = None
        if totalAmount:
            liquidReleased = float(totalAmount) # the release took less than 15 mins, so we use total amount of liquid in the container
        else:
            # Step 8: Calcualte total liquid released
            liquidReleased = totalLiquidReleased(releaseRate)

        # If operating temperature (opTempDegC) < normal boiling point: Step 7 -> Step 6 -> Step 4 -> Step 3 -> Step 1
        if opTempDegC < float(boilingPoint):
            
            # Step 7: Calculate total mass
            totalMass = totalMassPool(liquidReleased, 0)

            # Step 6: Calculate pool area
            # If liquid release is into a diked area of sufficient size, the pool size is set equal to the diked area
            poolArea = dikedArea if dikedArea else liquidPoolArea(totalMass, float(liquidDensity))

            # Step 4: Calculate airborne quality from pool evaporation (AQ_P)
            # Convert vapor pressure to bars
            vaporPressureBars = conversions.std_P(float(vaporPressure), vaporPressureUnit)

            # Convert vapor pressure in bars to kPa
            vaporPressurekPa = conversions.unstd_P(vaporPressureBars, 'kPa')

            # Calcualte characteristic pool temperature (ºC)
            # If operating temperature (temDegC) > boiling point, then use operating temperature
            # Otherwise use boiling point
            poolTempDegC = float(boilingPoint) if float(opTempDegC) > float(boilingPoint) else opTempDegC

            # Airborne quality from pool evaporation (AQ_P)
            AQPool = vaporFromPool(poolArea, molecularWeight, vaporPressurekPa, poolTempDegC)

            # Step 3: Calculate total airborne quantity (liquid release) (AQ_L)
            AQ_L = AQLiquid(0, AQPool, releaseRate)

            # Step 1: Calculate PAC toxicity rating
            rating = PACToxicityRating(AQ_L, row, molecularWeight)

            return rating
        
        else:
            # Operating temperature (opTempDegC) >= normal boiling point: Step 9 -> Step 5 -> Did all liquid flash? -> Yes, Step 1 -> No, Steps 7, 6, 4, 3, 1
            
            # Step 9: Calculate flashed fraction of the liquid
            flashedFractionLiquid = flashedFraction(opTempDegC, heatCapacity, HOV, boilingPoint)

            # Step 5: Calculate qirborne quantity from flash (AQ_F)
            AQ_F = AQFlash(flashedFractionLiquid, releaseRate)

            # Did all liquid flash?
            if flashedFractionLiquid < 0.2:
                # Not all liquid flashed

                # Step 7: Calculate total mass
                totalMass = totalMassPool(liquidReleased, flashedFractionLiquid)

                # Step 6: Calculate pool area
                poolArea = dikedArea if dikedArea else liquidPoolArea(totalMass, float(liquidDensity))

                # Step 4: Calculate airborne quality from pool evaporation (AQ_P)
                # Convert vapor pressure to bars
                vaporPressureBars = conversions.std_P(float(vaporPressure), vaporPressureUnit)

                # Convert vapor pressure in bars to kPa
                vaporPressurekPa = conversions.unstd_P(vaporPressureBars, 'kPa')

                # Calcualte characteristic pool temperature (ºC)
                # If operating temperature (temDegC) > boiling point, then use operating temperature
                # Otherwise use boiling point
                poolTempDegC = float(boilingPoint) if float(opTempDegC) > float(boilingPoint) else opTempDegC
                AQPool = vaporFromPool(poolArea, molecularWeight, vaporPressurekPa, poolTempDegC)

                if flashedFractionLiquid == 0:
                    AQ_L = AQPool
                else:
                    # Step 3: Calculate total airborne quantity (liquid release) (AQ_L)
                    AQ_L = AQLiquid(AQ_F, AQPool, releaseRate)

                # Step 1: Calculate PAC toxicity rating
                rating = PACToxicityRating(AQ_L, row, molecularWeight)

                return rating
            else:
                # All liquid flashed

                """
                    set airborne quantity from flash, AQ_F to the liquid release rate, L
                    set airborne quantity from pool evaporation, AQ_P = 0 (i.e. no pool is formed) and no need for further pool calculations.
                """

                # Step 1: Calculate PAC toxicity rating
                rating = PACToxicityRating(AQ_F, row, molecularWeight)

                return rating
