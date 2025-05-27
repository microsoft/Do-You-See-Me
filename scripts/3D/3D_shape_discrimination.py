import bpy
from mathutils import Vector, Euler
from bpy_extras.object_utils import world_to_camera_view
import bmesh

import os
import random
import math
import json
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)

# Configuration
data_dir = "data"
output_dir = "form_constancy"

# Scene and lighting configuration
scenes = ["city square", "bridge", "indoor", "outdoor", "playground", "hall", "grassland", 
          "garage", "street", "beach", "station", "tunnel", "moonlit grass", "dusk city", 
          "skywalk", "garden"]
lights = ["left", "middle", "right"]

# Shape types for discrimination
shape_types_3d = ['cube', 'sphere', 'cylinder', 'cone', 'torus']

# Bounds of valid locations where the foreground object can be placed
bounds = {
    "indoor": {"xmin": -4.5, "xmax": 4.5, "ymin": -15, "ymax": 0},
    "outdoor": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "playground": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "bridge": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "city square": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "hall": {"xmin": -4.5, "xmax": 4.5, "ymin": -15, "ymax": 0},
    "grassland": {"xmin": -4.5, "xmax": 4.5, "ymin": -15, "ymax": -2},
    "garage": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "street": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "beach": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "station": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "tunnel": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "moonlit grass": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "dusk city": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "skywalk": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
    "garden": {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0},
}

# Default bounds as fallback
default_bounds = {"xmin": -4.5, "xmax": 4.5, "ymin": -20, "ymax": 0}

# Light positions
light_position = {
    "left": [5, -5, 7],
    "middle": [0, 0, 7],
    "right": [-5, 5, 7]
}

# Colors for materials
material_colors = ["red", "blue", "yellow", "black", "white"]


def get_ground_level(scene_name, x, y):
    """
    Get the ground level at a specific position
    Returns the z-coordinate where the object should be placed
    """
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    
    # Cast a ray downward from a high position
    start_pos = Vector((x, y, 10))
    direction = Vector((0, 0, -1))
    
    ray_result = scene.ray_cast(depsgraph, start_pos, direction, distance=50)
    
    if ray_result[0]:  # Hit something
        hit_location = ray_result[1]
        return hit_location.z
    else:
        # Default ground level if no hit
        return 0.0
    

def check_overlap(new_pos, existing_positions, min_distance=2.0):
    """Check if new position overlaps with existing positions"""
    for pos in existing_positions:
        if (Vector(new_pos) - Vector(pos)).length < min_distance:
            return True
    return False


def create_material(color_name):
    """Create a material with given color"""
    material = bpy.data.materials.new(name=f"Material_{color_name}")
    material.use_nodes = True
    
    nodes = material.node_tree.nodes
    nodes.clear()
    
    node_pbr = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_output = nodes.new(type='ShaderNodeOutputMaterial')
    
    links = material.node_tree.links
    links.new(node_pbr.outputs["BSDF"], node_output.inputs["Surface"])
    
    color_map = {
        'red': (0.8, 0.1, 0.1, 1),
        'blue': (0.1, 0.1, 0.8, 1),
        'yellow': (0.8, 0.8, 0.1, 1),
        'purple': (0.8, 0.1, 0.8, 1),
        'orange': (0.8, 0.4, 0.1, 1), 
        'black': (0, 0, 0, 1),
        'white': (1, 1, 1, 1),
    }
    
    node_pbr.inputs["Base Color"].default_value = color_map.get(color_name, (0.5, 0.5, 0.5, 1))
    return material


# def check_occlusion_level(obj, camera, existing_objects, min_visibility=0.3):
#     """
#     Check if an object is sufficiently visible from the camera
#     Returns True if object is visible enough, False otherwise
#     """
#     scene = bpy.context.scene
    
#     # Create a temporary mesh to get vertex positions
#     depsgraph = bpy.context.evaluated_depsgraph_get()
#     obj_eval = obj.evaluated_get(depsgraph)
#     mesh = obj_eval.to_mesh()
    
#     # Get all vertices in world space
#     vertices_world = [obj.matrix_world @ v.co for v in mesh.vertices]
#     obj_eval.to_mesh_clear()
    
#     # Check how many vertices are visible from camera
#     visible_count = 0
#     total_count = len(vertices_world)
    
#     if total_count == 0:
#         return False, 0  # No vertices, not visible
    
