import pandas as pd
import math
from models import PACRating
from helpers.units import conversions
    
df = pd.read_excel("data/thor_database.xlsx")

def get_row(casNo):
    """
    Sees if the chemical with a given cas exists in the table.
    returns the row if it does otherwise returns None 
    """
    row = df[df['CAS Number'] == casNo]
    if len(row) == 0:
        return None
    return row

def calculate_heat_of_reaction(casNo: str, phase: str, numberOfMoles: str):
    row = get_row(casNo)
    assert row is not None, f'Unable to calculate heat of formation for chemical {casNo}, please enter the value manually.'

    heatOfFormation = row[phase.lower()].values[0]
    assert not math.isnan(heatOfFormation), f'Unable to calculate heat of formation for chemical {casNo} in {phase} phase, please enter the value manually.'

    print(float(numberOfMoles) * heatOfFormation)
    return float(numberOfMoles) * heatOfFormation
