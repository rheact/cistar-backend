import pandas as pd

df = pd.read_excel("chem_data.xlsx")

def cal(cas,x,T=30,d_h=200):
    col = ['Chemical','LiqCp_A','LiqCp_B']
    df = pd.read_excel("chem_data.xlsx")
    a= df.loc[df['CAS'].isin(cas)][col]
    b = a[col].values
    print('b: ', b)
    n = len(b)
    m = .373
    cps = []
    # for i in range(n):
    #     cp = b[i][1] + b[i][2]*T
    #     cps.append(cp)
    #     m+= x[i]*cp
    #     print("Cp of " + b[i][0] +": " + str(cp))

    print("Cp of Mixture:" + str(m))
    
    #ad_t = d_h / m
    ad_t = -57.1 / .373
    ad_p = (ad_t/T)**(1.4/0.4)
    
    print('type: ', type(ad_p))
    print(ad_p)
    print("Adiabatic Temperature: " + str(ad_t))
    print("Adiabatic Pressure: " + str(ad_p))
    
    #d_t = ad_t - T
    #d_p = ad_p - P

#Calling the functions
#x = [0.25,0.25,0.25,0.25]
#cas = ['75-07-0','64-19-7','108-24-7','67-64-1']


# Calculation block example
# weighted average
x = [0.16, 0.16, 0.16, 0.17, 0.17, 0.17]
cas = ['65-85-0', '7647-01-0', '7664-93-9', '7446-11-9', '98-07-7', '7732-18-5']

cal(cas,x,30, -57.1)