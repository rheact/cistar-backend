import pdftotext

from .services import get_physical_chemical_properties, get_h_numbers, get_product_name, get_CAS_weight, get_explosion_limits
from .ppe import get_ppe

def parse(f: bytes):
    pdfFileObject = f
    if type(f) == str:
        pdfFileObject = open(f, 'rb')

    text = ''
    pdf = pdftotext.PDF(pdfFileObject)
    for page in pdf:
        text += page
        
    pdfFileObject.close()

    h_numbers, h_statements = get_h_numbers(text)
    phys_chem_properties = get_physical_chemical_properties(text)
    product_name = get_product_name(text)
    cas_num, weight = get_CAS_weight(text)
    upperlimit, lowerlimit = get_explosion_limits(text)
    ppe_sections, ppe_pages = get_ppe(text)

    properties_list = [product_name]  + [weight] + [cas_num] + phys_chem_properties + [upperlimit] + [lowerlimit]
    properties = convert_arr_to_dict(properties_list)
    properties['hNumbers'] = h_numbers
    properties['hStatements'] = h_statements
    properties['ppe_sections'] = ppe_sections
    properties['ppe_pages'] = ppe_pages
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
