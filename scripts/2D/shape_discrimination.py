# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import svgwrite
import random
import math
from collections import defaultdict
import random
import csv
import os
from collections import defaultdict
import itertools
import pandas as pd
shape_types = ['circle', 'rectangle', 'triangle', 'hexagon', 
                'star', 'pentagon', 'octagon']

class Shape:
    def __init__(self, shape_type, base_path=None):
        self.type = shape_type
        self.base_path = base_path
        self.center = (0, 0)
        self.scale = 1.0
        self.rotation = 0
        self.stroke_width = 2
        self.stroke_color = 'black'
        self.fill = 'none'

    def get_path_data(self):
        if self.type == 'circle':
            return f"M0,0 m-30,0 a30,30 0 1,0 60,0 a30,30 0 1,0 -60,0"
        elif self.type == 'rectangle':
            return "M-30,-20 h60 v40 h-60 Z"
        elif self.type == 'triangle':
            return "M0,-30 L30,30 L-30,30 Z"
        elif self.type == 'hexagon':
            return "M30,0 L15,-26 L-15,-26 L-30,0 L-15,26 L15,26 Z"
        elif self.type == 'star':
            points = []
            points_count = 5
            outer_radius = 30
            inner_radius = 15
            for i in range(points_count * 2):
                angle = math.pi * i / points_count - math.pi / 2
                radius = outer_radius if i % 2 == 0 else inner_radius
                x = math.cos(angle) * radius
                y = math.sin(angle) * radius
                points.append((x, y))
            return self._points_to_path(points)
        elif self.type == 'pentagon':
            points = []
            for i in range(5):
                angle = 2 * math.pi * i / 5 - math.pi / 2
                x = math.cos(angle) * 30
                y = math.sin(angle) * 30
                points.append((x, y))
            return self._points_to_path(points)
        elif self.type == 'octagon':
            points = []
            for i in range(8):
                angle = 2 * math.pi * i / 8 - math.pi / 8
                x = math.cos(angle) * 30
                y = math.sin(angle) * 30
                points.append((x, y))
            return self._points_to_path(points)
        return self.base_path

    def _points_to_path(self, points):
        if not points:
            return ""
        path = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
        for x, y in points[1:]:
            path += f" L{x:.1f},{y:.1f}"
        path += " Z"
        return path

    def get_bounding_box(self):
        """Calculate bounding box after transformations."""
        base_size = 60  # Base size for all shapes
        if self.type == 'circle':
            radius = 30 * self.scale
            return (-radius, -radius, radius * 2, radius * 2)
        else:
            return (-base_size/2 * self.scale, -base_size/2 * self.scale,
                   base_size * self.scale, base_size * self.scale)

    def get_transformed_corners(self):
        """Get corners of bounding box after rotation."""
        bbox = self.get_bounding_box()
        corners = [
            (bbox[0], bbox[1]),  # Top-left
            (bbox[0] + bbox[2], bbox[1]),  # Top-right
            (bbox[0] + bbox[2], bbox[1] + bbox[3]),  # Bottom-right
            (bbox[0], bbox[1] + bbox[3])  # Bottom-left
        ]
        
        # Rotate corners
        rad = math.radians(self.rotation)
        cos_rot = math.cos(rad)
        sin_rot = math.sin(rad)
        rotated = []
        for x, y in corners:
            rx = x * cos_rot - y * sin_rot + self.center[0]
            ry = x * sin_rot + y * cos_rot + self.center[1]
            rotated.append((rx, ry))
        return rotated

