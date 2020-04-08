# services for calculation block related functions

import pandas as pd
import numpy as np

#relevant column numbers in chem_data.xlsx
COLUMNS = {
    'CHEMICAL': 0,
    'CAS': 2,
    'BOILING_PT': 8,
    'MELTING_PT': 9,
    'FLASH_PT': 10,
    'AUTO_IGNITON_TEMP': 11,
    'LIQCP_A': 18,
    'LIQCP_B': 19,
    'UEL': 100, # do these exist ?
    'LEL': 101,
}
    
df = pd.read_excel("utils/chem_data.xlsx")

# sees if the chemical with a given cas exists in the table.
# returns the row if it does
# otherwise returns false
def get_row(cas):
    row = df.loc[df['CAS'] == cas].to_numpy()
    if len(row) == 0:
        return False

    return row[0]

# extracts boiling_pt given the corresponding row from
# chem_data.xlsx. Used only when it is known that the chemical
# exists in the table
def extract_boiling_pt(row):
    return row[COLUMNS['BOILING_PT']]

# extracts melting_pt given the corresponding row from
# chem_data.xlsx. Used only when it is known that the chemical
# exists in the table
def extract_melting_pt(row):
    return row[COLUMNS['MELTING_PT']]

# extracts flash_pt given the corresponding row from
# chem_data.xlsx. Used only when it is known that the chemical
# exists in the table
def extract_flash_pt(row):
    return row[COLUMNS['FLASH_PT']]

# extracts auto_ignition_temp given the corresponding row from
# chem_data.xlsx. Used only when it is known that the chemical
# exists in the table
def extract_auto_ignition_temp(row):
    return row[COLUMNS['AUTO_IGNITON_TEMP']]

# estimates the cp of a compound given the corresponding
# row from chem_data.xlsx and a temperature according to the formula:
# cp = A + BT
# where A is the LiqCp_A entry in row,
#       B is the LiqCp_B entry in row,
#       T is the temperature in kelvin.
# Used only when it is known that the chemical exists in the table
def estimate_cp(row, T):
    liqCp_A = row[COLUMNS['LIQCP_A']]
    liqCp_B = row[COLUMNS['LIQCP_B']]
    return liqCp_A + liqCp_B * T

def celsius_to_kelvin(C):
    return C + 273