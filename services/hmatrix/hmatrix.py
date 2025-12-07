import pandas as pd
from models import HMatrixColumn

GREEN = '#7fd13b'
YELLOW = '#ffff00'
ORANGE = '#ffa500'
RED = '#c00000'

# For some reason, in h_matrix.xlsx, the only options for colors are 0, 2, 3, 4
COLORS = {0: GREEN, 2: YELLOW, 3: ORANGE, 4: RED}

# Number of "hazards" for each h-index
NUM_HAZARDS = 11

"""
    Generate one row for the hazard matrix based on the given list of h-indices
"""
def max_h_plot(h_ids) -> HMatrixColumn:
    # A list of the max h_nums in the plot
    max_h_nums = [0] * NUM_HAZARDS
    
    df = pd.read_excel("data/revised_h_matrix.xlsx")
    for id in h_ids.split(', '):
        # Not all h-indecies are in the h_matrix.xlsx file
        if id not in list(df['Index']):
            continue

        row = df.loc[df['Index'] == id]
        nums = list(row.iloc[0])
        update_h_nums_if_necessary(max_h_nums, nums[2:])
        
    plot = {
        'skinAbsorption': COLORS[max_h_nums[0]],
        'skinContact': COLORS[max_h_nums[1]],
        'eyeContact': COLORS[max_h_nums[2]],
        'respiratory': COLORS[max_h_nums[3]],
        'ingestion': COLORS[max_h_nums[4]],
        'sensitizer': COLORS[max_h_nums[5]],
        'carcinogen': COLORS[max_h_nums[6]],
        'reproductiveHazard': COLORS[max_h_nums[7]],
        'organToxicity': COLORS[max_h_nums[8]],
        'flammability': COLORS[max_h_nums[9]],
        'reactivityOrExplosivity': COLORS[max_h_nums[10]],
    }
    return HMatrixColumn(**plot)


"""
    Given a row in the hmatrix, if any of the indicators are greater than what's currently in the 
    max_h_nums, this function will update the max plot to reflect the max indicator.

    For example:
        given max_h_nums = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 3]
        and numbers [1, 0, 2, 0, 0, 2, 2, 2, 2, 2, 1],
        max_h_nums will update to [1, 1, 2, 0, 0, 2, 2, 2, 2, 2, 3]
"""
def update_h_nums_if_necessary(h_nums, nums):
    for i in range(NUM_HAZARDS):
        if nums[i] > h_nums[i]:
            h_nums[i] = nums[i]
