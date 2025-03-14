import random
import re
from collections import defaultdict
import math
import csv
import os
import pandas as pd

def scale_points_from_center(points, center, scale):
    """Scale points relative to center by given scale factor."""
    scaled_points = []
    cx, cy = center
    for x, y in points:
        dx = x - cx
        dy = y - cy
        new_x = cx + (dx * scale)
        new_y = cy + (dy * scale)
        scaled_points.append((new_x, new_y))
    return scaled_points

def points_to_path(points):
    """Convert points back to SVG path data."""
    if not points:
        return ""
    path = f"M{points[0][0]:.1f} {points[0][1]:.1f}"
    for x, y in points[1:]:
        path += f" L{x:.1f} {y:.1f}"
    path += " Z"
    return path

def parse_path_points(path_data):
    """
    Extract all points from SVG path data.
    Returns list of (x,y) tuples.
    """
    numbers = re.findall(r'[MLAZ]\s*(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', path_data)
    return [(float(x), float(y)) for x, y in numbers]

def calculate_center(points):
    """Calculate geometric center of points."""
    if not points:
        return (0, 0)
    x_sum = sum(x for x, y in points)
    y_sum = sum(y for x, y in points)
    return (x_sum / len(points), y_sum / len(points))

def parse_shape_dimensions(path_data):
    """
    Parse shape dimensions from path data more reliably.
    Returns (x, y, width, height) or None if parsing fails.
    """
    try:
        numbers = []
        for match in re.finditer(r'[MLHVAZ]\s*(-?\d+\.?\d*)\s*,?\s*(-?\d+\.?\d*)?', path_data):
            x = float(match.group(1))
            y = float(match.group(2)) if match.group(2) else None
            if y is not None:
                numbers.append((x, y))
        
        if not numbers:
            return None
            
        x_coords = [x for x, y in numbers]
        y_coords = [y for x, y in numbers]
        min_x = min(x_coords)
        min_y = min(y_coords)
        width = max(x_coords) - min_x
        height = max(y_coords) - min_y
        
        return min_x, min_y, width, height
    except (ValueError, IndexError):
        return None

def scale_shape(shape_type, original_path, scale):
    """
    Scale different shapes according to their type.
    Returns scaled path string.
    """
    if shape_type in ['circle', 'ellipse']:
        # Extract radius and center from circle path
        match = re.search(r'm(-?\d+\.?\d*)\s+0\s+a(\d+\.?\d*),(\d+\.?\d*)', original_path)
        if match:
            radius = float(match.group(2))
            new_radius = radius * scale
            return f"M0 0 m-{new_radius} 0 a{new_radius},{new_radius} 0 1,0 {2*new_radius},0 a{new_radius},{new_radius} 0 1,0 -{2*new_radius},0"
        return original_path
    
    # For all other shapes, scale the coordinates
    try:
        commands = []
        current_pos = (0, 0)
        command_pattern = re.compile(r'([MmLlHhVvZz])([^MmLlHhVvZz]*)')        
        for match in command_pattern.finditer(original_path):
            command = match.group(1)
            coords = match.group(2).strip()
            command = command.upper()
            
            if command in 'ML':
                # Handle absolute move and line commands
                numbers = [float(n) for n in coords.split()]
                scaled_numbers = []
                for i in range(0, len(numbers), 2):
                    x = numbers[i] * scale
                    y = numbers[i + 1] * scale
                    scaled_numbers.extend([x, y])
                commands.append(command + ' ' + ' '.join(f"{n:.1f}" for n in scaled_numbers))
                if scaled_numbers:
                    current_pos = (scaled_numbers[-2], scaled_numbers[-1])
            
            elif command == 'H':
                # Handle horizontal line
                x = float(coords) * scale
                commands.append(f"H{x:.1f}")
                current_pos = (x, current_pos[1])
            
            elif command == 'V':
                # Handle vertical line
                y = float(coords) * scale
                commands.append(f"V{y:.1f}")
                current_pos = (current_pos[0], y)
            
            elif command in 'Z':
                commands.append(command)
        
        return ' '.join(commands)
    except (ValueError, IndexError):
        # If parsing fails, return original path
        return original_path

