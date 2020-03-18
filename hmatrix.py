import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def h_plot(h_ids):
    columns = ('H statement','Statement','Flammability','Reactivity','Skin' 'absorption','Skin' 'Contact','Eye' 'Contact','Respiratory','Carcinogen','Reproductive' 'Hazard','Sensitizer','Other','Ingestion')
    color_dict = {0:'#10e831',
             2:'#f2f745',
             3:'#FFA500',
             4:'#fc0324'}
    df = pd.read_excel("H_matrix.xlsx")
    n = len(h_ids)
    cell_text = []
    colors = []
    for i in range(n):
        text = [""]*13
        
        code = h_ids[i]
        if code in list(df['Index']):
                              
            a= df.loc[df['Index'] == code]
            b = list(a.iloc[0])
            b[1]=str(b[1])
            b[1] = b[1].replace(u'\xa0', u' ')
            text[0] = b[0]
            text[1] = b[1]
            c_n = b[2:]
            clrs = [color_dict[int(x)] for x in c_n]
            clrs = ['w']*2+clrs
            cell_text.append(text)
            colors.append(clrs)
            
    if cell_text:
        #plt.figure(figsize=(20,10))

        fig, ax = plt.subplots()
        ax.axis('tight')
        ax.axis('off')
        the_table = ax.table(cellText=cell_text,cellColours=colors,
                             colLabels=columns,loc='center',colWidths = [0.06, 0.23, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06] )

        
        the_table.auto_set_font_size(False)
        the_table.set_fontsize(13)
        
        the_table.scale(7,7)
        
        plt.savefig('test.png', bbox_inches='tight')
        
        
        #plt.show()
        #plt.savefig('test2png.png', dpi=100)


def max_h_plot(h_ids):
    columns = ('Flammability','Reactivity','Skin' 'absorption','Skin' 'Contact','Eye' 'Contact','Respiratory','Carcinogen','Reproductive' 'Hazard','Sensitizer','Other','Ingestion')
    color_dict = {0:'#10e831',
             2:'#f2f745',
             3:'#FFA500',
             4:'#fc0324'}
    df = pd.read_excel("H_matrix.xlsx")
    n = len(h_ids)
    cell_text = []
    colors = []
    m_t = []
    for i in range(n):
        text = [""]*11
        
        code = h_ids[i]
        if code in list(df['Index']):
                              
            a= df.loc[df['Index'] == code]
            b = list(a.iloc[0])

            c_n = b[2:]
            m_t.append(c_n)
            
            

    
    m_t = list(np.max(np.array(m_t), axis=0))
    
    clrs = [color_dict[int(x)] for x in m_t]
    colors.append(clrs)
    cell_text.append(text)
            
    
    

    fig, ax = plt.subplots()
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=cell_text,cellColours=colors,
                         colLabels=columns,loc='center',colWidths = [0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06] )


    the_table.auto_set_font_size(False)
    the_table.set_fontsize(13)

    the_table.scale(7,7)

    plt.savefig('ch.png', bbox_inches='tight')


    plt.show()
    

#call this function
# h_plot(['H200','H350','H315','H373'])
# max_h_plot(['H200','H350','H315','H373'])