#     for vertex in vertices_world:
#         # Convert world position to camera view
#         camera_coord = world_to_camera_view(scene, camera, vertex)
        
#         # Check if point is within camera view
#         if 0 <= camera_coord.x <= 1 and 0 <= camera_coord.y <= 1 and camera_coord.z > 0:
#             # Ray cast to check for occlusion by existing objects
#             direction = (vertex - camera.location).normalized()
#             hit_distance = (vertex - camera.location).length
            
#             ray_result = scene.ray_cast(
#                 depsgraph,
#                 camera.location,
#                 direction,
#                 distance=hit_distance * 0.99  # Slightly less to avoid self-intersection
#             )
            
#             if not ray_result[0] or ray_result[4] == obj:  # No hit or hit own object
#                 visible_count += 1
#             # If another object is hit, the vertex is occluded
    
#     visibility_ratio = visible_count / total_count
#     return visibility_ratio >= min_visibility, visibility_ratio



def check_occlusion_level(obj, camera, existing_objects, min_visibility=0.3):
    scene = bpy.context.scene
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    vertices_world = [obj.matrix_world @ v.co for v in mesh.vertices]
    obj_eval.to_mesh_clear()
 
    # only these are real occluders
    occluders = {o for o in existing_objects}
 
    visible_count = 0
    total_count = len(vertices_world)
    if total_count == 0:
        return False, 0
 
    for vertex in vertices_world:
        camera_coord = world_to_camera_view(scene, camera, vertex)
        if 0 <= camera_coord.x <= 1 and 0 <= camera_coord.y <= 1 and camera_coord.z > 0:
            direction     = (vertex - camera.location).normalized()
            hit_distance  = (vertex - camera.location).length

        # only consider hits on previously placed objects as occlusion
        ray_result = scene.ray_cast(
            depsgraph,
            camera.location,
            direction,
            distance=hit_distance * 0.99
        )
        if not ray_result[0]:
            visible_count += 1
        else:
            hit_obj = ray_result[4]
            # ignore hits on non-occluders or on itself
            if hit_obj == obj or hit_obj not in occluders:
                visible_count += 1

    visibility_ratio = visible_count / total_count
    return visibility_ratio >= min_visibility, visibility_ratio