def check_overlap(shape1, shape2, min_distance_inwards):
    # min_distance_inwards is the minimum distance between the two shapes that is allowed for them to not be considered overlapping, setting
    #  this to negative will allow the shapes to overlap in a controlled manner.

    """Check if two shapes overlap using Separating Axis Theorem (SAT)."""
    corners1 = shape1.get_transformed_corners()
    corners2 = shape2.get_transformed_corners()

    def get_axes(corners):
        axes = []
        for i in range(len(corners)):
            p1 = corners[i]
            p2 = corners[(i + 1) % len(corners)]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            normal = (-edge[1], edge[0])
            length = math.sqrt(normal[0]**2 + normal[1]**2)
            if length > 0:
                axes.append((normal[0]/length, normal[1]/length))
        return axes

    def project(corners, axis):
        dots = [axis[0] * x + axis[1] * y for x, y in corners]
        return min(dots), max(dots)

    axes = get_axes(corners1) + get_axes(corners2)

    for axis in axes:
        p1_min, p1_max = project(corners1, axis)
        p2_min, p2_max = project(corners2, axis)
        # out of all the axes, there exists atleast one axis where the projection between all the points of polygon 1 do not overalp with projections of polygon 2
        if p1_min > p2_max + min_distance_inwards  or p2_min  > p1_max + min_distance_inwards :
            return False
    # if the if condition is never triggered, it means that there is an overlap and the function returns True
    return True

def generate_complex_composition(canvas_width=800, canvas_height=600, 
                    num_shapes=None, max_instances=5,
                    max_concentric=3, concentric_probability=0.6,
                    min_scale=0.8, max_scale=2.0,
                    max_placement_attempts=50, min_distance_inwards=4):
    """Generate a pattern of shapes with overlap prevention."""
    
    dwg = svgwrite.Drawing(size=(canvas_width, canvas_height))
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), fill='white'))
    

    if num_shapes is None:
        num_shapes = random.randint(1, len(shape_types))
    
    selected_shapes = random.sample(shape_types, num_shapes)
    placed_shapes = []
    shape_counts = defaultdict(int)
    
    def add_shape_to_drawing(shape, group=None):
        """Add a shape to the SVG drawing."""
        path = dwg.path(d=shape.get_path_data())
        path.fill(shape.fill)
        path.stroke(shape.stroke_color)
        # path.stroke_width(shape.stroke_width)
        
        transform = f"translate({shape.center[0]},{shape.center[1]}) "
        transform += f"rotate({shape.rotation}) "
        transform += f"scale({shape.scale})"
        
        path['transform'] = transform
        
        if group:
            group.add(path)
        else:
            dwg.add(path)
    
    for shape_type in selected_shapes:
        num_instances = random.randint(1, max_instances)
        
        for _ in range(num_instances):
            base_shape = Shape(shape_type)
            placement_success = False
            attempts = 0
            
            while not placement_success and attempts < max_placement_attempts:
                # Generate random parameters
                scale = random.uniform(min_scale, max_scale)
                rotation = random.uniform(0, 360)
                
                # Adjust base_shape properties
                base_shape.scale = scale
                base_shape.rotation = rotation
                
                # Calculate safe boundaries for placement
                bbox = base_shape.get_bounding_box()
                max_dim = max(abs(bbox[2]), abs(bbox[3])) * 1.2  # Add 20% padding
                
                # Try random position
                x = random.uniform(max_dim, canvas_width - max_dim)
                y = random.uniform(max_dim, canvas_height - max_dim)
                base_shape.center = (x, y)
                
                # Check for overlaps
                overlaps = False
                for existing_shape in placed_shapes:
                    if check_overlap(base_shape, existing_shape, min_distance_inwards):
                        overlaps = True
                        break
                
                if not overlaps:
                    placement_success = True
                    placed_shapes.append(base_shape)
                    
                    # Handle concentric patterns
                    if random.random() < concentric_probability:
                        num_rings = random.randint(2, max_concentric)
                        group = dwg.g()
                        
                        for i in range(num_rings):
                            ring_shape = Shape(shape_type)
                            ring_shape.center = base_shape.center
                            ring_shape.rotation = base_shape.rotation
                            ring_shape.scale = base_shape.scale * (1 - i * 0.3)
                            add_shape_to_drawing(ring_shape, group)
                            shape_counts[shape_type] += 1
                        
                        dwg.add(group)
                    else:
                        add_shape_to_drawing(base_shape)
                        shape_counts[shape_type] += 1
                
                attempts += 1
    
    return dwg.tostring(), dict(shape_counts)



