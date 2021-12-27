import math
from fastapi import APIRouter, HTTPException, UploadFile, File
from models.sds_extract import SDSExtraction
from sds.parser import parse
from calculation_block.calculation_block import extract_properties, cp

router = APIRouter()

@router.post('/pdf', response_model=SDSExtraction)
def file_upload(sds: UploadFile = File(...), temperature=None):
    """
    Extracts information from an SDS document.
    Temperature (in Celcius) is required to caluclate Cp of the compound.
    Only Sigma-Aldrich SDS are allowed at the moment.
    """
    if temperature is None:
        raise HTTPException(400, "Temperature (in Celcius) required")
    if not sds.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Uploaded file is not a PDF")

    # parse local pdf file
    try:
        properties = parse(sds.file)
    except:
        print('Error parsing file. Please try again')
        raise HTTPException(400, "Error parsing file. Please try again")

    sds.close()

    # Retrive CAS no from PDF
    cas_no = properties['casNo']
    
    # Calculate Cp
    properties['cp'] = cp(cas_no, temperature)

    # Parse properties from second database
    additional_properties = extract_properties(cas_no)
    coerce_properties(properties, additional_properties)
    
    return properties

def coerce_properties(properties, additional_properties):
    """
    If a property was not contained in the SDS and retreived with parse(),
    however does exist in the second database,
    we'll replace that value in properties with the value from the second database
    """
    props = ['boilingPt', 'flashPt', 'autoIgnitionTemp', 'upperExplosionLim', 'lowerExplosionLim']
    for prop in props:
        if properties[prop] == 'No data available' and prop in additional_properties and not math.isnan(additional_properties[prop]):
            properties[prop] = additional_properties[prop]