def get_shape_z_offset(shape_type, rotation_euler, scale_factor=1.0):
    """
    Calculate a more accurate z-offset based on shape geometry, rotation, and scale.
    
    Args:
        shape_type (str): Type of shape ('cube', 'sphere', etc.)
        rotation_euler (tuple): (x, y, z) rotation in radians
        scale_factor (float): Scale factor applied to the object
    
    Returns:
        float: Z-offset to place shape properly on ground
    """
    # Extract rotation components
    rot_x, rot_y, rot_z = rotation_euler
    
    if shape_type == 'sphere':
        # Sphere is always the radius from ground regardless of rotation
        return 0.75 * scale_factor
    
    elif shape_type == 'cube':
        # For a cube, calculate the distance from center to lowest vertex after rotation
        # The half-side length of the cube
        half_side = 0.75 * scale_factor
        
        # Calculate the 8 vertices of the cube in local coordinates
        vertices = [
            Vector((x * half_side, y * half_side, z * half_side)) 
            for x in [-1, 1] for y in [-1, 1] for z in [-1, 1]
        ]
        
        # Create rotation matrix from Euler angles
        rot_matrix = Euler(rotation_euler).to_matrix()
        
        # Transform vertices by rotation
        rotated_vertices = [rot_matrix @ v for v in vertices]
        
        # Find lowest z-value
        lowest_z = min(v.z for v in rotated_vertices)
        
        # Return offset to compensate for the lowest point
        return -lowest_z
    
    elif shape_type == 'cylinder':
        # For a cylinder, calculate based on rotation
        height = 1.5 * scale_factor
        radius = 0.75 * scale_factor
        half_height = height / 2
        
        # If x or y rotation is significant, the lowest point might be the rim
        if abs(rot_x) > 0.1 or abs(rot_y) > 0.1:
            # Create a simple approximation with key points
            end_cap_points = [Vector((0, 0, half_height)), Vector((0, 0, -half_height))]
            
            # Add points around the rims
            rim_points = []
            for angle in range(0, 360, 30):  # Sample points around the rim
                rad = math.radians(angle)
                # Top rim
                rim_points.append(Vector((radius * math.cos(rad), radius * math.sin(rad), half_height)))
                # Bottom rim
                rim_points.append(Vector((radius * math.cos(rad), radius * math.sin(rad), -half_height)))
            
            # Combine all points
            points = end_cap_points + rim_points
            
            # Create rotation matrix
            rot_matrix = Euler(rotation_euler).to_matrix()
            
            # Transform points
            rotated_points = [rot_matrix @ p for p in points]
            
            # Find lowest z-value
            lowest_z = min(p.z for p in rotated_points)
            return -lowest_z
        else:
            # If no significant x/y rotation, just use half-height
            return half_height
    
    elif shape_type == 'cone':
        # For a cone, calculate based on rotation
        height = 1.5 * scale_factor
        radius = 0.75 * scale_factor
        half_height = height / 2
        
        # Create key points for the cone
        points = [Vector((0, 0, half_height)), Vector((0, 0, -half_height))]  # Apex and center of base
        
        # Add points around the base rim
        for angle in range(0, 360, 30):  # Sample points around the rim
            rad = math.radians(angle)
            points.append(Vector((radius * math.cos(rad), radius * math.sin(rad), -half_height)))
        
        # Create rotation matrix
        rot_matrix = Euler(rotation_euler).to_matrix()
        
        # Transform points
        rotated_points = [rot_matrix @ p for p in points]
        
        # Find lowest z-value
        lowest_z = min(p.z for p in rotated_points)
        return -lowest_z
    
    elif shape_type == 'torus':
        # For a torus, calculate based on rotation
        major_radius = 0.75 * scale_factor
        minor_radius = 0.25 * scale_factor
        
        # Sample points around the torus
        points = []
        for major_angle in range(0, 360, 30):
            major_rad = math.radians(major_angle)
            center_x = major_radius * math.cos(major_rad)
            center_y = major_radius * math.sin(major_rad)
            
            for minor_angle in range(0, 360, 30):
                minor_rad = math.radians(minor_angle)
                x = center_x + (minor_radius * math.cos(minor_rad) * math.cos(major_rad))
                y = center_y + (minor_radius * math.cos(minor_rad) * math.sin(major_rad))
                z = minor_radius * math.sin(minor_rad)
                points.append(Vector((x, y, z)))
        
        # Create rotation matrix
        rot_matrix = Euler(rotation_euler).to_matrix()
        
        # Transform points
        rotated_points = [rot_matrix @ p for p in points]
        
        # Find lowest z-value
        lowest_z = min(p.z for p in rotated_points)
        return -lowest_z
    
    # Default for unknown shapes
    return 0.5 * scale_factor


def create_shape(shape_type, scale_factor=1.0):
    """Create a shape with the given type and scale factor"""
    if shape_type == 'cube':
        bpy.ops.mesh.primitive_cube_add(size=1.5 * scale_factor, location=(0, 0, 0))
    elif shape_type == 'sphere':
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75 * scale_factor, location=(0, 0, 0))
    elif shape_type == 'cylinder':
        bpy.ops.mesh.primitive_cylinder_add(radius=0.75 * scale_factor, depth=1.5 * scale_factor, location=(0, 0, 0))
    elif shape_type == 'cone':
        bpy.ops.mesh.primitive_cone_add(radius1=0.75 * scale_factor, depth=1.5 * scale_factor, location=(0, 0, 0))
    elif shape_type == 'torus':
        bpy.ops.mesh.primitive_torus_add(major_radius=0.75 * scale_factor, minor_radius=0.25 * scale_factor, location=(0, 0, 0))
    else:
        logging.warning(f"Unknown shape type: {shape_type}")
        return None
    
    return bpy.context.active_object


def apply_material_to_object(obj, color):
    """Apply a material with the given color to the object"""
    material = create_material(color)
    
    # Clear existing materials
    if obj.data.materials:
        obj.data.materials.clear()
    
    # Add new material
    obj.data.materials.append(material)
    return color


def get_rotation_for_shape(shape_type):
    """Get appropriate rotation for a shape type"""
    if shape_type in ['cylinder', 'cone']:
        # Limit cylinder and cone rotation to avoid them being completely on their side
        x_rot = random.uniform(-math.pi/4, math.pi/4)
        y_rot = random.uniform(-math.pi/4, math.pi/4)
        z_rot = random.uniform(0, 2*math.pi)
        # return (x_rot, y_rot, z_rot)
        return (0, 0,  random.uniform(0, 0.5*math.pi))
    else:
        # return (random.uniform(-math.pi/3, math.pi/3), 
        #         random.uniform(-math.pi/3, math.pi/3), 
        #         random.uniform(0, 2*math.pi))
        return (0, 0,  random.uniform(0, 0.5*math.pi))



