import pandas as pd
import numpy as np
import math

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
    

df = pd.read_excel("chem_data.xlsx")

def cal(cas,x,T=30,d_h=200):
    col = ['Chemical','LiqCp_A','LiqCp_B']
    #df = pd.read_excel("chem_data.xlsx")
    a= df.loc[df['CAS'].isin(cas)][col]
    b = a[col].values
    print('b: ', b)
    n = len(b)
    m = .373
    cps = []
    # for i in range(n):
    #     cp = b[i][1] + b[i][2]*T
    #     cps.append(cp)
    #     m+= x[i]*cp
    #     print("Cp of " + b[i][0] +": " + str(cp))

    print("Cp of Mixture:" + str(m))
    
    #ad_t = d_h / m
    ad_t = -57.1 / .373
    ad_p = (ad_t/T)**(1.4/0.4)
    
    print('type: ', type(ad_p))
    print(ad_p)
    print("Adiabatic Temperature: " + str(ad_t))
    print("Adiabatic Pressure: " + str(ad_p))
    
    #d_t = ad_t - T
    #d_p = ad_p - P

# extracts boiling_pt, melting_pt, flash_pt, auto_ignition_temp
# for the chemical with the given cas
# returns a dictionary of the form
# 'propertyName':property
# if the cas does not exist in the table the dictionary will contain
# 'propertyName':nan
def extract_properties(cas):
    properties = {
        'boilingPt': math.nan,
        'meltingPt': math.nan,
        'flashPt': math.nan,
        'autoIgnitionTemp': math.nan,
    }

    row = get_row(cas)
    if row is False:
        return properties
    
    properties['boilingPt'] = extract_boiling_pt(row)
    properties['meltingPt'] = extract_melting_pt(row)
    properties['flashPt'] = extract_auto_ignition_temp(row)
    properties['autoIgnitionTemp'] = extract_flash_pt(row)
    return properties

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


#Calling the functions
#x = [0.25,0.25,0.25,0.25]
#cas = ['75-07-0','64-19-7','108-24-7','67-64-1']


# Calculation block example
# weighted average
hcl = '7647-01-0'
x = [0.16, 0.16, 0.16, 0.17, 0.17, 0.17]
cas = ['65-85-0', '7647-01-0', '7664-93-9', '7446-11-9', '98-07-7', '7732-18-5']
# for c in cas:
#     print(get_row(c))
#row = get_row('7647-01-0')
#extract_auto_ignition_temp('7647-01-0')
#cal(cas,x,30, -57.1)