shape_dictionary = {
    "star": '''<path d="M50 10 L61 40 L94 40 L68 60 L79 90 L50 70 L21 90 L32 60 L6 40 L39 40 Z" 
          fill="none" stroke="black" stroke-width="1"/>''',
    "triangle": '''<path d="M50 20 L80 80 L20 80 Z" fill="none" stroke="black" stroke-width="2"/>''',
    "pentagon": '''<path d="M50 20 L80 40 L70 80 L30 80 L20 40 Z" fill="none" stroke="black" stroke-width="2"/>''',
    # "circle": '''<path d="M50 50 m-30 0 a30,30 0 1,0 60,0 a30,30 0 1,0 -60,0" fill="none" stroke="black" stroke-width="2"/>''',
    # "rectangle": '''<path d="M20 20 h60 v40 h-60 Z" fill="none" stroke="black" stroke-width="2"/>''',
    "hexagon": '''<path d="M50 20 L80 35 L80 65 L50 80 L20 65 L20 35 Z" fill="none" stroke="black" stroke-width="2"/>''',
    "octagon": '''<path d="M35 20 L65 20 L80 35 L80 65 L65 80 L35 80 L20 65 L20 35 Z" fill="none" stroke="black" stroke-width="2"/>''',
    "cross": '''<path d="M35 20 L65 20 L65 35 L80 35 L80 65 L65 65 L65 80 L35 80 L35 65 L20 65 L20 35 L35 35 Z" fill="none" stroke="black" stroke-width="2"/>'''
}

color_dictionary = {
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
    "orange": "#FFA500",
    "purple": "#800080",
    "black": "#000000",
    "gray": "#808080",
    "yellow": "#FFFF00"
}

def calculate_shape_bounds(shape_type, points, scale, rotation_deg):
    """
    Calculate the bounding box of a shape after scaling and rotation.
    Assumes 'points' are centered at the origin.
    Returns (width, height) of the bounding box.
    """
    rotation = math.radians(rotation_deg)
    
    if shape_type in ['circle', 'ellipse']:
        # For circles, use the known base radius of 30 from the path definition.
        # Since we centered the circle, it now starts from (0,0).
        radius = scale * 30
        return (radius * 2, radius * 2)
    
    if not points:
        return (0, 0)
    
    # Compute bounding box from centered points
    x_coords = [x for x, y in points]
    y_coords = [y for x, y in points]
    original_width = (max(x_coords) - min(x_coords))
    original_height = (max(y_coords) - min(y_coords))
    
    # Scale
    width = original_width * scale
    height = original_height * scale
    
    # Rotate the bounding box
    rotated_width = abs(width * math.cos(rotation)) + abs(height * math.sin(rotation))
    rotated_height = abs(width * math.sin(rotation)) + abs(height * math.cos(rotation))
    return (rotated_width, rotated_height)


def check_overlap(new_box, placed_boxes):
    """
    Check if new bounding box overlaps with any placed boxes.
    Each box is tuple: (x1, y1, x2, y2) representing top-left and bottom-right corners
    """
    if not placed_boxes:
        return False
        
    for box in placed_boxes:
        # Check if one rectangle is to the left of the other
        if new_box[2] < box[0] or box[2] < new_box[0]:
            continue
        # Check if one rectangle is above the other
        if new_box[3] < box[1] or box[3] < new_box[1]:
            continue
        # If we get here, the rectangles overlap
        return True
    return False

def get_bounding_box(x, y, width, height, rotation):
    """
    Get rotated bounding box corners given center position and dimensions.
    Returns (x1, y1, x2, y2) for the encompassing axis-aligned bounding box.
    """
    # Convert rotation to radians
    rotation_rad = math.radians(rotation)
    
    # Calculate the rotated width and height
    rot_width = abs(width * math.cos(rotation_rad)) + abs(height * math.sin(rotation_rad))
    rot_height = abs(width * math.sin(rotation_rad)) + abs(height * math.cos(rotation_rad))
    
    # Calculate the corners of the encompassing axis-aligned bounding box
    x1 = x - rot_width/2
    y1 = y - rot_height/2
    x2 = x + rot_width/2
    y2 = y + rot_height/2
    
    return (x1, y1, x2, y2)

def try_place_shape(width, height, canvas_width, canvas_height, padding, placed_boxes, max_attempts=50):
    """
    Try to find a valid position for a shape with given dimensions.
    Returns (x, y, box) if successful, None if failed.
    """
    for _ in range(max_attempts):
        # Calculate safe positioning ranges
        x_min = padding + width/2
        x_max = canvas_width - padding - width/2
        y_min = padding + height/2
        y_max = canvas_height - padding - height/2
        
        if x_max <= x_min or y_max <= y_min:
            return None
            
        # Try random position
        x = random.uniform(x_min, x_max)
        y = random.uniform(y_min, y_max)
        rotation = random.uniform(0, 360)
        
        # Get bounding box for this position
        box = get_bounding_box(x, y, width, height, rotation)
        
        # Check for overlaps
        if not check_overlap(box, placed_boxes):
            return x, y, rotation, box
            
    return None