def remap_dict_for_json(d):
    """Convert dictionary keys to strings for JSON compatibility"""
    if isinstance(d, dict):
        return {str(k): v for k, v in d.items()}
    else:
        raise TypeError("Input must be a dictionary")


def generate_single_discrimination_image(scene_name, light_type, 
                                        num_shapes, max_instances_per_shape,
                                         output_path=None, min_visibility=0.3):
    """Generate a single 3D shape discrimination image with controlled occlusion"""
    
    # Load scene
    scene_file = os.path.join(data_dir, "scenes", scene_name + ".blend")
    if not os.path.exists(scene_file):
        # If scene file doesn't exist, create a simple scene
        bpy.ops.wm.read_homefile(use_empty=True)
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
        ground = bpy.context.active_object
        ground.name = "Ground"
    else:
        bpy.ops.wm.open_mainfile(filepath=scene_file)
    
    # Clear selection
    bpy.ops.object.select_all(action='DESELECT')
    
    # Add lighting
    if os.path.exists(os.path.join(data_dir, "lights", "lights.blend")):
        with bpy.data.libraries.load(os.path.join(data_dir, "lights", "lights.blend")) as (data_from, data_to):
            data_to.objects = ["Point"]
        
        for obj in data_to.objects:
            if obj is not None:
                bpy.context.collection.objects.link(obj)
    else:
        # Create a simple light if not available
        bpy.ops.object.light_add(type='POINT', location=light_position[light_type])
        light = bpy.context.active_object
        light.data.energy = 1000
    
    # Set light position
    if "Point" in bpy.data.objects:
        bpy.data.objects["Point"].location = Vector(light_position[light_type])
    
    # Configure render settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.resolution_x = 800
    bpy.context.scene.render.resolution_y = 600
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.cycles.device = 'CPU'
    # switch to GPU
    bpy.context.scene.cycles.device = 'GPU'

    # enable all GPU devices (CUDA / OPTIX / OPENCL as appropriate)
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'    # or 'OPTIX' / 'OPENCL'
    for dev in prefs.devices:
        dev.use = True

    # Position camera first
    if 'Camera' not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(10, -10, 8))
        camera = bpy.context.active_object
        camera.rotation_euler = (math.radians(60), 0, math.radians(45))
        bpy.context.scene.camera = camera
    else:
        camera = bpy.data.objects['Camera']
        # Add camera jitter
        camera.rotation_euler[0] += math.radians(random.uniform(-0.5, 0.5))
        camera.rotation_euler[1] += math.radians(random.uniform(-0.5, 0.5))
    
    # Get scene bounds, with fallback to default if not found
    scene_bounds = bounds.get(scene_name, default_bounds)
    
    # Select random shapes
    selected_shape_types = random.sample(shape_types_3d, min(num_shapes, len(shape_types_3d)))
    
    # Initialize tracking variables
    shape_counts = defaultdict(int)  # Counts by shape type
    shape_color_counts = defaultdict(int)  # Counts by (shape, color) combination
    placed_positions = []  # Positions of successfully placed objects
    placed_objects = []  # References to successfully placed objects
    total_placed = 0  # Total number of objects placed
    
    # Place objects
    for shape_type in selected_shape_types:
        # Determine number of instances for this shape type
        num_instances = random.randint(1, max_instances_per_shape)
        
        for i in range(num_instances):
            attempts = 0
            max_attempts = 50
            successfully_placed = False
            
            while attempts < max_attempts and not successfully_placed:
                # Generate random position within bounds
                x = random.uniform(scene_bounds["xmin"], scene_bounds["xmax"])
                y = random.uniform(scene_bounds["ymin"], scene_bounds["ymax"])
                
                # Get ground level at this position
                ground_z = get_ground_level(scene_name, x, y)
                scale_factor = random.uniform(0.6, 1.2)

                # Create object with scale
                obj = create_shape(shape_type, scale_factor)
                if obj is None:
                    attempts += 1
                    continue
                
                obj.name = f"{shape_type}_{total_placed + i}"
                
                # Apply random rotation appropriate for the shape
                rotation = get_rotation_for_shape(shape_type)
                obj.rotation_euler = rotation
                
                # Get proper z-offset based on shape type, rotation, and scale
                z_offset = get_shape_z_offset(shape_type, rotation, scale_factor)
                
                # Set final position with proper z-coordinate
                final_z = ground_z + z_offset
                final_position = (x, y, final_z)
                obj.location = final_position
                
                # Check for overlap using updated position
                if not check_overlap(final_position, placed_positions):
                    # Random color (only apply after position check)
                    color = random.choice(material_colors)
                    
                    # Check visibility from camera
                    is_visible, visibility_ratio = check_occlusion_level(obj, camera, placed_objects, min_visibility)
                    
                    if is_visible or not placed_objects:  # First object or visible enough
                        # Now apply material after confirmed placement
                        apply_material_to_object(obj, color)
                        
                        # Record successful placement
                        placed_positions.append(final_position)
                        placed_objects.append(obj)
                        shape_counts[shape_type] += 1
                        shape_color_counts[(shape_type, color)] += 1
                        successfully_placed = True
                        logging.info(f"Placed {obj.name} with visibility ratio: {visibility_ratio:.2f}")
                    else:
                        # Remove object if not visible enough
                        bpy.data.objects.remove(obj, do_unlink=True)
                        logging.info(f"Removed {shape_type} due to insufficient visibility: {visibility_ratio:.2f}")
                else:
                    # Remove object if it overlaps
                    bpy.data.objects.remove(obj, do_unlink=True)
                
                attempts += 1
            
            if successfully_placed:
                total_placed += 1
            else:
                logging.warning(f"Failed to place {shape_type} after {max_attempts} attempts")
    
    # Ensure we have at least one object
    if total_placed == 0:
        logging.warning("No objects were placed! Placing a default object.")
        
        # Place a default object in front of camera
        scale_factor = random.uniform(0.8, 1.5)
        default_shape = random.choice(shape_types_3d)
        obj = create_shape(default_shape, scale_factor)
        
        # Position in camera view
        obj.location = (0, -5, 1)
        color = random.choice(material_colors)
        apply_material_to_object(obj, color)
        
        # Update counts
        shape_counts[default_shape] += 1
        shape_color_counts[(default_shape, color)] += 1
        total_placed = 1
    
    # Render
    if output_path is None:
        output_path = os.path.join(output_dir, f"shape_discrimination_{scene_name}_{light_type}_{difficulty}.png")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    
    # Save JSON with ground truth
    ground_truth = {
        "scene": scene_name,
        "light": light_type,
        "shape_counts": dict(shape_counts),
        "shape_color_counts": remap_dict_for_json(dict(shape_color_counts)),
        "min_visibility": min_visibility,
        "num_objects": total_placed,
        "num_shapes": num_shapes,
        "max_instances_per_shape": max_instances_per_shape,
    }
    
    json_path = output_path.replace('.png', '.json')
    with open(json_path, 'w') as f:
        json.dump(ground_truth, f, indent=4)
    
    logging.info(f"Generated image: {output_path}")
    logging.info(f"Ground truth: {json_path}")
    
    return output_path, ground_truth


