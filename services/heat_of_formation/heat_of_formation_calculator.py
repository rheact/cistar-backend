import pandas as pd
import math
from decimal import *
from helpers.units import conversions
    
main_df = pd.read_excel("data/CRC_Pedley_Combined_Updated.xlsx")
nbs_df = pd.read_excel("data/nbs_updated.xlsx")

"""
    See if the chemical with a given cas exists in the given file (df).
    returns the row if it does otherwise returns None 
"""
def get_row(casNo, df):
    row = df[df['CAS Number'] == casNo]
    if len(row) == 0:
        return None
    return row

"""
    Calculate the heat of reaction for a chemical with the provided CAS number and in the specified phase, utilizing CRC, Pedley, and NBS databases.
    (Note: Pedley only includes liquid and gas phases)

    If the chemical is present in the CRC & Pedley database:
        1. If the heat of formation for the desired phase exists, use the value to calculate the heat of reaction.
        2. If the desired phase is solid:
            2.1 If the heat of formation of the chemical in the liquid phase and its heat of fusion exist,
                calculate the heat of reaction for the solid phase as heat of formation in liquid phase - heat of fusion.
            2.2 Else if the heat of formation of the chemical in the gas phase, and heat of fusion and vaporization exist,
                calculate the heat of reaction for the solid phase as heat of formation in gas phase - heat of fusion - heat of vaporization.
        3. If the desired phase is liquid:
            3.1 If the heat of formation of the chemical in the solid phase and its heat of fusion exist,
                calculate the heat of reaction for the liquid phase as heat of formation in solid phase + heat of fusion.
            3.2 Else if the heat of formation of the chemical in the gas phase, and heat of vaporization exist,
                calculate the heat of reaction for the liquid phase as heat of formation in gas phase - heat of vaporization.
            3.3 Else if the heat of reaction for the liquid phase of this chemical exists in the Pedley database,
                use the value from the Pedley database.
        4. If the desired phase is gas:
            4.1 If the heat of formation of the chemical in the liquid phase and its heat of vaporization exist,
                calculate the heat of formation for the gas phase as heat of formation in liquid phase + heat of vaporization.
            4.2 Else if the heat of formation of the chemical in the solid phase, and heat of fusion and vaporization exist,
                calculate the heat of formation for the gas phase as heat of formation in solid phase + heat of fusion + heat of vaporization.
            4.3 Else if the heat of reaction for the gas phase of this chemical exists in the Pedley database,
                use the value from the Pedley database.

    If the chemical doesn't exist in the CRC & Pedley database but exists in the NBS database:
        Try to obtain the heat of formation for the desired phase directly.
"""
def calculate_heat_of_reaction(casNo: str, phase: str, numberOfMoles: str):
    row = get_row(casNo, main_df)
    nbs_row = get_row(casNo, nbs_df)

    assert row is not None or nbs_row is not None, f'Unable to calculate heat of formation for chemical {casNo}, please enter the value manually.'
     
    heatOfFormation = None
    if row is not None:
        heatOfFormation = row['CRC Heat of Formation ' + phase].values[0]
        heatOfFusion = row['CRC Heat of Fusion'].values[0]
        heatOfVaporization = row['CRC Heat of Vaporization'].values[0]

        hSolid = row['CRC Heat of Formation Solid'].values[0]
        hLiquid = row['CRC Heat of Formation Liquid'].values[0]
        hGas = row['CRC Heat of Formation Gas'].values[0]

        pedleyLiquid = row['Pedley Heat of Formation Liquid'].values[0]
        pedleyGas = row['Pedley Heat of Formation Gas'].values[0]

        if math.isnan(heatOfFormation):
            if phase == 'Solid':
                if not math.isnan(hLiquid) and not math.isnan(heatOfFusion):
                    heatOfFormation = hLiquid - heatOfFusion

                elif not math.isnan(hGas) and not math.isnan(heatOfFusion) and not math.isnan(heatOfVaporization):
                    heatOfFormation = hGas - heatOfFusion - heatOfVaporization

            elif phase == 'Liquid':
                if not math.isnan(hSolid) and not math.isnan(heatOfFusion):
                    heatOfFormation = hSolid + heatOfFusion

                elif not math.isnan(hGas) and not math.isnan(heatOfVaporization):
                    heatOfFormation = hGas - heatOfVaporization

                if math.isnan(heatOfFormation) and not math.isnan(pedleyLiquid):
                    heatOfFormation = pedleyLiquid

            else:
                # phase == 'Gas'
                if not math.isnan(hLiquid) and not math.isnan(heatOfVaporization):
                    heatOfFormation = hLiquid + heatOfVaporization

                elif not math.isnan(hSolid) and not math.isnan(heatOfFusion) and not math.isnan(heatOfVaporization):
                    heatOfFormation = hSolid + heatOfFusion + heatOfVaporization
                
                if math.isnan(heatOfFormation) and not math.isnan(pedleyGas):
                    heatOfFormation = pedleyGas

    if (heatOfFormation is None or math.isnan(heatOfFormation)) and nbs_row is not None:
        if phase == 'Solid':
            heatOfFormation = nbs_row['Crystalline solid (cr)'].values[0]
        elif phase == 'Liquid':
            heatOfFormation = nbs_row['Liquid (l)'].values[0]
        else:
            # phase == 'Gas'
            heatOfFormation = nbs_row['Gas (g)'].values[0]

    assert not math.isnan(heatOfFormation), f'Unable to calculate heat of formation for chemical {casNo} in {phase} phase, please enter the value manually.'
    
    return round(float(numberOfMoles) * heatOfFormation, 3)