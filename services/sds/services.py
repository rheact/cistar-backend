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

    properties =[''] * len(letters)

    for i in range(len(letters)):
        letter = letters[i]
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
                property = re.search(r"[\d\.]+", property).group()
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

    num = re.search(r"\d+-\d{2}-\d", cprop, re.DOTALL).group()
    # remove newlines
    num = num.replace('\n', '')

    weight = re.search(r"\d+\.\d+ g/mol", cprop).group() #Mol wt.
    # remove ' g/mol' (6 chars)
    weight = weight[:6]
    return num, weight
    
def stability(l):
    stb = re.search(r"10\. STABILITY.+11\. T",text,re.DOTALL).group() #for stability
    print('STABILITY AND REACTIVITY')
    s = re.search(r"10\.1.+11\.",l,re.DOTALL).group()
    v =[0]*7
    idx = ['Reactivity','Chemical stability','Possibility of hazardous reactions','Conditions to avoid','Incompatible materials','Hazardous decomposition products formed under fire conditions','Other decomposition products']


    j = 1
    k = 2
    j += 1
    k += 1
    for i in range(0,6):
        try:
            if i==4:
                r = r"10\."+str(j)+".+""10\." +str(k)
                o = re.search(r,s,re.DOTALL).group()
                v[i] = re.search(r"\n.+\n\n",o).group()
                v[i] = v[i].replace('\n','').lower().strip()
                j = j + 1
                k = k + 1 
            if i==5:
                r = r"10\.6"+".+"+"\nIn"
                o = re.search(r,s,re.DOTALL).group()

                n = re.search(r"\n\n.+\nIn",o,re.DOTALL).group()
                h = re.findall(r"- .+\n",n)
                h[:] = [x.lstrip('-').replace('\n','').lower().strip() for x in h]
                for x in h:
                    v[i] = x
                    i+=1





            r = r"10\."+str(j)+".+""10\." +str(k)
            o = re.search(r,s,re.DOTALL).group()
            v[i] = re.search(r"\n\n.+\n\n",o).group()
            v[i] = v[i].replace('\n','').lower().strip()
            j = j + 1
            k = k + 1
        except:
            j = j + 1
            k = k + 1

    # for x,y in zip(idx,v):
    #     print(x+':')
    #     print(y+'\n')
    ###
    return v 
