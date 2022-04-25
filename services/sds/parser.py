from pint import test
from .retrievers import get_physical_chemical_properties, get_h_numbers, get_product_name, get_CAS_weight, get_explosion_limits
from .ppe_pages import get_ppe_page_nos, get_ppe_pages_base64

import fitz

def parse(fb: bytes) -> dict:
    properties = dict()
    doc = fitz.Document(None, fb, 'pdf')

    pagetexts = []
    for page in doc.pages():
        pagetexts.append(page.get_text())
    text = ''.join(pagetexts)

    properties['hNumbers'], properties['hStatements'] = get_h_numbers(text)
    properties['productName'] = get_product_name(text)
    properties['casNo'], properties['molWt'] = get_CAS_weight(text)
    properties['upperExplosionLim'], properties['lowerExplosionLim'] = get_explosion_limits(text)
    properties['ppe_pagerange'] = get_ppe_page_nos(pagetexts)
    properties['ppe_pages']= get_ppe_pages_base64(doc, properties['ppe_pagerange'])

    phys_chem_properties = get_physical_chemical_properties(text)
    properties['ph'] = phys_chem_properties[0]
    properties['boilingPt'] = phys_chem_properties[1]
    properties['flashPt'] = phys_chem_properties[2]
    properties['vapourPressure'] = phys_chem_properties[3]
    properties['vapourDensity'] = phys_chem_properties[4]
    properties['relDensity'] = phys_chem_properties[5]
    properties['autoIgnitionTemp'] = phys_chem_properties[6]
    properties['decompositionTemp'] = phys_chem_properties[7]
    properties['viscosity'] = phys_chem_properties[8]

    doc.close()

    return properties
