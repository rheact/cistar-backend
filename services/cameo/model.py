from typing import List
from pydantic import BaseModel

class CameoTable(BaseModel):
    html_element: str
    errors: List[str]
