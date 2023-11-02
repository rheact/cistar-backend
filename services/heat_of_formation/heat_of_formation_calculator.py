import pandas as pd
import math
from decimal import *
from helpers.units import conversions
    
main_df = pd.read_excel("data/CRC_Pedley_Combined_Updated.xlsx")
nbs_df = pd.read_excel("data/nbs_updated.xlsx")

def get_row(casNo, df):
    """
    Sees if the chemical with a given cas exists in the table.
    returns the row if it does otherwise returns None 
    """
    row = df[df['CAS Number'] == casNo]
    if len(row) == 0:
        return None
    return row

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