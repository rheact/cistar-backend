import pandas as pd
import math
from helpers.units import conversions
    
main_df = pd.read_excel("data/thor_database.xlsx")
hof_df = pd.read_excel("data/thor_hof_database.xlsx")
hov_df = pd.read_excel("data/thor_hov_database.xlsx")

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
    assert row is not None, f'Unable to calculate heat of formation for chemical {casNo}, please enter the value manually.'

    heatOfFormation = row[phase.lower()].values[0]

    if math.isnan(heatOfFormation):
        if phase == 'Solid':
            hLiquid = row['liquid'].values[0]
            hGas = row['gas'].values[0]
            hofRow = get_row(casNo, hof_df)
            hovRow = get_row(casNo, hov_df)
            if not math.isnan(hLiquid):
                if hofRow is not None:
                    hFus = hofRow['Heat of Fusion'].values[0]
                    heatOfFormation = hLiquid - hFus
            elif not math.isnan(hGas):
                hFus = hofRow['Heat of Fusion'].values[0] if hofRow is not None else None
                hVap = hovRow['Heat of Vaporization'].values[0] if hovRow is not None else None
                if hFus is not None and hVap is not None:
                    heatOfFormation = hGas - hFus - hVap
        elif phase == 'Liquid':
            hSolid = row['solid'].values[0]
            hGas = row['gas'].values[0]
            hofRow = get_row(casNo, hof_df)
            hovRow = get_row(casNo, hov_df)
            if not math.isnan(hSolid):
                if hofRow is not None:
                    hFus = hofRow['Heat of Fusion'].values[0]
                    heatOfFormation = hSolid + hFus
            elif not math.isnan(hGas):
                if hovRow is not None:
                    hVap = hovRow['Heat of Vaporization'].values[0]
                    heatOfFormation = hGas - hVap
        else:
            hSolid = row['solid'].values[0]
            hLiquid = row['gas'].values[0]
            hofRow = get_row(casNo, hof_df)
            hovRow = get_row(casNo, hov_df)
            if not math.isnan(hLiquid):
                if hovRow is not None:
                    hVap = hovRow['Heat of Vaporization'].values[0]
                    heatOfFormation = hLiquid + hVap
            elif not math.isnan(hSolid):
                hFus = hofRow['Heat of Fusion'].values[0] if hofRow is not None else None
                hVap = hovRow['Heat of Vaporization'].values[0] if hovRow is not None else None
                if hFus is not None and hVap is not None:
                    heatOfFormation = hSolid + hFus + hVap

    assert not math.isnan(heatOfFormation), f'Unable to calculate heat of formation for chemical {casNo} in {phase} phase, please enter the value manually.'
    
    return float(numberOfMoles) * heatOfFormation