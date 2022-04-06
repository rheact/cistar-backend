""" Services for calculation block related functions as well as chem_table data """

from typing import Union
import pandas as pd
import math

""" Relevant column numbers in chem_table.xlsx """
COLUMNS = {
    'CHEMICAL': 0,
    'CAS': 1,
    'BOILING_PT': 27,
    'MELTING_PT': 28,
    'FLASH_PT': 34,
    'UEL': 35, # do these exist ?
    'LEL': 36,
    'AUTO_IGNITON_TEMP': 37,
    'LIQCP_A': 47,
    'LIQCP_B': 48,
}
    
df = pd.read_excel("data/chem_table.xlsx")

def get_row(cas):
    """
    Sees if the chemical with a given cas exists in the table.
    returns the row if it does otherwise returns None 
    """
    row = df.loc[df['CAS Number'] == cas].to_numpy()
    if len(row) == 0:
        return None
    return row[0]

def __extract_boiling_pt(row):
    return row[COLUMNS['BOILING_PT']]

def __extract_melting_pt(row):
    return row[COLUMNS['MELTING_PT']]

def __extract_flash_pt(row):
    return row[COLUMNS['FLASH_PT']]

def __extract_upper_explosion_limit(row):
    return row[COLUMNS['UEL']]

def __extract_lower_explosion_limit(row):
    return row[COLUMNS['LEL']]

def __extract_auto_ignition_temp(row):
    return row[COLUMNS['AUTO_IGNITON_TEMP']]

def __estimate_cp_of_chemical(row, kelvin_T) -> float:
    """
    Estimates the cp of a compound given the corresponding
    row from chem_table.xlsx and a temperature according to the formula:
    cp = A + BT
    where A is the LiqCp_A entry in row,
          B is the LiqCp_B entry in row,
          T is the temperature in kelvin.
    Used only when it is known that the chemical exists in the table
    """
    liqCp_A = row[COLUMNS['LIQCP_A']]
    liqCp_B = row[COLUMNS['LIQCP_B']]
    return liqCp_A + liqCp_B * kelvin_T

def extract_properties(cas) -> dict:
    """
    Extracts boiling_pt, melting_pt, flash_pt, auto_ignition_temp
    for the chemical with the given cas

    Returns: A dictionary
    """
    properties = {
        'boilingPt': math.nan,
        'meltingPt': math.nan,
        'flashPt': math.nan,
        'autoIgnitionTemp': math.nan,
        'upperExplosionLim': math.nan,
        'lowerExplosionLim': math.nan,
    }

    row = get_row(cas)
    if row is None:
        return properties
    
    properties['boilingPt'] = __extract_boiling_pt(row)
    properties['meltingPt'] = __extract_melting_pt(row)
    properties['flashPt'] = __extract_flash_pt(row)
    properties['autoIgnitionTemp'] = __extract_auto_ignition_temp(row)
    properties['upperExplosionLim'] = __extract_upper_explosion_limit(row)
    properties['lowerExplosionLim'] = __extract_lower_explosion_limit(row)
    return properties

def estimate_cp_from_database(cas: str, celcius_T: str) -> Union[float, str]:
    """
    Estimates the cp for the chemical with the given cas
    at the given temperature (in degrees celsius)
    Returns the estimate cp as a number
    If the CAS does not exist in the table it will return the empty string
    (because the user must input the cp later)
    """
    row = get_row(cas)

    if row is None:
        return ''
    
    # T will be a string, convert to int
    # This is in Celcius!!
    temp = int(celcius_T)
    if math.isnan(temp) is True:
        raise Exception
    
    # TODO: Kelvin
    return __estimate_cp_of_chemical(row, temp + 273.15)