def generate_easy_example(index):
    """Generate an easy example with single shape type"""
    # Select one random shape
    
    # Random number of instances (1-4)
    num_instances = random.randint(1, 4)
    
    composition, shape_counts = generate_complex_composition(
        canvas_width=400,
        canvas_height=400,
        num_shapes=1,
        max_instances=num_instances,
        max_concentric=1,  # No concentric shapes for easy
        concentric_probability=0,
    )
    
    filename = f"easy_{index}.svg"
    return filename, composition, shape_counts

def generate_medium_example(index):
    """Generate a medium example with 2-3 shape types"""
    num_shapes = random.randint(2, len(shape_types))
    
    composition, shape_counts = generate_complex_composition(
        canvas_width=400,
        canvas_height=400,
        num_shapes=num_shapes,
        max_instances=3,
        max_concentric=1,  # No concentric shapes for medium
        concentric_probability=0,
    )
    filename = f"medium_{index}.svg"
    return filename, composition, shape_counts

def generate_hard_example(index):
    """Generate a hard example with 3+ shapes and concentric patterns"""
    # Select 3 or more shapes
    num_shapes = random.randint(5, len(shape_types))
    
    composition, shape_counts = generate_complex_composition(
        canvas_width=400,
        canvas_height=400,
        num_shapes=num_shapes,
        max_instances=4,
        max_concentric=3,  # Up to two rings for concentric shapes
        concentric_probability=0.4,
    )
    
    filename = f"hard_{index}.svg"
    return filename, composition, shape_counts

def generate_dataset(output_dir="geometric_dataset"):
    """Generate the complete dataset with all examples"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare CSV data
    csv_data = []
    
    # Generate easy examples (40%)
    for i in range(1, 41):
        filename, composition, shape_counts = generate_easy_example(i)
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(composition)
        csv_data.append({
            'filename': filename,
            'shape_dictionary': str(shape_counts)
        })
        print(f"Generated {filename}")
    
    # Generate medium examples (30%)
    for i in range(1, 31):
        filename, composition, shape_counts = generate_medium_example(i)
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(composition)
        csv_data.append({
            'filename': filename,
            'shape_dictionary': str(shape_counts)
        })
        print(f"Generated {filename}")
    
    # Generate hard examples (30%)
    for i in range(1, 31):
        filename, composition, shape_counts = generate_hard_example(i)
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(composition)
        csv_data.append({
            'filename': filename,
            'shape_dictionary': str(shape_counts)
        })
        print(f"Generated {filename}")
    
    # Write CSV file
    csv_path = os.path.join(output_dir, 'dataset_info.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'shape_dictionary'])
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"\nGenerated {len(csv_data)} examples")
    print(f"Dataset information saved to {csv_path}")

if __name__ == "__main__":

    min_distance_inwards_lst = [10, -20, -30, -40]
    num_shapes_lst = [3, 7]
    num_instances_lst = [3, 6, 10]
    
    sweep_lst = list(itertools.product(num_shapes_lst, num_instances_lst, min_distance_inwards_lst))
    csv_data = []
    if not os.path.exists("visual_discrimination/sweep/geometric_dataset"):
        os.makedirs("visual_discrimination/sweep/geometric_dataset")
    
    for i, sweep in enumerate(sweep_lst):
        for j in range(10):
            num_shapes, num_instances, min_distance_inwards = sweep
            composition, shape_counts = generate_complex_composition(
                canvas_width=400,
                canvas_height=400,
                num_shapes=num_shapes,
                max_instances=num_instances,
                max_concentric=3,  # Up to two rings for concentric shapes
                concentric_probability=0.4,
                min_distance_inwards = min_distance_inwards
            )
            filename = f"sweep_{i}_{j}.svg"
            with open(os.path.join("visual_discrimination/sweep/geometric_dataset", filename), 'w') as f:
                f.write(composition)
            print(f"Generated {filename}")
            csv_data.append({
                'filename': filename,
                'shape_dictionary': str(shape_counts),
                'sweep': sweep
            })
    
    csv_path = os.path.join("visual_discrimination/sweep/geometric_dataset", 'dataset_dump.csv')
    pd.DataFrame(csv_data).to_csv(csv_path, index=False)

