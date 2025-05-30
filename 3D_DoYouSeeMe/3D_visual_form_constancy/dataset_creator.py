# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import os
import json

base_dir = "3D_DoYouSeeMe/form_constancy"

files = os.listdir(base_dir)

data_list = []
for file in files:
    if file.endswith(".json"):
        with open(os.path.join(base_dir, file), "r") as f:
            data = f.read()
        data = json.loads(data)
        question = data["question"]
        answer = data["answer"]
        num_shapes = data["num_shapes"]
        noise_amount = data["noise_amount"]
        data_list.append({
            "filename": os.path.splitext(file)[0] + ".png",
            "question": question,
            "answer": answer,
            "sweep": [num_shapes, noise_amount]
        })
import pandas as pd

df = pd.DataFrame(data_list)
df.to_csv(os.path.join(base_dir, "dataset_info.csv"), index=False)