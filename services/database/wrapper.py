""" Services for calculation block related functions as well as chem_table data """

from typing import Union
import pandas as pd
import math

from helpers.errors import InputDataError
    
df = pd.read_excel("data/chem_table.xlsx")

def get_row(cas):
    """
    Sees if the chemical with a given cas exists in the table.
    returns the row if it does otherwise returns None 
    """
    row = df[df['CAS Number'] == cas]
    if len(row) == 0:
        return None
    return row

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
    
    properties['boilingPt'] = row['Boiling\nPoint\n(deg C)']
    properties['meltingPt'] = row['Melting\nPoint\n(deg C)']
    properties['flashPt'] = row['Flash\nPoint\n(deg C)']
    properties['autoIgnitionTemp'] = row['Autoignition Temp\n(deg C)']
    properties['upperExplosionLim'] = row['LFL\n(vol %)']
    properties['lowerExplosionLim'] = row['UFL (vol %)']
    return properties

def estimate_cp_from_database(cas: str, celcius_T: str) -> Union[float, str]:
    """
    Estimates the cp for the chemical with the given cas
    at the given temperature (in degrees celsius)
    Returns the estimate cp as a number
    If the CAS does not exist in the table it will return the empty string
    (because the user must input the cp later)
    """
    # T will be a string, convert to int
    celcius_T = float(celcius_T)
    if math.isnan(celcius_T) is True:
        raise InputDataError("Temperature is not a number")

    row = get_row(cas)
    if row is None:
        return ''
    
    # cp = A + BT
    # where A is the LiqCp_A entry in row,
    #       B is the LiqCp_B entry in row,
    #       T is the temperature in celcius.
    liqCp_A = float(row['Liq Cp\n(cal/g-C)\nA Coeff'])
    liqCp_B = float(row['Liq Cp\n(cal/g-C)\nB Coeff'])
    return liqCp_A + liqCp_B * celcius_T
