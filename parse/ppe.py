import re
from typing import List, Tuple

footer_expr = re.compile(
    r"[\n\r\s]*SIGALD - (?:\d)+[\n\r\s]+[a-zA-Z\n\r\s,]+Page ([0-9]+) of [0-9]+[\n\r\s]*",
)

SECTIONS = [
    "Appropriate Engineering Controls",
    "Eye/face protection",
    "Skin protection",
    "Body protection",
    "Respiratory protection",
    "Control of environmental exposure",
    "Section 9",
]

def get_ppe(text: str) -> Tuple[dict, List[int]]:

    # Find sections
    def find(s, insensitive=True):
        if insensitive:
            found = re.search(s, text, re.IGNORECASE)
        else:
            found = re.search(s, text)

        if not found:
            return None

        return found.span()

    find_start = find(r"Appropriate Engineering Controls[\r\n]")
    if not find_start:
        return {}, []
    find_end = find("SECTION 9")
    if not find_end:
        return {}, []
    big_start = find_start[0]
    big_end = find_end[1]
    text = text[big_start:big_end]

    sindex = dict()
    sindex[0] = find(r"Appropriate Engineering Controls[\r\n]")
    sindex[6] = find("SECTION 9")
    sindex[1] = find(r"Eye/face protection[\r\n]")
    sindex[2] = find(r"Skin protection[\r\n]")
    sindex[3] = find(r"Body protection[\r\n]")
    sindex[4] = find(r"Respiratory protection[\r\n]")
    sindex[5] = find(r"Control of environmental exposure[\r\n]")

    # Remove footer
    def textWithoutFooters(start, end) -> Tuple[ str, List[int] ]:
        # Extract text
        ex = text[start:end]

        # Find footer spans and page numbers
        spans = list()
        px = list()
        footer = footer_expr.search(ex)
        while footer:
            page = int(footer.groups(1)[0])
            px.append(page)
            spans.append(footer.span())
            footer = footer_expr.search(ex[footer.endpos:])

        # Remove spans from extracted text
        x = 0
        ret = ""
        for s, e in spans:
            ret += ex[x:s]
            x = e
        ret += ex[x:]

        return ret, px

    # Extract portion of section 8.2
    ret = dict()
    pnos = list()

    def extractAppend(title, ss, se):
        start = sindex[ss][1]
        end = sindex[se][0]
        extract, pages = textWithoutFooters(start, end)
        ret[title] = extract
        pnos.extend(pages)

    for idx, key in enumerate(SECTIONS[:-1]):
        extractAppend(key, idx, idx + 1)

    return ret, pnos
