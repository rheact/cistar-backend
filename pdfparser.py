
import re
import pdftotext

def parse(f):
    text = ''
    pdfFileObject = open(f, 'rb')
    pdf = pdftotext.PDF(pdfFileObject)
    for page in pdf:
        text += page
        
    pdfFileObject.close()

    h_numbers = get_h_numbers(text)
    phys_chem_properties = get_physical_chemical_properties(text)
    product_name = pname(text)
    cas_num, weight = num_weight(text)
    
    properties_list = [product_name]  + [weight] + [cas_num] + phys_chem_properties

    properties = convert_arr_to_dict(properties_list)
    properties['hNumbers'] = h_numbers
    return properties
# a: array of properties
# @return dict: dictionary of property name : value
def convert_arr_to_dict(a):
    dict = {}
    dict['productName'] = a[0]
    dict['molWt'] = a[1]
    dict['casNo'] = a[2]
    dict['ph'] = a[3]
    dict['boilingPt'] = a[4]
    dict['flashPt'] = a[5]
    dict['flammabilityLimits'] = a[6]
    dict['vapourPressure'] = a[7]
    dict['vapourDensity'] = a[8]
    dict['relDensity'] = a[9]
    dict['autoIgnitionTemp'] = a[10]
    dict['decompositionTemp'] = a[11]
    dict['viscosity'] = a[12]

    return dict

def get_physical_chemical_properties(text):
    #idx = ['Appearance','Odour','Odour Threshold','pH','Melting point','Initial boiling point','Flash point','Evaporation rate','Flammability','Explosive limits','Vapour pressure','Vapour density','Relative density','Water solubility','Partition coefficient','Auto-ignition temperature','Decomposition temperature','Viscosity','Explosive properties','Oxidizing properties']
    # Section 9 - Physical and Chemical Properties
    phys_chem = re.search(r"PHYSICAL AND.+9\.2", text, re.DOTALL|re.IGNORECASE).group() 
    p = re.split(r'\n', phys_chem)
    letters = ['d', 'f', 'g', 'j', 'k', 'l', 'm', 'p', 'q', 'r']
    idx = ['pH ',
        'Initial boiling point and boiling range ',
        'Flash point ',
        'Upper/lower flammability or explosive limits ',
        'Vapour pressure ',
        'Vapour density ',
        'Relative density ',
        'Auto-ignition temperature ',
        'Decomposition temperature ',
        'Viscosity '
    ]
    properties =['']*len(letters)

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

        # attempt to remove units from property
        try:
            property = re.search(r"[\d\.]+", property).group()
        except:
            property = 'No data available'
        properties[i] = property
        pass
    
    return properties

def get_h_numbers(text):
    # Section 2 - hazard info
    hazard_info = re.search(r"2\.1.+2\.2\s*GHS",text,re.DOTALL).group() #for h index
    try:
        # gonna be a dictionary of h_number : h_statement pairs
        return_dict = {}
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
            return_dict[num] =  h_statement
    except:
        return_dict = {}
    return return_dict
        
def pname(text):
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
    
# CAS # and molecular weight
def num_weight(text):
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
    return v 
