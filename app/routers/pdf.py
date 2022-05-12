import math
from fastapi import APIRouter, UploadFile, File
from helpers.errors import InputDataError
from models import Chemical
from services.database import extract_properties
from services.sds.parser import parse

router = APIRouter()

@router.post('/pdf', response_model=Chemical)
async def file_upload(file: UploadFile = File(...)):
    """
    Extracts information from an SDS document.
    Only Sigma-Aldrich SDS are allowed at the moment.
    """
    if not file.filename.lower().endswith('.pdf'):
        raise InputDataError("Uploaded file is not a PDF")

    # Parse pdf file
    properties = parse(await file.read())

    # Retrive CAS no from PDF
    cas_no = properties.casNo

    # Parse properties from second database
    additional_properties = extract_properties(cas_no)

    # If a property was not contained in the SDS and retreived with parse(),
    # however does exist in the second database,
    # we'll replace that value in properties with the value from the second database
    for prop in ['boilingPt', 'flashPt', 'autoIgnitionTemp', 'upperExplosionLim', 'lowerExplosionLim']:
        print(prop)
        if properties.__getattribute__(prop) == 'No data available' and prop in additional_properties and not math.isnan(additional_properties[prop]):
            properties.__setattr__(prop, str(additional_properties[prop]))

    # Close file
    await file.close()
    return properties
