import fitz
import base64
import re
from typing import List, Optional, Tuple

section8dot2 = re.compile(
    r"\n?\s*8.2\s*Exposure controls\s*\n"
)

section9 = re.compile(
    r"\n?\s*SECTION\s*9:\s*Physical\s*and\s*chemical\s*properties\s*\n"
)

"""
    Gets page numbers of pages Section 8.2 -> Section 9
        - Start page is the page with heading "8.2 Exposure Controls"
        - End page is the page with heading "SECTION 9: Physical and chemical properties"
"""
def get_ppe_page_nos(pagetexts: List[str]) -> Optional[Tuple[int, int]]:

    # Approach:
    # This function uses a FSA to judge which state we are in to set start and end
    state = 0
    start = -1
    end = -1

    for pno, page in enumerate(pagetexts):
        # state: finding start
        if state == 0:
            m = section8dot2.search(page)
            if m is not None:
                state = 1
                start = pno

        # state: finding end
        if state == 1:
            m = section9.search(page)
            if m is not None:
                state = 2
                end = pno
                break # no need to search more

    # state: found both start and end
    if state != 2:
        return None

    return start, end

"""
    Generate a list of Base64-encoded PNG images
"""
def get_ppe_pages_base64(doc: fitz.Document, pagerange: Tuple[int,int]) -> List[str]:
    pbytes = list()
    for pno in range(pagerange[0], pagerange[1]+1):
        page = doc.load_page(pno)
        pb = base64.b64encode(page.get_pixmap().tobytes())
        pbytes.append("data:image/png;base64, " + pb.decode('utf-8'))
    return pbytes
