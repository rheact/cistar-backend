import math

from .services import get_row, extract_auto_ignition_temp, extract_boiling_pt, extract_flash_pt, extract_melting_pt, extract_lower_explosion_limit, extract_upper_explosion_limit, estimate_cp, celsius_to_kelvin, kelvin_to_celsius

def calculate_cp_mix(d_h, cp_mix, T = 0, P = 1):
    # print(d_h)
    # print(cp_mix)
    # print(T)
    # print(P)
    # m = 0
    # cps = []
    # for i in range(n):
    #     cp = b[i][1] + b[i][2]*T
    #     cps.append(cp)
    #     m+= x[i]*cp
    #     print("Cp of " + b[i][0] +": " + str(cp))
    # print("d_h: ", d_h)
    # print("cp_mix: ", cp_mix)
    # print("T: ", T)
    # print("P: ", P)

    # multiply heat of reaction by -1 for exo/endothermic reactions
    d_h = d_h * -1
    
    #print(T)
    GAMMA = 1.67
    ad_t = d_h / cp_mix
    final_t = celsius_to_kelvin(ad_t + T)
    kelvin = celsius_to_kelvin(T)
    
    g = GAMMA/(1 - GAMMA)
    # print("kelvin: ", kelvin)
    # print("final_t: ", final_t)
    # print("P: ", P)
    # print("g: ", g)
    ad_p = (kelvin/final_t)**(g) * P
    #print("ad_p: ", ad_p)
    return {
        'adiabaticTemp': ad_t,
        'finalTemp': kelvin_to_celsius(final_t),
        'adiabaticPressure': ad_p, 
    }
    

def calculate_without_cp_mix(reactants, products, d_h, T = 0, P = 1):
    cp_mix = 0
    # print('reactants: ', reactants)
    # print('products: ', products)

    # add weighted cp of reactants
    for reactant in reactants:
        cp = reactant['cp']
        if cp == '':
            cp = 0
        else:
            cp = float(cp)
        fraction = float(reactant['molWtFraction'])
        cp_mix += cp * fraction

    # add weighted cp of reactants
    for product in products:
        if cp == '':
            cp = 0
        else:
            cp = float(cp)
        fraction = float(product['molWtFraction'])
        cp_mix += cp * fraction
        
    # multiply heat of reaction by -1 for exo/endothermic reactions
    d_h = d_h * -1
    
    GAMMA = 1.67
    ad_t = d_h / cp_mix
    final_t = celsius_to_kelvin(ad_t + T)
    kelvin = celsius_to_kelvin(T)
    g = GAMMA/(1 - GAMMA)
    ad_p = (kelvin/final_t)**(g) * P
    
    # print("Adiabatic Temperature: " + str(ad_t))
    # print("Adiabatic Pressure: " + str(ad_p))

    return {
        'adiabaticTemp': ad_t,
        'finalTemp': kelvin_to_celsius(final_t),
        'adiabaticPressure': ad_p, 
    }

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