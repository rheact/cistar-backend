"""
    A dictionary that defines conversion functions for temperature ('T'), pressure ('P'), enthalpy change ('dH'), and specific heat capacity ('Cp').

    's' denotes conversion from a source unit to a standardized unit.
    'us' denotes the reverse, conversion from the standardized unit back to the source unit.
"""
UNIT_MAP = {
    'T': {
        '°C': {
            's': lambda v: v,
            'us': lambda v: v,
        },
        '°F': {
            # f to degC
            's': lambda v: (v-32)*5/9,
            # degC to f
            'us': lambda v: (9*v/5)+32,
        },
        'K': {
            's': lambda v: v-273.15,
            'us': lambda v: v+273.15,
        },
    },
    'P': {
        'bar': {
            's': lambda v: v,
            'us': lambda v: v,
        },
        'kPa': {
            's': lambda v: v/100,
            'us': lambda v: v*100,
        },
        'atm': {
            's': lambda v: v*1.01325,
            'us': lambda v: v/1.01325,
        },
        'torr': {
            's': lambda v: (v/760)*1.01325,
            'us': lambda v: (v/1.01325)*760,
        },
        'psia': {
            's': lambda v: (v/14.6959)*1.01325,
            'us': lambda v: (v/1.01325)*14.6959,
        },
        'psig': {
            's': lambda v: (1 + v/14.6959)*1.01325,
            'us': lambda v: (v/1.01325)*14.6959 - 1,
        },
    },
    'dH': {
        'cal/g': {
            's': lambda v, _: v,
            'us': lambda v, _: v,
        },
        'kcal/g': {
            's': lambda v, _: v*1000,
            'us': lambda v, _: v*1000,
        },
        'J/g': {
            's': lambda v, _: (v/4.184),
            'us': lambda v, _: v*4.184,
        },
        'kJ/g': {
            's': lambda v, _: (v/4.184)*1000,
            'us': lambda v, _: (v/1000)*4.184,
        },
        'cal/mol': {
            's': lambda v, mw: v/mw,
            'us': lambda v, mw: v*mw,
        },
        'kcal/mol': {
            's': lambda v, mw: v*1000/mw,
            'us': lambda v, mw: v*mw/1000,
        },
        'J/mol': {
            's': lambda v, mw: (v/4.184)/mw,
            'us': lambda v, mw: v*4.184*mw,
        },
        'kJ/mol': {
            's': lambda v, mw: (v/4.184)*1000/mw,
            'us': lambda v, mw: (v*4.184*mw)/1000,
        },
        'btu/lb': {
            's': lambda v, _: (v*252.164)/453.592,
            'us': lambda v, _: (v*453.592)/252.164,
        },
    },
    'Cp': {
        'cal/g/°C': {
            's': lambda v, _: v,
            'us': lambda v, _: v,
        },
        'kcal/g/°C': {
            's': lambda v, _: v*1000,
            'us': lambda v, _: v/1000,
        },
        'J/g/°C': {
            's': lambda v, _: (v/4.184),
            'us': lambda v, _: v*4.184,
        },
        'kJ/g/°C': {
            's': lambda v, _: (v/4.184)*1000,
            'us': lambda v, _: (v/1000)*4.184,
        },
        'kcal/mol/°C': {
            's': lambda v, mw: v*1000/mw,
            'us': lambda v, mw: v*mw/1000,
        },
        'kJ/mol/°C': {
            's': lambda v, mw: (v/4.184)*1000/mw,
            'us': lambda v, mw: (v*4.184*mw)/1000,
        },
    }
}
