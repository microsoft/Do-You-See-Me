import random
import re
from collections import defaultdict
SEED = 42
random.seed(SEED)

def generate_question_and_answer(grid_dict):
    """
    Generate a question + answer based on a grid dictionary.
    
    Returns:
        question (str): e.g.
            "In grid 1, starting from the torus at position (row 0, column 1),
             how many spheres are there to the right of it in the same row?"
        answer (int): the count of target shapes in that direction.
    """
    # 1. Parse all entries
    positions = []  # list of (grid_id, row, col, shape)
    for key, shape in grid_dict.items():
        m = re.match(r"grid_(\d+)_(\d+)_(\d+)", key)
        if not m:
            continue
        gid, r, c = map(int, m.groups())
        positions.append((gid, r, c, shape))

    # 2. Group by grid and compute bounds
    by_grid = defaultdict(list)
    for gid, r, c, shape in positions:
        by_grid[gid].append((r, c, shape))
    gid, cells = next(iter(by_grid.items()))
    rows = [r for r, c, _ in cells]
    cols = [c for r, c, _ in cells]
    max_row, max_col = max(rows), max(cols)

    # 3. Filter to interior cells if possible
    interior = [(r, c, s) for (r, c, s) in cells
                if 0 < r < max_row and 0 < c < max_col]
    if interior:
        ref_r, ref_c, ref_shape = random.choice(interior)
    else:
        # fallback for very thin grids
        ref_r, ref_c, ref_shape = random.choice(cells)

    # 4. Build possible directions (with predicates)
    directions = []
    if ref_c < max_col:
        directions.append((
            "to the right of it in the same row",
            lambda r, c: r == ref_r and c > ref_c
        ))
    if ref_c > 0:
        directions.append((
            "to the left of it in the same row",
            lambda r, c: r == ref_r and c < ref_c
        ))
    if ref_r < max_row:
        directions.append((
            "ahead it in the same column",
            lambda r, c: c == ref_c and r > ref_r
        ))
    if ref_r > 0:
        directions.append((
            "behind it in the same column",
            lambda r, c: c == ref_c and r < ref_r
        ))
    # Should always have at least one direction now
    direction_text, predicate = random.choice(directions)

    # 5. Pick a target shape (different from reference)
    other_shapes = list({s for _, _, s in cells if s != ref_shape})
    target_shape = random.choice(other_shapes)

    # 6. Compute the answer
    count = sum(
        1
        for (r, c, s) in cells
        if predicate(r, c) and s == target_shape
    )

    # 7. Formulate the question
    question = (
        f"In grid {gid}, starting from the {ref_shape} at position "
        f"(row {ref_r}, column {ref_c}), how many {target_shape}s are there "
        f"{direction_text}?"
    )

    return question, count, (max_row, max_col)

import os
import json

base_dir = "3D_DoYouSeeMe/visual_spatial"

os.listdir(base_dir)

data_list = []
for filename in os.listdir(base_dir):
    if filename.endswith(".json"):
        # print(filename)
        with open(os.path.join(base_dir, filename), "r") as f:
            data = f.read()
        data = json.loads(data)
        q, a, (max_row, max_col) = generate_question_and_answer(data)
        data_list.append({"filename": os.path.splitext(filename)[0] + ".png",
                          "question": q,
                          "answer": a,
                          "sweep": [max_row, max_col]})

import pandas as pd
df = pd.DataFrame(data_list)
df.to_csv(os.path.join(base_dir, "dataset_info.csv"), index=False)

        
        
