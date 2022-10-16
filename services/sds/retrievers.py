import re

def get_explosion_limits(text):
    """
    Upper/lower explosion limits are an interesting case so I decided to
    separate them from the rest of the physical/chemical properties
    """
    # Section 9 - Physical and Chemical Properties
    phys_chem = re.search(r"PHYSICAL AND.+9\.2", text, re.DOTALL|re.IGNORECASE).group()
    regex = r"j\).+k\)"
    limits = re.search(regex, phys_chem, re.DOTALL).group()
    limits = limits.replace('\n', '')

    # remove extraneous spaces
    limits = " ".join(limits.split())

    try:
        limits = re.findall(r"[\d\.]+", limits)
        upper = limits[0]
        lower = limits[1]
    except:
        upper = 'No data available'
        lower = 'No data available'

    return upper, lower

def get_physical_chemical_properties(text):
    #idx = ['Appearance','Odour','Odour Threshold','pH','Melting point','Initial boiling point','Flash point','Evaporation rate','Flammability','Explosive limits','Vapour pressure','Vapour density','Relative density','Water solubility','Partition coefficient','Auto-ignition temperature','Decomposition temperature','Viscosity','Explosive properties','Oxidizing properties']
    # Section 9 - Physical and Chemical Properties
    phys_chem = re.search(r"PHYSICAL AND.+9\.2", text, re.DOTALL|re.IGNORECASE).group() 
    letters = ['d', 'f', 'g', 'k', 'l', 'm', 'p', 'q', 'r']
    idx = ['pH ',
        'Initial boiling point and boiling range ',
        'Flash point ',
        'Vapour pressure ',
        'Vapour density ',
        'Relative density ',
        'Auto-ignition temperature ',
        'Decomposition temperature ',
        'Viscosity '
    ]

    properties = [''] * len(letters)

    for i, letter in enumerate(letters):
        next_letter = chr(ord(letter) + 1)
        # get all data between 2 letters [letter1]) and [letter2])
        regex = r"" + letter + "\)" + ".+" + next_letter + "\)"

        # last iteration, so we look for start of next section (9.2)
        if letter == 't':
            next_letter = '9.2'

        property = re.search(regex, phys_chem, re.DOTALL).group()

        # all of these start with [a])\n \n - 5 chars
        property = property[5:]

        # remove new lines
        property = property.replace('\n', '')

        # remove extraneous spaces
        property = " ".join(property.split())

        # remove the property name so the first thing is just the value
        property = property.replace(idx[i], '')

        # take from start of substring until [next_letter])
        property = property[0: property.find(next_letter + ')')]
        
        # strange case
        if 'No data available' in property:
            property = 'No data available'
        else:
            # attempt to remove units from property
            try:
                property = re.search(r"-?[\d\.,]+", property).group()
                property = property.replace(',','')
            except:
                property = 'No data available'

        properties[i] = property
        
    return properties

def get_h_numbers(text):
    """
    Returns an string with all the h-Nums, sepparated by commas
    and a string with all the h-statements, sepparated by newline
    """
    # Section 2 - hazard info
    hazard_info = re.search(r"2\.1.+2\.2\s*GHS",text,re.DOTALL).group() #for h index
    try:
        return_nums = ''
        return_statements = ''

        # just get h-statements
        osha_hcs = '(OSHA HCS)'
        hazard_info = hazard_info[hazard_info.find(osha_hcs) + len(osha_hcs):]
        # remove new lines
        hazard_info = hazard_info.replace('\n', '')
        # remove extraneous spaces
        hazard_info = " ".join(hazard_info.split())
        # find all lines of the form [H-STATEMENT], [HXXX]
        h_numbers = re.findall(r'\w.*?,\s*H\d{3}', hazard_info, re.DOTALL)
        for h_num in h_numbers:
            last_comma = h_num.rfind(',')
            num = h_num[last_comma + 2:]
            h_statement = h_num[:last_comma]
            return_nums += num + ', '
            return_statements += h_statement + '\n'
        
        # trim last ', ' and last '\n' from return value
        return_nums = return_nums[:-2]
        return_statements = return_statements[:-1]
    except:
        return_nums = ''
        return_statements = ''

    return return_nums, return_statements
        
def get_product_name(text):
    # section 1.1 - Product name
    pnm = re.search(r"1\.1.+1\.2\s*Releva", text, re.DOTALL).group()
    a = re.search(r"Product name\s*:.+Product Number",pnm,re.DOTALL).group()
    # remove "Product Name : " and "Product Number"
    a = a.replace('\n', '')
    
    # remove extraneous spaces
    a = " ".join(a.split())
    
    b = a.replace('Product name : ', '')
    b = b.replace('Product Number', '')

    return b
    
def get_CAS_weight(text):
    """
    CAS # and molecular weight
    """
    # Section 3 - composition/information on ingredients
    cprop = re.search(r"COMPOSITION.+FIRST", text, re.DOTALL|re.IGNORECASE).group() #for maol. wt and CAS number
    cas_num = "UNKOWN"
    s = re.search(r"(\d+-\d{2}-\d)", cprop, re.DOTALL)
    if s is not None:
        cas_num = s.group(1)
        cas_num = cas_num.replace('\n', '') # Remove newlines

    # Mol wt.
    weight = "UNKNOWN"
    s = re.search(r"(\d+\.\d+) g/mol", cprop)
    if s is not None:
        weight = s.group(1)
    return cas_num, weight