def generate_complex_composition(shape_dict=shape_dictionary, canvas_width=800, canvas_height=600, 
                               num_shapes=None, max_instances=10):  # Increased max_instances
    """Generate composition with shape-specific scaling and non-overlapping placement."""
    if num_shapes is None:
        num_shapes = random.randint(1, len(shape_dict))
    
    selected_shapes = random.sample(list(shape_dict.keys()), num_shapes)
    shape_counts = defaultdict(int)
    color_counts = defaultdict(int)
    placed_boxes = []  # Keep track of placed shapes
    
    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_width} {canvas_height}">
    <rect width="{canvas_width}" height="{canvas_height}" fill="white"/>
"""
    
    # Calculate initial scale based on canvas size and desired number of shapes
    total_shapes = sum(random.randint(1, max_instances) for _ in range(num_shapes))
    avg_shape_area = (canvas_width * canvas_height) / (total_shapes * 4)  # Use 1/4 of equal division
    base_scale_factor = math.sqrt(avg_shape_area / (100 * 100))  # Assuming 100x100 is typical shape size
    
    for shape_name in selected_shapes:
        num_instances = random.randint(1, max_instances)
        shape_content = shape_dict[shape_name]
        
        path_match = re.search(r'd="([^"]+)"', shape_content)
        if not path_match:
            continue
        
        original_path_data = path_match.group(1)
        original_points = parse_path_points(original_path_data)
        
        if not original_points:
            continue
        
        # Center the shape
        cx, cy = calculate_center(original_points)
        centered_points = [(px - cx, py - cy) for px, py in original_points]
        path_data = points_to_path(centered_points)
        
        svg += f"\n    <!-- {shape_name} instances -->\n"
        
        for _ in range(num_instances):
            # Calculate initial scale
            scale = random.uniform(base_scale_factor * 0.5, base_scale_factor * 1.5)
            
            # Calculate bounding box dimensions
            bounds_width, bounds_height = calculate_shape_bounds(shape_name, centered_points, scale, 0)
            padding = max(10, bounds_width * 0.05, bounds_height * 0.05)  # Reduced padding
            
            # Try to place the shape
            placement = try_place_shape(bounds_width, bounds_height, 
                                     canvas_width, canvas_height,
                                     padding, placed_boxes)
            
            if placement is None:
                # Try with reduced scale if initial placement fails
                scale *= 0.8
                bounds_width *= 0.8
                bounds_height *= 0.8
                placement = try_place_shape(bounds_width, bounds_height,
                                         canvas_width, canvas_height,
                                         padding, placed_boxes)
                
                if placement is None:
                    continue  # Skip this shape if still can't place
            
            x, y, rotation, box = placement
            placed_boxes.append(box)
            
            # Select color and update counts
            color_name = random.choice(list(color_dictionary.keys()))
            color_value = color_dictionary[color_name]
            
            shape_counts[shape_name] += 1
            color_counts[(shape_name, color_name)] += 1
            
            scaled_path = scale_shape(shape_name, path_data, scale)
            svg += f"""    <g transform="translate({x:.1f} {y:.1f}) rotate({rotation:.1f})">
        <path d="{scaled_path}" fill="{color_value}" stroke="black" stroke-width="2"/>
    </g>
