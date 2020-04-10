import math

from .services import get_row, extract_auto_ignition_temp, extract_boiling_pt, extract_flash_pt, extract_melting_pt, extract_lower_explosion_limit, extract_upper_explosion_limit, estimate_cp, celsius_to_kelvin

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

# estimates the cp for the chemical with the given cas
# at the given temperature (in degrees celsius)
# returns the estimate cp as a number
# if the cas does not exist in the table it will return the empty string
# (because the user must input the cp later)
def cp(cas, T):
    row = get_row(cas)

    if row is False:
        return ''
    
    # T will be a string, convert to int
    temp = int(T)
    if math.isnan(temp) is True:
        raise Exception
    
    return estimate_cp(row, celsius_to_kelvin(temp))


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
        'upperExplosionLim': math.nan,
        'lowerExplosionLim': math.nan,
    }

    row = get_row(cas)
    if row is False:
        return properties
    
    properties['boilingPt'] = extract_boiling_pt(row)
    properties['meltingPt'] = extract_melting_pt(row)
    properties['flashPt'] = extract_flash_pt(row)
    properties['autoIgnitionTemp'] = extract_auto_ignition_temp(row)
    properties['upperExplosionLim'] = extract_upper_explosion_limit(row)
    properties['lowerExplosionLim'] = extract_lower_explosion_limit(row)
    return properties

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
row = get_row('7647-01-0')
#extract_auto_ignition_temp('7647-01-0')
#cal(cas,x,30, -57.1)