import ast
import pandas as pd
import os
import math
import random
random.seed(0)


dir_path = "visual_discrimination/sweep/geometric_dataset"
df = pd.read_csv(os.path.join(dir_path, "dataset_dump.csv"))

'''
The dataset_dump.csv file contains the following columns:
1. filename: SVG filename of the image
2. shape_dictionary: It contains shape name as the key and corresponding count as the value
'''

data = []
for index, row in df.iterrows():
    shape_dict = ast.literal_eval(row['shape_dictionary'])
    filename = row['filename']
    sweep = ast.literal_eval(row['sweep'])
    innerlist = []
    for shape, count in shape_dict.items():
        question = f"Count the total number of {shape}s in the image, including each concentric {shape} separately. For example, if there is one {shape} with 2 inner concentric rings, that counts as 3 {shape}s. Respond with only a number."
        answer = count
        innerlist.append({
            'filename': filename,
            'question': question,
            'answer': answer,
            'sweep': sweep
        })
    innerlist = random.sample(innerlist, 1)
    data.extend(innerlist)

df = pd.DataFrame(data)
df.to_csv(os.path.join(dir_path, "dataset_info.csv"), index=False)
