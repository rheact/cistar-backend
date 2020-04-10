import pdftotext

from .services import get_physical_chemical_properties, get_h_numbers, pname, num_weight

def parse(f):
    text = ''
    pdfFileObject = open(f, 'rb')
    pdf = pdftotext.PDF(pdfFileObject)
    for page in pdf:
        text += page
        
    pdfFileObject.close()

    h_numbers = get_h_numbers(text)
    phys_chem_properties = get_physical_chemical_properties(text)
    product_name = pname(text)
    cas_num, weight = num_weight(text)
    
    properties_list = [product_name]  + [weight] + [cas_num] + phys_chem_properties

    properties = convert_arr_to_dict(properties_list)
    properties['hNumbers'] = h_numbers
    return properties
    
# a: array of properties
# @return dict: dictionary of property name : value
def convert_arr_to_dict(a):
    dict = {}
    # we'll get the explosion limits from the second database later
    dict['upperExplosionLim'] = 'No data available'
    dict['lowerExplosionLim'] = 'No data available'
    
    dict['productName'] = a[0]
    dict['molWt'] = a[1]
    dict['casNo'] = a[2]
    dict['ph'] = a[3]
    dict['boilingPt'] = a[4]
    dict['flashPt'] = a[5]
    dict['flammabilityLimits'] = a[6]
    dict['vapourPressure'] = a[7]
    dict['vapourDensity'] = a[8]
    dict['relDensity'] = a[9]
    dict['autoIgnitionTemp'] = a[10]
    dict['decompositionTemp'] = a[11]
    dict['viscosity'] = a[12]

    return dict