from .map import UNIT_MAP

def std_T(v: float, u: str) -> float:
    """
    Standardise temperature from unit u to degC
    """
    if u is None or u == '':
        return v
    assert type(v) == float, f"Value is not a float: {v}"
    assert u in UNIT_MAP['T'].keys(), f"Unknown unit: {u}"
    return UNIT_MAP['T'][u]['s'](v)

def unstd_T(v: float, u: str) -> float:
    """
    Unstandardise temperature from degC to u
    """
    if u is None or u == '':
        return v
    assert type(v) == float, f"Value is not a float: {v}"
    assert u in UNIT_MAP['T'].keys(), f"Unknown unit: {u}"
    return UNIT_MAP['T'][u]['us'](v)

def std_P(v: float, u: str) -> float:
    """
    Standardise pressure from unit u to bars 
    """
    if u is None or u == '':
        return v
    assert type(v) == float, f"Value is not a float: {v}"
    assert u in UNIT_MAP['P'].keys(), f"Unknown unit: {u}"
    return UNIT_MAP['P'][u]['s'](v)

def unstd_P(v: float, u: str) -> float:
    """
    Unstandardise temperature from degC to u
    """
    if u is None or u == '':
        return v
    assert type(v) == float, f"Value is not a float: {v}"
    assert u in UNIT_MAP['P'].keys(), f"Unknown unit: {u}"
    return UNIT_MAP['P'][u]['us'](v)

def std_dH(v: float, u: str, mw: float) -> float:
    """
    Standardise heat of reaction from unit u to cal/g 
    Argument includes molecular weight of basis
    """
    if u is None or u == '':
        return v
    assert type(v) == float, f"Value is not a float: {v}"
    if 'mol' in u:
        assert type(mw) == float, f"Molecular weight is not a float: {mw}"
    assert u in UNIT_MAP['dH'].keys(), f"Unknown unit: {u}"
    return UNIT_MAP['dH'][u]['s'](v, mw)

def unstd_dH(v: float, u: str, mw: float) -> float:
    """
    Unstandardise heat of reaction from cal/g to u
    Argument includes molecular weight of basis
    """
    if u is None or u == '':
        return v
    assert type(v) == float, f"Value is not a float: {v}"
    if 'mol' in u:
        assert type(mw) == float, f"Molecular weight is not a float: {mw}"
    assert u in UNIT_MAP['dH'].keys(), f"Unknown unit: {u}"
    return UNIT_MAP['P'][u]['us'](v, mw)

def std_Cp(v: float, u: str, mw: float) -> float:
    """
    Standardise specific heat from unit u to cal/g/degC
    Argument includes molecular weight of basis
    """
    if u is None or u == '':
        return v
    assert type(v) == float, f"Value is not a float: {v}"
    if 'mol' in u:
        assert type(mw) == float, f"Molecular weight is not a float: {mw}"
    assert u in UNIT_MAP['Cp'].keys(), f"Unknown unit: {u}"
    return UNIT_MAP['Cp'][u]['s'](v, mw)

def unstd_Cp(v: float, u: str, mw: float) -> float:
    """
    Unstandardise specific heat from cal/g/degC to u
    Argument includes molecular weight of basis
    """
    if u is None or u == '':
        return v
    assert type(v) == float, f"Value is not a float: {v}"
    if 'mol' in u:
        assert type(mw) == float, f"Molecular weight is not a float: {mw}"
    assert u in UNIT_MAP['Cp'].keys(), f"Unknown unit: {u}"
    return UNIT_MAP['Cp'][u]['us'](v, mw)