from itertools import product

# Example usage
if __name__ == "__main__":
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a single image with random parameters
    scene = random.choice(scenes)
    light = random.choice(lights)
    difficulty = random.choice(["easy", "medium", "hard"])
    difficulty = "hard"  # For testing purposes, set to hard
    # Set minimum visibility threshold (0.3 means at least 30% of the object must be visible)
    min_visibility = 0.99
    
    num_instances_per_shape_list = [1, 2, 3]
    num_shapes_list = [1, 2, 3, 4, 5]
    min_visibility = [0.7, 0.8, 0.9, 0.99]

    product_list = list(product(num_shapes_list, num_instances_per_shape_list, min_visibility))
    
    count = 0
    instances_per_sweep = 2
    base_dir = os.path.join("3D_DoYouSeeMe", "shape_discrimination")
    data = [] 
    for num_shapes, max_instances_per_shape, min_visibility in product_list:
        for i in range(instances_per_sweep):
            image_path, ground_truth = generate_single_discrimination_image(
                scene, light, num_shapes=num_shapes,
                max_instances_per_shape=max_instances_per_shape,
                min_visibility=min_visibility,
                output_path = os.path.join(base_dir, f"{count}.png")
            )
            print(f"Image generated at: {image_path}")
            count +=1
            data.append({
                "id": count,
                "image_path": image_path,
                "ground_truth": ground_truth,
            })