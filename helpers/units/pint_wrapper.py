from typing import Optional
import pint
_U = pint.UnitRegistry()
_Q = _U.Quantity

# For a given unit, we need to bring it down to standard units for calculations.
# Standard units are as follows:
#   Temperature: degC
#   Pressure: bar
#   Heat: cal/g
#   Cp: cal/g/degC

def _standardizer(base: str):
    def std_func(value: float, unit: Optional[str]) -> _Q:
        # Check if unit doesn't exist
        if unit is None or unit == '' or _U(base) == _U(unit):
            return value * _U(base) # Assume that unit is standard already
        # Or else convert to base unit
        return (value * _U(unit)).to(_U(base))
    return std_func

std_temp = _standardizer("degC")
std_pres = _standardizer("bar")
std_heat = _standardizer("cal / g")
std_cp   = _standardizer("cal / g / delta_degC")

# After calculations, we need to send the data back in units specified by user.
# So we need to reverse the transformation above.
# Pint package on pip is very useful for this.

def _unstandardizer(base: str):
    def unstd_func(q: _Q, target: str) -> _Q:
        # Check if quantity passed is in base units
        assert q.units == _U(base), f"{q.units} is not standard {base}"
        # Convert to user defined units
        return q.to(_U(target))
    return unstd_func

unstd_temp = _unstandardizer("degC")
unstd_pres = _unstandardizer("bar")
unstd_heat = _unstandardizer("cal / g")
unstd_cp   = _unstandardizer("cal / g / delta_degC")
