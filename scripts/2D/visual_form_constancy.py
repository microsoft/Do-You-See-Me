# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import svgwrite
import random
from typing import List, Dict, Any
import os
import pandas as pd



class VisualDiscriminationTestGenerator:
    def __init__(self, size: int = 200):
        """
        Initialize the Visual Discrimination Test Generator.
        
        Args:
            size: Size of the SVG canvas (square)
        """
        self.size = size
        
    def get_random_coord(self, max_val: int) -> int:
        """Generate random coordinate within bounds."""
        return random.randint(10, max_val)
    
    def get_random_shape_params(self) -> Dict[str, Any]:
            """Generate random parameters for shape generation."""
            return {
                'x': self.get_random_coord(150),
                'y': self.get_random_coord(150),
                'size': 20 + self.get_random_coord(30),  # size between 20-50
                'rotation': self.get_random_coord(360)
            }
    
    def create_circle(self, dwg: svgwrite.Drawing, params: Dict[str, Any]) -> svgwrite.shapes.Circle:
        """Create a circle shape."""
        return dwg.circle(
            center=(params['x'], params['y']),
            r=params['size'] / 2,
            fill='none',
            stroke='black',
            stroke_width=2
        )
    
    def create_square(self, dwg: svgwrite.Drawing, params: Dict[str, Any]) -> svgwrite.shapes.Rect:
        """Create a square/rectangle shape."""
        # Apply aspect ratio modification if specified
        width = params['size']
        height = params['size']
        if 'aspect_ratio' in params:
            height *= params['aspect_ratio']
            
        rect = dwg.rect(
            insert=(params['x'], params['y']),
            size=(width, height),
            fill='none',
            stroke='black',
            stroke_width=2
        )
        
        # Apply transformations
        if 'rotation' in params:
            rect.rotate(params['rotation'], center=(
                params['x'] + width/2,
                params['y'] + height/2
            ))
            
        if params.get('mirror', False):
            rect.scale(-1, 1)
        
        return rect
    
    def create_triangle(self, dwg: svgwrite.Drawing, params: Dict[str, Any]) -> svgwrite.shapes.Polygon:
        """Create a triangle shape with possible modifications."""
        # Calculate base size with aspect ratio if specified
        width = params['size']
        height = params['size']
        if 'aspect_ratio' in params:
            height *= params['aspect_ratio']
            
        # Create points with possible asymmetry
        points = [
            (params['x'], params['y'] + height),  # bottom left
            (params['x'] + width, params['y'] + height),  # bottom right
            (params['x'] + width/2, params['y'])  # top middle
        ]
        
        # Create the triangle
        triangle = dwg.polygon(
            points=points,
            fill='none',
            stroke='black',
            stroke_width=2
        )
        
        # Apply transformations
        if 'rotation' in params:
            triangle.rotate(params['rotation'], center=(
                params['x'] + width/2,
                params['y'] + height/2
            ))
            
        if params.get('mirror', False):
            triangle.scale(-1, 1)
            
        return triangle
    
    def create_line(self, dwg: svgwrite.Drawing, params: Dict[str, Any]) -> svgwrite.shapes.Line:
        """Create a line shape."""
        line = dwg.line(
            start=(params['x'], params['y']),
            end=(params['x'] + params['size'], params['y'] + params['size']),
            stroke='black',
            stroke_width=2
        )
        if params['rotation']:
            line.rotate(params['rotation'], center=(
                params['x'] + params['size']/2,
                params['y'] + params['size']/2
            ))
        return line
    
    def generate_compound_shape(self) -> List[Dict[str, Any]]:
        """Generate a compound shape pattern."""
        num_shapes = random.randint(2, 10)  # 2-4 shapes
        shapes_data = []
        
        for _ in range(num_shapes):
            params = self.get_random_shape_params()
            shape_type = random.randint(0, 3)  # 0-3 for different shapes
            params['shape_type'] = shape_type
            shapes_data.append(params)
            
        return shapes_data
    
    def create_svg_from_shapes(self, shapes_data: List[Dict[str, Any]], filename: str) -> None:
        """Create SVG file from shape data."""
        dwg = svgwrite.Drawing(filename, size=(f"{self.size}px", f"{self.size}px"))
        
        for params in shapes_data:
            shape_type = params['shape_type']
            try:
                if shape_type == 0:
                    dwg.add(self.create_circle(dwg, params))
                elif shape_type == 1:
                    dwg.add(self.create_square(dwg, params))
                elif shape_type == 2:
                    dwg.add(self.create_triangle(dwg, params))
                elif shape_type == 3:
                    dwg.add(self.create_line(dwg, params))
                # print("success: ", params)    
            except Exception as e:
                print(e)
                # print("fail", params)    
        dwg.save()
    
    def generate_variations(self, base_pattern: List[Dict[str, Any]], sweep) -> List[List[Dict[str, Any]]]:

        """Generate variations of the base pattern."""
        variations = []
        rotation, aspect_ratio, size, shape_change = sweep
        # Add the original pattern
        variations.append(base_pattern)
        
        # Generate 3 variations with slight modifications
        for _ in range(3):
            variation = []
            for shape in base_pattern:
                modified_shape = shape.copy()
                
                # Apply random modifications with controlled probabilities
                for modification in [
                    # Rotation changes
                    lambda s: {'rotation': s['rotation'] + random.randint(rotation-2, rotation+2)},
                    
                    # Size variations (subtle changes)
                    lambda s: {'size': s['size'] * size},
                    
                    # Shape type changes (rare)
                    lambda s: {'shape_type': random.randint(1, 3) if shape_change else s['shape_type']},
                                        
                    # Proportional changes for rectangles and triangles
                    lambda s: {'aspect_ratio': aspect_ratio}
                ]:
                    # print(modification)
                    modified_shape.update(modification(modified_shape))
                
                # Ensure shapes stay within bounds
                modified_shape['x'] = max(0, min(modified_shape['x'], 150))
                modified_shape['y'] = max(0, min(modified_shape['y'], 150))
                
                variation.append(modified_shape)
            variations.append(variation)
            
        return variations
    
    def generate_test_item(self, output_dir: str = "test_items") -> Dict[str, Any]:
        """Generate a complete test item."""
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate base pattern
        base_pattern = self.generate_compound_shape()
        
        # Generate variations
        variations = self.generate_variations(base_pattern)
        
        # Create SVG files
        # Target pattern
        target_file = os.path.join(output_dir, "target.svg")
        self.create_svg_from_shapes(base_pattern, target_file)
        
        # Options
        option_files = []
        for i, variation in enumerate(variations):
            option_file = os.path.join(output_dir, f"option_{i+1}.svg")
            self.create_svg_from_shapes(variation, option_file)
            option_files.append(option_file)
        
        return {
            'target': target_file,
            'options': option_files,
            'correct_answer': 1  # First option is always the correct one
        }

    def create_test_presentation(self, shapes_data: Dict[str, List[Dict[str, Any]]], output_file: str) -> None:
            """
            Create a single SVG combining target and options in test presentation format.
            
            Args:
                shapes_data: Dictionary containing target and option shapes data
                output_file: Path to save the combined SVG
            """
            # Create larger SVG for the complete test item
            dwg = svgwrite.Drawing(output_file, size=("600px", "1000px"))
                # Add white background
            dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))
            
            # Add title
            dwg.add(dwg.text("Visual Discrimination Test", 
                            insert=(300, 40),
                            text_anchor="middle",
                            font_size=24,
                            font_family="Arial"))
            
            # Add target section
            dwg.add(dwg.text("Target Pattern", 
                            insert=(300, 80),
                            text_anchor="middle",
                            font_size=18,
                            font_family="Arial"))
            
            # Create target pattern group with translation
            target_group = dwg.g()
            target_group.translate(200, 100)  # Position the target pattern
            
            # Add shapes to target group
            for params in shapes_data['target']:
                shape_type = params['shape_type']
                if shape_type == 0:
                    target_group.add(self.create_circle(dwg, params))
                elif shape_type == 1:
                    target_group.add(self.create_square(dwg, params))
                elif shape_type == 2:
                    target_group.add(self.create_triangle(dwg, params))
                elif shape_type == 3:
                    target_group.add(self.create_line(dwg, params))
            
            dwg.add(target_group)
            
            # Add options section
            dwg.add(dwg.text("Options", 
                            insert=(300, 350),
                            text_anchor="middle",
                            font_size=18,
                            font_family="Arial"))
                        
            # Create option groups with translations
            for i, option_shapes in enumerate(shapes_data['options']):
                option_group = dwg.g()
                # Position options in 2x2 grid
                row = i // 2
                col = i % 2
                option_group.translate(100 + col * 250, 400 + row * 250)
                
                # Add option label
                dwg.add(dwg.text(f"Option {i+1}", 
                            insert=(175 + col * 250, 380 + row * 250),
                            text_anchor="middle",
                            font_size=14,
                            font_family="Arial"))
                
                # Add shapes to option group
                for params in option_shapes:
                    shape_type = params['shape_type']
                    if shape_type == 0:
                        option_group.add(self.create_circle(dwg, params))
                    elif shape_type == 1:
                        option_group.add(self.create_square(dwg, params))
                    elif shape_type == 2:
                        option_group.add(self.create_triangle(dwg, params))
                    elif shape_type == 3:
                        option_group.add(self.create_line(dwg, params))
                
                dwg.add(option_group)
            
            dwg.save()

    def generate_complete_test_item(self, sweep, output_file: str = "test_item.svg") -> Dict[str, Any]:
        """
        Generate a complete test item and save it as a single SVG file.
        
        Args:
            output_file: Path to save the combined SVG
            
        Returns:
            Dictionary containing test information including correct answer
        """
        # Generate base pattern
        base_pattern = self.generate_compound_shape()
        
        # Generate variations
        variations = self.generate_variations(base_pattern, sweep)
        
        # Create combined SVG
        shapes_data = {
            'target': base_pattern,
            'options': variations
        }
        
        idx = list(range(len(shapes_data['options'])))
        random.shuffle(idx)
        correct_option = idx.index(0)
        shapes_data['options'] = [shapes_data['options'][i] for i in idx]

        self.create_test_presentation(shapes_data, output_file)
        
        # return {
        #     'file': output_file,
        #     'correct_answer': correct_option+1  # First option is always the correct one
        # }
        return correct_option+1

rotation_list = [5, 25, 50]
aspect_ratio_list = [0.8, 1.1, 1.4]
size_list = [0.8, 1.1, 1.4]
shape_change = [0, 1]


import itertools
sweep_list = itertools.product(rotation_list, aspect_ratio_list, size_list, shape_change)


generator = VisualDiscriminationTestGenerator()
idx = 0
base_dir = "visual_discrimination/sweep/visual_form_constancy"
if not os.path.exists(base_dir):
    os.makedirs(base_dir)

data = []
for sweep in sweep_list:
    for _ in range(5):
        fname = f"{idx}.svg"
        answer = generator.generate_complete_test_item(output_file=os.path.join(base_dir, fname), sweep=sweep)
        data.append({
            'filename': fname,
            'answer': answer,
            'sweep': sweep
        })
        idx+=1

pd.DataFrame(data).to_csv(os.path.join(base_dir, "dataset_info.csv"), index=False)