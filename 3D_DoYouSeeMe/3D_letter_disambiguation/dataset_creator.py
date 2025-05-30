# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

# variation, dot_size, spacing, letter_number
import os
import pandas as pd
import json

# {
#     "scene": "skywalk",
#     "light": "left",
#     "dot_type": "cylinder",
#     "dot_size": 0.14,
#     "spacing": 0.5,
#     "dot_color": "red",
#     "background_dots": false,
#     "letters": [
#         "Q",
#         "P"
#     ]
# }

base_dir = "3D_DoYouSeeMe/letter_disambiguation"

files = os.listdir(base_dir)

data_list = []
for file in files:
    if file.endswith(".json"):
        with open(os.path.join(base_dir, file), "r") as f:
            data = f.read()
        data = json.loads(data)
        
        question = "In the scene, which letters do you see from left to right?"
        letters = data["letters"]
        answer = "".join(letters)
        
        variation = data["dot_type"]
        dot_size = data["dot_size"]
        spacing = data["spacing"]
        num_letters = len(letters)
        data_list.append({
            "filename": os.path.splitext(file)[0] + ".png",
            "question": question,
            "answer": answer,
            "sweep": [variation, dot_size, spacing, num_letters]
        })

df = pd.DataFrame(data_list)
df.to_csv(os.path.join(base_dir, "dataset_info.csv"), index=False)