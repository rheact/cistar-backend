
# coding: utf-8

# In[ ]:


import re
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, XMLConverter, HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import BytesIO

def convert_pdf(path, format='text', codec='utf-8', password=''):
    rsrcmgr = PDFResourceManager()
    retstr = BytesIO()
    laparams = LAParams()
    if format == 'text':
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'html':
        device = HTMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    elif format == 'xml':
        device = XMLConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    else:
        raise ValueError('provide format, either text, html or xml!')
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue().decode()
    fp.close()
    device.close()
    retstr.close()
    return text


def phy_chem(l):
    #print('PHYSICAL AND CHEMICAL PROPERTIES')

    idx =['Appearance','Odour','Odour Threshold','pH','Melting point','Initial boiling point','Flash point','Evaporation rate','Flammability','Explosive limits','Vapour pressure','Vapour density','Relative density','Water solubility','Partition coefficient','Auto-ignition temperature','Decomposition temperature','Viscosity','Explosive properties','Oxidizing properties']
    s = re.search(r"a\).+9\.2",l,re.DOTALL).group()

    v =[0]*20
    try:

        o = re.search(r"a\).+b\)",s,re.DOTALL).group()
        v[0] = re.search(r"\n\n.+\n\n",o,re.DOTALL).group()
        v[0] = v[0].replace('\n','').lower()
    except:
        v[0] = 0


    j = "b"
    k = "c"

    for i in range(1,20):
        try:
            if j == 'i':
                o = re.search(r"i\).+j",s,re.DOTALL).group()
                v[i] = re.search(r"s\).+\n\n",o).group().lstrip('s)')
                v[i] = v[i].replace('\n','').lower().strip()
                j = chr(ord(j)+1)
                k = chr(ord(k)+1)
                continue
            if j == 't':
                o = re.search(r"t\).+9\.2",s,re.DOTALL).group()
                v[i] = re.search(r"\n\n.+\n\n",o).group()
                v[i] = v[i].replace('\n','').lower().strip()
                j = chr(ord(j)+1)
                k = chr(ord(k)+1)
                continue

            r = r"[^a]" + re.escape(j)+"\).+" + re.escape(k)+"\)"
            o = re.search(r,s,re.DOTALL).group()
            v[i] = re.search(r"\n\n.+\n\n",o).group()
            v[i] = v[i].replace('\n','').lower().strip()
            j = chr(ord(j)+1)
            k = chr(ord(k)+1)
            
        except:
            
            j = chr(ord(j)+1)
            k = chr(ord(k)+1)


    # for x,y in zip(idx,v):
    #     print(x+':')
    #     print(str(y)+'\n')
    return v


def hindex(l):
    try:
        h = re.findall(r'\bH\w{3}\b',l)
    except:
        h = []
    return h
        
def pname(l):
    a = re.search(r"CAS-No\. .+ \d",l,re.DOTALL).group()
    b = re.search(r":.+",a).group().lstrip(':').strip()
    return b
#     print('PRODUCT NAME:')
#     print(b)
    
    
def comp(l):
    c = re.search(r"\d+-\d{2}-\d{1}",l).group() #CAS
    # remove g/mol units
    m = re.search(r"\d+\.\d+ g/mol",l ).group() #Mol wt.
    #print('MOLECULAR WEIGHT:' , m)
    
    #print('\n')
    #print('CAS-NO:')
    return m,c
    
def stability(l):
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


#f =file()
def parse(f):
    t = convert_pdf(f,'text')
    hid = re.search(r"2\.1.+2.2  GHS",t,re.DOTALL).group() #for h index
    hNumbers = hindex(hid)

    p = re.search(r"9\. PHYSICAL AND.+9\.2",t,re.DOTALL).group() #for physical and chemical properties
    pnm = re.search(r"1\.1.+1\.2  Releva",t,re.DOTALL).group() #for product name
    cprop = re.search(r"3\.1.+4\. FIRST",t,re.DOTALL).group() #for maol. wt and CAS number
    stb = re.search(r"10\. STABILITY.+11\. T",t,re.DOTALL).group() #for stability
    a = ['']*23
    a[0] = pname(pnm)
    a[1],a[2] = comp(cprop)
    v = phy_chem(p)
    for i in range(3,23):
        a[i] = v[i-3]
    
    # format output to remove units
    mol_wt = a[1]
    a[1] = re.search(r"\d+\.\d+", mol_wt).group() # molecular weight

    melting_pt = a[7]
    a[7] = re.search(r"\d+ - \d+", melting_pt).group() # melting point

    boiling_pt = a[8]
    a[8] = re.search(r"\d+", boiling_pt).group() # boiling point

    flash_pt = a[9]
    a[9] = re.search(r"\d+", flash_pt).group() # flash point

    rel_density = a[15]
    a[15] = re.search(r"\d+\.\d+", rel_density).group() # relative density

    water_solubility = a[16]
    a[16] = re.search(r"\d+\.\d+", water_solubility).group() # water solubility

    partition_coeff = a[17]
    a[17] = re.search(r"\d+\.\d+", partition_coeff).group() # partition coefficient

    auto_ignition_temp = a[18]
    a[18] = re.search(r"\d+", str(auto_ignition_temp)).group() # auto-ignition temperature
    
    properties = convert_arr_to_dict(a)
    properties['hNumbers'] = hNumbers
    return properties

# a: array of properties
# @return dict: dictionary of property name : value
def convert_arr_to_dict(a):
    dict = {}
    dict['productName'] = a[0]
    dict['molWt'] = a[1]
    dict['casNo'] = a[2]
    dict['appearance'] = a[3]
    dict['odour'] = a[4]
    dict['odourThreshold'] = a[5]
    dict['ph'] = a[6]
    dict['meltingPt'] = a[7]
    dict['boilingPt'] = a[8]
    dict['flashPt'] = a[9]
    dict['evaporationRate'] = a[10]
    dict['flammability'] = a[11]
    dict['flammabilityLimits'] = a[12]
    dict['vapourPressure'] = a[13]
    dict['vapourDensity'] = a[14]
    dict['relDensity'] = a[15]
    dict['waterSolubility'] = a[16]
    dict['partitionCoeff'] = a[17]
    dict['autoIgnitionTemp'] = a[19]
    dict['decompositionTemp'] = a[20]
    dict['viscosity'] = a[21]
    dict['explosiveProperties'] = a[22]
    return dict

    

# print('\n')
# pname(pnm)
# print('\n')
# comp(cprop)
# print('\n')
# hindex(hid)
# print('\n')
# phy_chem(p)
# print('\n')
# stability(stb)

