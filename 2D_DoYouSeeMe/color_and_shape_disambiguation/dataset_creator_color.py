# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import pandas as pd
import ast
import random
random.seed(0)
import math
# read dataset_info.csv
data = pd.read_csv('visual_discrimination/sweep/color_and_shape_disambiguation/dataset_dump.csv')
DATA_SAMPLE_RATIO = 0.5
'''
Eg: dataset_info.csv
filename,shape_dictionary,color_dictionary
easy_1.svg,{'triangle': 3},"{('triangle', 'yellow'): 1, ('triangle', 'orange'): 1, ('triangle', 'green'): 1}"
medium_1.svg,"{'octagon': 3, 'cross': 6, 'star': 5}","{('octagon', 'red'): 1, ('octagon', 'gray'): 2, ('cross', 'yellow'): 2, ('cross', 'green'): 1, ('cross', 'purple'): 1, ('cross', 'blue'): 1, ('cross', 'orange'): 1, ('star', 'green'): 1, ('star', 'orange'): 1, ('star', 'blue'): 2, ('star', 'black'): 1}"

easy_1.svg is the file name, it contains 1 yellow triangle, 1 orange triangle and 1 green triangle.

Thus, a maximum number of questions that ca be asked for an image is the number of keys in the color_dictionary.
'''

# dataset list of dictionary row enteries
dataset = []
    
for idx, row in data.iterrows():
    shape_dict = ast.literal_eval(row['shape_dictionary'])
    color_dict = ast.literal_eval(row['color_dictionary'])
    filename = row['filename']
    sweep = row['sweep']


    for (shape, color), count in random.sample(list(color_dict.items()), math.ceil(DATA_SAMPLE_RATIO*len(color_dict))):
        question = f"Count the number of {shape}'s that are {color}."
        answer = count
        data = {
            'filename': filename,
            'question': question,
            'answer': answer,
            'sweep': sweep
        }
        dataset.append(data)
pd.DataFrame(dataset).to_csv('visual_discrimination/sweep/color_and_shape_disambiguation/dataset_info.csv', index=False)