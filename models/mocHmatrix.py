from typing import List
from pydantic import BaseModel

class MOCHMatrix(BaseModel):
    level1: List[str]
    level2: List[str]
    level3: List[str]
