import svgwrite
import random
from typing import List, Dict, Any, Tuple
import os
import numpy as np
import pandas as pd
from tqdm import tqdm 

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
    
    def generate_compound_shape(self, num_shapes) -> List[Dict[str, Any]]:
        shapes_data = []
        
        for _ in range(num_shapes):
            params = self.get_random_shape_params()
            shape_type = random.randint(0, 3)  # 0-3 for different shapes
            params['shape_type'] = shape_type
            shapes_data.append(params)
            
        return shapes_data

    def get_random_coord(self, max_val: int) -> int:
        """Generate random coordinate within bounds."""
        return random.randint(10, max_val)
    
    def generate_background(self, dwg: svgwrite.Drawing, density: float = 0.1) -> List[svgwrite.base.BaseElement]:
        """
        Generate background noise elements.
        
        Args:
            dwg: SVG drawing object
            density: Controls how dense the background noise should be (0.0 to 1.0)
            
        Returns:
            List of background elements
        """
        background_elements = []
        
        # Calculate number of elements based on density
        num_elements = int((self.size * self.size * density) / 100)  # Adjust divisor to control density
        
        for _ in range(num_elements):
            element_type = random.choice(['line', 'dot', 'rectangle'])
            x = self.get_random_coord(self.size - 20)
            y = self.get_random_coord(self.size - 20)
            
            if element_type == 'line':
                # Create random lines
                length = random.randint(5, 30)
                angle = random.randint(0, 360)
                end_x = x + length * random.random()
                end_y = y + length * random.random()
                element = dwg.line(
                    start=(x, y),
                    end=(end_x, end_y),
                    stroke='black',
                    stroke_width=1
                )
                
            elif element_type == 'dot':
                # Create small circles
                element = dwg.circle(
                    center=(x, y),
                    r=random.randint(1, 3),
                    fill='black',
                    stroke='none'
                )
                
            else:  # rectangle
                # Create small rectangles
                width = random.randint(3, 15)
                height = random.randint(3, 15)
                element = dwg.rect(
                    insert=(x, y),
                    size=(width, height),
                    fill='none',
                    stroke='black',
                    stroke_width=1
                )
            background_elements.append(element)
            
        return background_elements

    def create_svg_from_shapes(self, shapes_data: List[Dict[str, Any]], 
                             filename: str,
                             include_background: bool = False,
                             background_density: float = 0.1) -> None:
        """Create SVG file from shape data with optional background."""
        dwg = svgwrite.Drawing(filename, size=(f"{self.size}px", f"{self.size}px"))
        
        # Add background first if included
        if include_background:
            background_elements = self.generate_background(dwg, background_density)
            for element in background_elements:
                dwg.add(element)
        
        # Add main shapes
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
            except Exception as e:
                print(f"Error creating shape: {e}")
                
        dwg.save()
    

    def generate_variations(self, base_pattern: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Generate 4 specific variations of the base pattern with rotations and random modifications.
        
        Returns:
            List of variations, each containing shape data
        """
        variations = []
        
        # 1. Exact copy with background (background is added during SVG creation)
        variations.append(base_pattern.copy())
        
        def apply_random_rotation(pattern: List[Dict[str, Any]]) -> None:
            """Apply random rotation to all shapes in the pattern"""
            rotation = random.uniform(15, 20) if random.random() > 0.5 else random.uniform(-20, -15)
            for shape in pattern:
                current_rotation = shape.get('rotation', 0)
                shape['rotation'] = current_rotation + rotation
        
        def create_variation(base: List[Dict[str, Any]], 
                           remove_shapes: bool = False, 
                           move_shapes: bool = False,
                           num_shapes_to_remove: int = 1) -> List[Dict[str, Any]]:
            """Create a variation with specified modifications"""
            variation = [shape.copy() for shape in base]
            
            # Apply at least one modification
            modifications_applied = 0
            
            # Remove shapes if specified
            if remove_shapes and variation:
                num_to_remove = min(num_shapes_to_remove, len(variation))
                for _ in range(num_to_remove):
                    if variation:
                        remove_index = random.randint(0, len(variation) - 1)
                        variation.pop(remove_index)
                        modifications_applied += 1
            
            if move_shapes and variation:
                num_shapes_to_move = random.randint(1, min(2, len(variation)))
                for _ in range(num_shapes_to_move):
                    move_index = random.randint(0, len(variation) - 1)
                    variation[move_index].update({
                        'x': self.get_random_coord(150),
                        'y': self.get_random_coord(150)
                    })
                    modifications_applied += 1
            
            # Always apply rotation if no other modifications were made
            if modifications_applied == 0 or random.random() > 0.5:
                apply_random_rotation(variation)
                modifications_applied += 1
            
            return variation
        
        # Generate variations 2-4 with random combinations of modifications
        for i in range(3):
            variation = None
            if i == 0:
                # Variation 2: Missing one shape + possible rotation
                variation = create_variation(base_pattern, remove_shapes=False, num_shapes_to_remove=1)
            elif i == 1:
                # Variation 3: Missing two shapes + possible rotation
                variation = create_variation(base_pattern, remove_shapes=False, num_shapes_to_remove=2)
            else:
                # Variation 4: Moved shapes + possible rotation
                variation = create_variation(base_pattern, move_shapes=True)
            
            variations.append(variation)
        
        return variations

    def generate_complete_test_item(self, num_shapes, output_file: str = "test_item.svg", background_density=0.1) -> Dict[str, Any]:
        """
        Generate a complete test item and save it as a single SVG file.
        
        Args:
            output_file: Path to save the combined SVG
            
        Returns:
            Dictionary containing test information including correct answer
        """
        # Generate base pattern
        base_pattern = self.generate_compound_shape(num_shapes)
        
        # Generate variations
        variations = self.generate_variations(base_pattern)
        
        # Create combined SVG
        shapes_data = {
            'target': base_pattern,
            'options': variations
        }
        
        # Modify create_test_presentation to include backgrounds
        answer = self.create_test_presentation(shapes_data, output_file, background_density=background_density)
        
        return {
            'file': output_file,
            'correct_answer': answer+1 
        }

    def create_test_presentation(self, shapes_data: Dict[str, List[Dict[str, Any]]], output_file: str, background_density) -> None:
        """Create a single SVG combining target and options in test presentation format."""
        dwg = svgwrite.Drawing(output_file, size=("600px", "1000px"))
        
        # Add white background
        dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))
        
        # Add title
        dwg.add(dwg.text("Visual Figure Ground Test", 
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
        target_group.translate(200, 100)
        
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

        idx = list(range(len(shapes_data['options'])))
        random.shuffle(idx)
        correct_option = idx.index(0)
        shapes_data['options'] = [shapes_data['options'][i] for i in idx]
        # Create option groups with translations and backgrounds
        for i, option_shapes in enumerate(shapes_data['options']):
            option_group = dwg.g()
            row = i // 2
            col = i % 2
            option_group.translate(100 + col * 250, 400 + row * 250)
            
            # # Add background for variations
            background_elements = self.generate_background(dwg, density=background_density)
            for element in background_elements:
                element.translate(100 + col * 250, 400 + row * 250)
                dwg.add(element)
            
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
        return correct_option


import itertools

num_shapes_list = [2, 6, 10]
background_density_list = [0.1, 0.3, 0.5]

sweep_list = itertools.product(num_shapes_list, background_density_list)

base_dir = "visual_discrimination/sweep/visual_figure_ground"

if not os.path.exists(base_dir):
    os.makedirs(base_dir)
idx = 0
data = []
for sweep in sweep_list:
    num_shapes, background_density = sweep
    generator = VisualDiscriminationTestGenerator()
    for i in tqdm(range(10)):
        fname = f"{idx}.svg"
        response = generator.generate_complete_test_item(num_shapes, os.path.join(base_dir, fname), background_density)
        answer = response['correct_answer']
        data.append({
            'filename': fname,
            'answer': answer,
            'background_density': background_density,
            "sweep": sweep
        })
        idx += 1
# Save metadata to CSV
df = pd.DataFrame(data)
df.to_csv(os.path.join(base_dir, 'dataset_info.csv'), index=False)