"""
    
    svg += "</svg>"
    return svg, dict(shape_counts), dict(color_counts)


def generate_easy_example(index, shape_dict):
    """Generate an easy example with single shape type and random colors"""
    # Select one random shape
    shape_name = random.choice(list(shape_dict.keys()))
    selected_dict = {shape_name: shape_dict[shape_name]}
    
    # Random number of instances (1-4)
    num_instances = random.randint(1, 5)
    
    composition, shape_counts, color_counts = generate_complex_composition(
        shape_dict=selected_dict,
        canvas_width=400,
        canvas_height=400,
        num_shapes=1,
        max_instances=num_instances
    )
    
    filename = f"easy_{index}.svg"
    return filename, composition, shape_counts, color_counts

def generate_medium_example(index, shape_dict):
    """Generate a medium example with 1-3 shape types and random colors"""
    # Select 1-3 random shapes
    num_shapes = 2
    selected_shapes = random.sample(list(shape_dict.keys()), num_shapes)
    selected_dict = {name: shape_dict[name] for name in selected_shapes}
    
    composition, shape_counts, color_counts = generate_complex_composition(
        shape_dict=selected_dict,
        canvas_width=400,
        canvas_height=400,
        num_shapes=num_shapes,
        max_instances=8
    )
    
    filename = f"medium_{index}.svg"
    return filename, composition, shape_counts, color_counts

def generate_hard_example(index, shape_dict):
    """Generate a hard example with 3+ shapes and random colors."""
    # Select 3 or more shapes
    num_shapes = random.randint(3, len(shape_dict))
    selected_shapes = random.sample(list(shape_dict.keys()), num_shapes)
    selected_dict = {name: shape_dict[name] for name in selected_shapes}
    
    composition, shape_counts, color_counts = generate_complex_composition(
        shape_dict=selected_dict,
        canvas_width=400,
        canvas_height=400,
        num_shapes=num_shapes,
        max_instances=4
    )
    
    filename = f"hard_{index}.svg"
    return filename, composition, shape_counts, color_counts

def generate_dataset(output_dir="visual_discrimination/color_and_shape_disambiguation"):
    """Generate the complete dataset with all examples, including color counts."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare CSV data
    csv_data = []
    
    # Generate easy examples (40%)
    for i in range(1, 41):
        filename, composition, shape_counts, color_counts = generate_easy_example(i, shape_dictionary)
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(composition)
        csv_data.append({
            'filename': filename,
            'shape_dictionary': str(shape_counts),
            'color_dictionary': str(color_counts)
        })
        print(f"Generated {filename}")
    
    # Generate medium examples (30%)
    for i in range(1, 31):
        filename, composition, shape_counts, color_counts = generate_medium_example(i, shape_dictionary)
        with open(os.path.join(output_dir, filename), 'w') as f:
            f.write(composition)
        csv_data.append({
            'filename': filename,
            'shape_dictionary': str(shape_counts),
            'color_dictionary': str(color_counts)
        })
        print(f"Generated {filename}")
    
    # Write CSV file
    csv_path = os.path.join(output_dir, 'dataset_info.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['filename', 'shape_dictionary', 'color_dictionary'])
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"\nGenerated {len(csv_data)} examples")
    print(f"Dataset information saved to {csv_path}")

def generate_base_shape_files(output_dir="geometric_dataset"):
    """Generate individual SVG files for each base shape."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Canvas dimensions for base shapes
    canvas_size = 100  # Using 100x100 viewBox for consistency
    
    for shape_name, shape_content in shape_dictionary.items():
        # Extract path data
        path_match = re.search(r'd="([^"]+)"', shape_content)
        if not path_match:
            continue
            
        path_data = path_match.group(1)
        
        # Create SVG with single shape
        svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_size} {canvas_size}">
    <rect width="{canvas_size}" height="{canvas_size}" fill="white"/>
    <path d="{path_data}" fill="none" stroke="black" stroke-width="2"/>
</svg>"""
        
        # Save to file
        filename = f"{shape_name}.svg"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write(svg)
        print(f"Generated base shape: {filename}")


num_shapes_list = [2, 4, 6]
num_instances = [2, 4, 6]

import itertools
dir_name = "visual_discrimination/sweep/color_and_shape_disambiguation"
if not os.path.exists(dir_name):
    os.makedirs(dir_name)

sweep_list = itertools.product(num_shapes_list, num_instances)
csv_data = []
idx = 0
for sweep in sweep_list:
    for _ in range(10):
        num_shapes, num_instances = sweep
        composition, shape_counts, color_counts = generate_complex_composition(
            shape_dict=shape_dictionary,
            canvas_width=400,
            canvas_height=400,
            num_shapes=num_shapes,
            max_instances=num_instances
        )

        filename = f"{idx}.svg"
        with open(os.path.join(dir_name, filename), 'w') as f:
            f.write(composition)
        idx+=1

        csv_data.append({
                'filename': filename,
                'shape_dictionary': str(shape_counts),
                'color_dictionary': str(color_counts),
                'sweep': sweep
            })

pd.DataFrame(csv_data).to_csv(os.path.join(dir_name, "dataset_dump.csv"), index=False)
