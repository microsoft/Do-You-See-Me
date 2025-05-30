# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import random
import os
import pandas as pd


import random

import random

def generate_multiple_grids(k=3, rows=4, cols=4, cell_size=50, padding=10, grid_spacing=30, boundary_padding=20):
    """
    Generate K grids in a horizontal layout within a single SVG.
    
    Args:
        k (int): Number of grids to generate
        rows (int): Number of rows in each grid
        cols (int): Number of columns in each grid
        cell_size (int): Size of each cell
        padding (int): Padding between cells
        grid_spacing (int): Spacing between grids
        boundary_padding (int): Padding at the left and right edges of the SVG
    
    Returns:
        tuple: (svg_content, list_of_spatial_dicts)
    """
    # 1. Calculate dimensions
    single_grid_width = cols * (cell_size + padding)
    single_grid_height = rows * (cell_size + padding)
    total_width = k * single_grid_width + (k-1) * grid_spacing + 2 * boundary_padding  # Add padding to both sides
    
    # 2. Initialize SVG
    svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="{total_width}" height="{single_grid_height}" xmlns="http://www.w3.org/2000/svg">
    <!-- White background -->
    <rect width="{total_width}" height="{single_grid_height}" fill="white"/>
'''
    
    # 3. Initialize list to store spatial dictionaries
    spatial_dicts = []
    
    # 4. Generate each grid
    for grid_num in range(k):
        # Initialize spatial dictionary for this grid
        current_spatial_dict = {}
        
        # Calculate grid offset (include boundary padding)
        grid_offset_x = boundary_padding + grid_num * (single_grid_width + grid_spacing)
        
        # Optional: Add grid boundary for visualization
        svg_content += f'''    <rect x="{grid_offset_x}" y="0" 
            width="{single_grid_width}" height="{single_grid_height}" 
            fill="none" stroke="black" stroke-width="3"/>
'''
        
        # Generate cells for current grid
        for row in range(rows):
            for col in range(cols):
                # Calculate cell position
                x = grid_offset_x + col * (cell_size + padding)
                y = row * (cell_size + padding)
                
                # Generate random shape and fill
                shape = random.choice(['square', 'circle', 'triangle'])
                fill = random.choice(['white', 'black'])
                
                # Store in spatial dictionary
                current_spatial_dict[(row, col)] = (shape, fill)
                
                # Generate SVG element based on shape
                if shape == 'square':
                    svg_content += f'''    <rect x="{x}" y="{y}" 
                        width="{cell_size}" height="{cell_size}" 
                        fill="{fill}" stroke="black" stroke-width="2"/>
'''
                elif shape == 'circle':
                    cx = x + cell_size/2
                    cy = y + cell_size/2
                    r = cell_size/2
                    svg_content += f'''    <circle cx="{cx}" cy="{cy}" r="{r}"
                        fill="{fill}" stroke="black" stroke-width="2"/>
'''
                else:  # triangle
                    points = f"{x + cell_size/2},{y} {x},{y + cell_size} {x + cell_size},{y + cell_size}"
                    svg_content += f'''    <polygon points="{points}"
                        fill="{fill}" stroke="black" stroke-width="2"/>
'''
        
        # Add current grid's spatial dictionary to list
        spatial_dicts.append(current_spatial_dict)
    
    # 5. Close SVG
    svg_content += '</svg>'
    
    # 6. Save to file (optional)
    with open('multiple_grids.svg', 'w') as f:
        f.write(svg_content)
    
    return svg_content, spatial_dicts

rows_list = [3, 6, 9]
cols_list = [3, 6, 9]
num_grids_list = [1, 3, 5]

import itertools

sweep_list = itertools.product(rows_list, cols_list, num_grids_list)

idx = 0
data = []

base_dir = "visual_discrimination/sweep/visual_spatial"
if not os.path.exists(base_dir):
    os.makedirs(base_dir)
    
for sweep in sweep_list:
    for _ in range(10):
        fname = f"{idx}.svg"
        rows, cols, num_grids = sweep
        svg, dict = generate_multiple_grids(k=num_grids, rows=rows, cols=cols, cell_size=50, padding=5, grid_spacing=50)
        with open(os.path.join(base_dir, fname), 'w') as f:
            f.write(svg)
        data.append({"name": fname, "spatial_dict": dict, "sweep": sweep})
        idx += 1
df = pd.DataFrame(data)
df.to_csv(os.path.join(base_dir, "dataset_dump.csv"), index=False)
