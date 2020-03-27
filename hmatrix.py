import matplotlib.pyplot as plt, mpld3
import pandas as pd
import numpy as np

GREEN = '#10e831'
YELLOW = '#f2f745'
ORANGE = '#ffa500'
RED = '#fc0324'

# for some reason, in h_matrix.xlsx,the only options for colors are 0, 2, 3, 4
COLORS = {0: GREEN, 2: YELLOW, 3: ORANGE, 4: RED}

# number of "hazards" for each h-index
NUM_HAZARDS = 11

def max_h_plot(h_ids):
    # a list of the max h_nums in the plot
    max_h_nums = [0] * NUM_HAZARDS
    
    df = pd.read_excel("h_matrix.xlsx")
    
    for id in h_ids:
        # not all h-indecies are in the h_matrix.xlsx file
        if id not in list(df['Index']):
            continue

        row = df.loc[df['Index'] == id]
        nums = list(row.iloc[0])
        update_h_nums_if_necessary(max_h_nums, nums[2:])
        
    max_h_plot = {
        'flammability': COLORS[max_h_nums[0]],
        'reactivity': COLORS[max_h_nums[1]],
        'skinAbsorption': COLORS[max_h_nums[2]],
        'skinContact': COLORS[max_h_nums[3]],
        'eyeContact': COLORS[max_h_nums[4]],
        'respiratory': COLORS[max_h_nums[5]],
        'carcinogen': COLORS[max_h_nums[6]],
        'reproductiveHazard': COLORS[max_h_nums[7]],
        'sensitizer': COLORS[max_h_nums[8]],
        'other': COLORS[max_h_nums[9]],
        'ingestion': COLORS[max_h_nums[10]],
    }
    return max_h_plot

# given a row in the hmatrix, if any of the indicators are greater than what's currently in the 
# max_h_nums, this function will update the max plot to reflect the max indicator.

# For example:
# given max_h_nums = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 3]
# and numbers [1, 0, 2, 0, 0, 2, 2, 2, 2, 2, 1],
# max_h_nums will update to [1, 1, 2, 0, 0, 2, 2, 2, 2, 2, 3]
def update_h_nums_if_necessary(h_nums, nums):
    print(nums)
    for i in range(NUM_HAZARDS):
        if nums[i] > h_nums[i]:
            h_nums[i] = nums[i]

# def max_h_plot(h_ids):
#     columns = ('Flammability','Reactivity','Skin' 'absorption','Skin' 'Contact','Eye' 'Contact','Respiratory','Carcinogen','Reproductive' 'Hazard','Sensitizer','Other','Ingestion')

#     color_dict = {0:'#10e831',
#              2:'#f2f745',
#              3:'#FFA500',
#              4:'#fc0324'}
#     df = pd.read_excel("h_matrix.xlsx")
#     n = len(h_ids)
#     cell_text = []
#     colors = []
#     m_t = []
#     for i in range(n):
#         text = [""]*11

#         code = h_ids[i]
#         print('code: ', code)
#         if code in list(df['Index']):

#             a= df.loc[df['Index'] == code]
#             print('a: ', a)

#             b = list(a.iloc[0])
#             print('b: ', b)
#             c_n = b[2:]
#             m_t.append(c_n)

#     try:
#         m_t = list(np.max(np.array(m_t), axis=0))
#     except ValueError as e:
#         print(e)

#     clrs = [color_dict[int(x)] for x in m_t]
#     colors.append(clrs)
#     cell_text.append(text)

#     fig, ax = plt.subplots()
#     ax.axis('tight')
#     ax.axis('off')
#     the_table = ax.table(cellText=cell_text,cellColours=colors,
#                          colLabels=columns,loc='center',colWidths = [0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06, 0.06] )

#     the_table.auto_set_font_size(False)
#     the_table.set_fontsize(13)

#     the_table.scale(7,7)

#     plt.savefig('ch.png', bbox_inches='tight')
#     #plt.show()
#     return 'ch.png'