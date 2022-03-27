import pandas as pd

GREEN = '#7fd13b'
YELLOW = '#ffff00'
ORANGE = '#ffa500'
RED = '#c00000'

# for some reason, in h_matrix.xlsx,the only options for colors are 0, 2, 3, 4
COLORS = {0: GREEN, 2: YELLOW, 3: ORANGE, 4: RED}

# number of "hazards" for each h-index
NUM_HAZARDS = 11

def max_h_plot(h_ids):
    # a list of the max h_nums in the plot
    max_h_nums = [0] * NUM_HAZARDS
    
    df = pd.read_excel("data/h_matrix.xlsx")
    for id in h_ids.split(', '):
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
    for i in range(NUM_HAZARDS):
        if nums[i] > h_nums[i]:
            h_nums[i] = nums[i]
