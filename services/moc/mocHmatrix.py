import pandas as pd
import json
from models import MOCHMatrix

GREEN = 'G'
YELLOW = 'Y'
ORANGE = 'O'
RED = 'R'

# for some reason, in h_matrix.xlsx,the only options for colors are 0, 2, 3, 4
COLORS = {0: GREEN, 2: YELLOW, 3: ORANGE, 4: RED}

HAZARDS = {
    0: 'skin absorption',
    1: 'skin contact',
    2: 'eye contact',
    3: 'respiratory',
    4: 'ingestion',
    5: 'sensitizer',
    6: 'carcinogen',
    7: 'reproductive hazard',
    8: 'organ toxicity',
    9: 'flammability',
    10: 'reactivity or explosivity'
}

# number of "hazards" for each h-index
NUM_HAZARDS = 11

def get_moc_hmatrix(hNumsMap) -> MOCHMatrix:
    # a list of the max h_nums in the plot
    total = [[] for i in range(NUM_HAZARDS)]
    results = {
        'level1': [],
        'level2': [],
        'level3': []
    }
    print(total)
    
    df = pd.read_excel("data/revised_h_matrix.xlsx")

    print(hNumsMap)

    hNumsMap = json.loads(hNumsMap)

    for hNums in hNumsMap.values():
        max_h_nums_single_chem = [0] * NUM_HAZARDS
        for id in hNums.split(', '):
            # not all h-indecies are in the h_matrix.xlsx file
            if id not in list(df['Index']):
                continue

            row = df.loc[df['Index'] == id]
            nums = list(row.iloc[0])
            update_h_nums_if_necessary(max_h_nums_single_chem, nums[2:])
        
        for i in range(NUM_HAZARDS):
            total[i].append(COLORS[max_h_nums_single_chem[i]])
        
        print(total)

    for i in range(NUM_HAZARDS):
        if i == 9:
            continue
        if 'R' in total[i]:
            # red color
            results['level3'].append(HAZARDS[i])
        elif 'O' in total[i]:
            # orange color
            results['level2'].append(HAZARDS[i])
        elif 'Y' in total[i] or 'G' in total[i]:
            results['level1'].append(HAZARDS[i])
    
    return MOCHMatrix(**results)

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
