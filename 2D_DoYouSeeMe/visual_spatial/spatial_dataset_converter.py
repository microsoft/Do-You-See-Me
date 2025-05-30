# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import os
import pandas as pd
import random
from typing import Dict, List, Tuple, Any, Optional

class MultiGridQuestionGenerator:
    def __init__(self, spatial_dicts: List[Dict]):
        """
        Initialize with a list of spatial dictionaries, each representing one grid
        
        Args:
            spatial_dicts: List of dictionaries, where each dictionary maps (row, col) 
                          to (shape, color) for one grid
        """
        self.spatial_dicts = spatial_dicts
        self.num_grids = len(spatial_dicts)
        self.grid_dimensions = [self._get_grid_dimensions(d) for d in spatial_dicts]
        self.shapes = ['triangle', 'square', 'circle']
        self.colors = ['black', 'white']
        
    def _get_grid_dimensions(self, spatial_dict: Dict) -> Tuple[int, int]:
        """Calculate dimensions for a single grid"""
        max_row = max(pos[0] for pos in spatial_dict.keys())
        max_col = max(pos[1] for pos in spatial_dict.keys())
        return (max_row + 1, max_col + 1)
    
    def _get_object_at_position(self, grid_idx: int, row: int, col: int) -> Tuple[str, str]:
        """Get object at position in specified grid"""
        return self.spatial_dicts[grid_idx].get((row, col), (None, None))

    def _count_objects_same_row(self, grid_idx: int, row: int, col: int, 
                              direction: str,
                              color: Optional[str] = None, 
                              shape: Optional[str] = None) -> int:
        """Count objects in same row in specified direction for given grid"""
        rows, cols = self.grid_dimensions[grid_idx]
        
        if not (0 <= row < rows and 0 <= col < cols):
            return -1
            
        if direction == 'right' and col >= cols - 1:
            return -1
        if direction == 'left' and col <= 0:
            return -1
            
        count = 0
        if direction == 'right':
            range_to_check = range(col + 1, cols)
        else:  # left
            range_to_check = range(col - 1, -1, -1)
            
        for c in range_to_check:
            curr_shape, curr_color = self._get_object_at_position(grid_idx, row, c)
            matches = True
            if color and curr_color != color:
                matches = False
            if shape and curr_shape != shape:
                matches = False
            if matches:
                count += 1
        return count

    def _count_objects_same_column(self, grid_idx: int, row: int, col: int,
                                 direction: str,
                                 color: Optional[str] = None,
                                 shape: Optional[str] = None) -> int:
        """Count objects in same column in specified direction for given grid"""
        rows, cols = self.grid_dimensions[grid_idx]
        
        if not (0 <= row < rows and 0 <= col < cols):
            return -1
            
        if direction == 'up' and row <= 0:
            return -1
        if direction == 'down' and row >= rows - 1:
            return -1
            
        count = 0
        if direction == 'up':
            range_to_check = range(row - 1, -1, -1)
        else:  # down
            range_to_check = range(row + 1, rows)
            
        for r in range_to_check:
            curr_shape, curr_color = self._get_object_at_position(grid_idx, r, col)
            matches = True
            if color and curr_color != color:
                matches = False
            if shape and curr_shape != shape:
                matches = False
            if matches:
                count += 1
        return count

    def _gen_directional_count_question(self) -> Optional[Dict[str, Any]]:
        """Generate a question about counting objects in a specific direction"""
        # Choose a random grid
        grid_idx = random.randint(0, self.num_grids - 1)
        rows, cols = self.grid_dimensions[grid_idx]
        
        # Choose direction and appropriate position constraints
        direction = random.choice(['left', 'right', 'up', 'down'])
        
        if direction == 'right':
            row = random.randint(0, rows - 1)
            col = random.randint(0, cols - 2)  # Avoid rightmost
        elif direction == 'left':
            row = random.randint(0, rows - 1)
            col = random.randint(1, cols - 1)  # Avoid leftmost
        elif direction == 'up':
            row = random.randint(1, rows - 1)  # Avoid topmost
            col = random.randint(0, cols - 1)
        else:  # down
            row = random.randint(0, rows - 2)  # Avoid bottommost
            col = random.randint(0, cols - 1)
            
        base_shape, base_color = self._get_object_at_position(grid_idx, row, col)
        
        # Randomly choose what to count
        count_type = random.choice(['color', 'shape', 'both'])
        target_color = random.choice(self.colors) if count_type in ['color', 'both'] else None
        target_shape = random.choice(self.shapes) if count_type in ['shape', 'both'] else None
        
        # Generate count based on direction
        if direction in ['left', 'right']:
            count = self._count_objects_same_row(grid_idx, row, col, direction, target_color, target_shape)
        else:
            count = self._count_objects_same_column(grid_idx, row, col, direction, target_color, target_shape)
            
        # Construct question text
        what_to_count = ""
        if count_type == 'color':
            what_to_count = f"{target_color} objects"
        elif count_type == 'shape':
            what_to_count = f"{target_shape}s"
        else:
            what_to_count = f"{target_color} {target_shape}s"
            
        question = (
            f"In grid {grid_idx + 1}, starting from the {base_color} {base_shape} at position "
            f"(row {row + 1}, column {col + 1}), how many {what_to_count} are there {direction} "
            f"of it in the same {'row' if direction in ['left', 'right'] else 'column'}?"
        )
            
        return {
            "question": question,
            "answer": count,
            "type": f"count_{direction}",
            "grid_idx": grid_idx
        }

    def generate_question_set(self, num_questions: int = 5) -> List[Dict[str, Any]]:
        """Generate a set of unique questions across all grids"""
        questions = []
        attempts = 0
        max_attempts = num_questions * 3
        
        question_generators = [
            self._gen_directional_count_question,
            # Add other question generators here
        ]
        
        while len(questions) < num_questions and attempts < max_attempts:
            gen_func = random.choice(question_generators)
            question = gen_func()
            if question and not any(self._are_similar_questions(question, q) for q in questions):
                questions.append(question)
            attempts += 1
            
        return questions

    def _are_similar_questions(self, q1: Dict[str, Any], q2: Dict[str, Any]) -> bool:
        """Check if two questions are too similar"""
        if q1['type'] != q2['type'] or q1['grid_idx'] != q2['grid_idx']:
            return False
        return q1['question'] == q2['question']


def process_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the dataset to generate questions for each set of grids
    
    Args:
        df: DataFrame with 'name' and 'spatial_dict' columns
        
    Returns:
        DataFrame with filename, question, answer columns
    """
    dataset = []
    
    for idx, row in df.iterrows():
        print(f"Processing {row['name']}")
        generator = MultiGridQuestionGenerator(row['spatial_dict'])
        questions = generator.generate_question_set(num_questions=random.randint(1, 5))
        
        for q in questions:
            q['filename'] = row['name']
            q['sweep'] = row['sweep']
        dataset.extend(questions)
        print("=====================================")
        
    return pd.DataFrame(dataset)[['filename', 'question', 'answer', 'sweep']]

import ast

df = pd.read_csv("visual_discrimination/sweep/visual_spatial/dataset_dump.csv")
df['spatial_dict'] = df.apply(lambda x: ast.literal_eval(x['spatial_dict']), axis=1)
df["sweep"] = df.apply(lambda x: ast.literal_eval(x["sweep"]), axis=1)

dataset = process_dataset(df)

dataset.to_csv("visual_discrimination/sweep/visual_spatial/dataset_info.csv", index=False)