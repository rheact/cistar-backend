from fastapi import APIRouter, HTTPException, UploadFile, File

from sds.parser import parse
from calculation_block.calculation_block import extract_properties, cp

router = APIRouter()

@router.post('/pdf')
def file_upload(sds: UploadFile = File(...), temperature=None):
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
    try:
        additional_properties = extract_properties(cas_no)
        coerce_properties(properties, additional_properties)
    except Exception as e:
        raise HTTPException(400, "Unable to get properties from second database")
    
    return properties

def coerce_properties(properties, additional_properties):
    """
    If a property was not contained in the SDS and retreived with parse(),
    however does exist in the second database,
    we'll replace that value in properties with the value from the second database
    """
    props = ['boilingPt', 'flashPt', 'autoIgnitionTemp', 'upperExplosionLim', 'lowerExplosionLim']
    for prop in props:
        if properties[prop] == 'No data available' and math.isnan(additional_properties[prop]) is False:
            properties[prop] = additional_properties[prop]
