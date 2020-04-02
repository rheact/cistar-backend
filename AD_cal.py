import pandas as pd

df = pd.read_excel("chem_data.xlsx")

def cal(cas,x,T=30,d_h=200):
    col = ['Chemical','LiqCp_A','LiqCp_B']
    df = pd.read_excel("chem_data.xlsx")
    a= df.loc[df['CAS'].isin(cas)][col]
    b = a[col].values
    n = len(b)
    m = 0
    cps = []
    for i in range(n):
        cp = b[i][1] + b[i][2]*T
        cps.append(cp)
        m+= x[i]*cp
        print("Cp of " + b[i][0] +": " + str(cp))

    print("Cp of Mixture:" + str(m))
    
    ad_t = d_h / m
    ad_p = (ad_t/T)**(1.4/0.4)
    
    print("Adiabatic Temperature: " + str(ad_t))
    print("Adiabatic Pressure: " + str(ad_p))
    
    #d_t = ad_t - T
    #d_p = ad_p - P

#Calling the functions
x = [0.25,0.25,0.25,0.25]
cas = ['75-07-0','64-19-7','108-24-7','67-64-1']

cal(cas,x)