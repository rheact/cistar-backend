import math
from fastapi import APIRouter, HTTPException, UploadFile, File
from models.sds_extract import SDSExtraction
from services.calculation_block import extract_properties, cp
from services.sds.parser import parse

router = APIRouter()

@router.post('/pdf', response_model=SDSExtraction)
async def file_upload(file: UploadFile = File(...), temperature=None):
    """
    Extracts information from an SDS document.
    Temperature is required to caluclate Cp of the compound.
    Only Sigma-Aldrich SDS are allowed at the moment.
    """
    if temperature is None:
        raise HTTPException(400, "Temperature required")
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Uploaded file is not a PDF")
    
    #TODO: Standardise temperature

    # Parse pdf file
    properties = parse(await file.read())

    # Retrive CAS no from PDF
    cas_no = properties['casNo']
    
    # Calculate Cp
    properties['cp'] = cp(cas_no, temperature)

    # Parse properties from second database
    additional_properties = extract_properties(cas_no)
    coerce_properties(properties, additional_properties)

    # Close file
    await file.close()
    
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
