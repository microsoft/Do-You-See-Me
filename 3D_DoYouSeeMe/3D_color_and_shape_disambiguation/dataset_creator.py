# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import random
import ast
SEED=51
random.seed(SEED)


def generate_shape_color_question_and_answer(info):
    """
    Ask about a specific (shape, color) pair.
    
    Returns:
        question (str): e.g.
            "In the scene 'skywalk' under 'middle' lighting, how many black cones are there?"
        answer   (int)
    """
    # parse the stringified keys into real tuples
    parsed = {}
    for k, count in info.get("shape_color_counts", {}).items():
        shape, color = ast.literal_eval(k)
        parsed[(shape, color)] = count

    (shape, color), cnt = random.choice(list(parsed.items()))
    question = (
        f"In the scene, "
        f"how many {color} {shape}'s are there?"
    )
    return question, cnt


def generate_shape_question_and_answer(info):
    """
    Ask about the total number of a given shape, agnostic of color.
    
    Returns:
        question (str): e.g.
            "In the scene 'skywalk' under 'middle' lighting, how many cones are there in total?"
        answer   (int)
    """
    # first try the provided shape_counts
    shape_counts = info.get("shape_counts", {})
    
    # fallback: aggregate from shape_color_counts if needed
    if not shape_counts:
        agg = {}
        for k, count in info.get("shape_color_counts", {}).items():
            shape, _ = ast.literal_eval(k)
            agg[shape] = agg.get(shape, 0) + count
        shape_counts = agg

    shape, total = random.choice(list(shape_counts.items()))
    question = (
        f"In the scene, "
        f"how many {shape}'s are there in total?"
    )
    return question, total

import os
import json

base_dir = "3D_DoYouSeeMe/color_disambiguation"

os.listdir(base_dir)

data_list = []
for filename in os.listdir(base_dir):
    if filename.endswith(".json"):
        # print(filename)
        with open(os.path.join(base_dir, filename), "r") as f:
            data = f.read()
        data = json.loads(data)
        q, a = generate_shape_color_question_and_answer(data)

        num_shapes = data["num_shapes"]
        max_instances_per_shape = data["max_instances_per_shape"]
        min_visibility = data["min_visibility"]
        
        data_list.append({"filename": os.path.splitext(filename)[0] + ".png",
                          "question": q,
                          "answer": a,
                          "sweep": [num_shapes, max_instances_per_shape, min_visibility]})

import pandas as pd
df = pd.DataFrame(data_list)
df.to_csv(os.path.join(base_dir, "dataset_info.csv"), index=False)