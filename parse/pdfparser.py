import pdftotext

from .services import get_physical_chemical_properties, get_h_numbers, pname, num_weight, explosion_limits

def parse(f):
    text = ''
    pdfFileObject = open(f, 'rb')
    pdf = pdftotext.PDF(pdfFileObject)
    for page in pdf:
        text += page
        
    pdfFileObject.close()

    h_numbers, h_statements = get_h_numbers(text)
    phys_chem_properties = get_physical_chemical_properties(text)
    product_name = pname(text)
    cas_num, weight = num_weight(text)
    upperlimit, lowerlimit = explosion_limits(text)

    properties_list = [product_name]  + [weight] + [cas_num] + phys_chem_properties + [upperlimit] + [lowerlimit]
    properties = convert_arr_to_dict(properties_list)
    properties['hNumbers'] = h_numbers
    properties['hStatements'] = h_numbers
    return properties
    
# a: array of properties
# @return dict: dictionary of property name : value
def convert_arr_to_dict(a):
    dict = {}
    dict['productName'] = a[0]
    dict['molWt'] = a[1]
    dict['casNo'] = a[2]
    dict['ph'] = a[3]
    dict['boilingPt'] = a[4]
    dict['flashPt'] = a[5]
    dict['vapourPressure'] = a[6]
    dict['vapourDensity'] = a[7]
    dict['relDensity'] = a[8]
    dict['autoIgnitionTemp'] = a[9]
    dict['decompositionTemp'] = a[10]
    dict['viscosity'] = a[11]
    dict['upperExplosionLim'] = a[12]
    dict['lowerExplosionLim'] = a[13]

    return dict