# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

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

# Scene and lighting configuration from original code
scenes = ["city square", "bridge", "indoor", "outdoor", "playground", "hall", "grassland", "garage", "street", "beach", "station", "tunnel", "moonlit grass", "dusk city", "skywalk", "garden"]
lights = ["left", "middle", "right"]

# Shape types for discrimination
shape_types_3d = ['cube', 'sphere', 'cylinder', 'cone', 'torus']

# bounds of valid locations where the foreground object can be placed
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

def check_occlusion_level(obj, camera, existing_objects, min_visibility=0.3):
    """
    Check if an object is sufficiently visible from the camera
    Returns True if object is visible enough, False otherwise
    """
    scene = bpy.context.scene
    render = scene.render
    
    # Create a temporary mesh to get vertex positions
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    mesh = obj_eval.to_mesh()
    
    # Get all vertices in world space
    vertices_world = [obj.matrix_world @ v.co for v in mesh.vertices]
    obj_eval.to_mesh_clear()
    
    # Check how many vertices are visible from camera
    visible_count = 0
    total_count = len(vertices_world)
    
    for vertex in vertices_world:
        # Convert world position to camera view
        camera_coord = world_to_camera_view(scene, camera, vertex)
        
        # Check if point is within camera view
        if 0 <= camera_coord.x <= 1 and 0 <= camera_coord.y <= 1 and camera_coord.z > 0:
            # Ray cast to check for occlusion
            direction = (vertex - camera.location).normalized()
            ray_result = scene.ray_cast(
                depsgraph,
                camera.location,
                direction,
                distance=(vertex - camera.location).length + 0.1
            )
            
            if ray_result[0]:  # Hit something
                hit_obj = ray_result[4]
                if hit_obj == obj:  # Hit the object itself
                    visible_count += 1
            else:  # No collision, vertex is visible
                visible_count += 1
    
    visibility_ratio = visible_count / total_count if total_count > 0 else 0
    return visibility_ratio >= min_visibility, visibility_ratio


def get_shape_z_offset(shape_type, rotation_euler, size=1.0):
    """
    Calculate a more accurate z-offset based on shape geometry and rotation.
    
    Args:
        shape_type (str): Type of shape ('cube', 'sphere', etc.)
        rotation_euler (tuple): (x, y, z) rotation in radians
        size (float): Base size of the shape
    
    Returns:
        float: Z-offset to place shape properly on ground
    """
    # Extract rotation components
    rot_x, rot_y, rot_z = rotation_euler
    
    if shape_type == 'sphere':
        # Sphere is always the radius from ground regardless of rotation
        return size * 0.75
    
    elif shape_type == 'cube':
        # For a cube, calculate the distance from center to lowest vertex after rotation
        # The half-side length of the cube
        half_side = size * 0.75  
        
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
        height = size * 1.5
        radius = size * 0.75
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
        height = size * 1.5
        radius = size * 0.75
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
        major_radius = size * 0.75
        minor_radius = size * 0.25
        
        # With any rotation, the lowest point will be at major_radius + minor_radius from center
        # But we need to account for rotation
        
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
    return size * 0.5

# def get_shape_z_offset(shape_type, rotation_euler):
#     """
#     Get the z-offset for each shape type to ensure it sits properly on the ground
#     Takes into account the shape type and rotation
#     """
#     # Base offsets for each shape type when not rotated
#     offsets = {
#         'cube': 0.75,  # Half of the cube size
#         'sphere': 0.75,  # Radius of the sphere
#         'cylinder': 0.75,  # Half of the cylinder height
#         'cone': 0.75,  # Half of the cone height
#         'torus': 0.25  # Minor radius of the torus
#     }
    
#     # Adjust for rotation (particularly for cylinder and cone)
#     if shape_type in ['cylinder', 'cone']:
#         # If rotated around x or y axis, adjust offset
#         x_rot = rotation_euler[0]
#         y_rot = rotation_euler[1]
        
#         # If significantly rotated, adjust offset
#         if abs(x_rot) > math.pi/4 or abs(y_rot) > math.pi/4:
#             # When on its side, use the radius as the offset
#             offsets[shape_type] = 0.75
    
#     return offsets.get(shape_type, 0.5)

def remap_dict_for_json(d):
    if isinstance(d, dict):
        return {str(k): v for k, v in d.items()}
    else:
        raise TypeError("Input must be a dictionary")



def check_object_collision(obj1, obj2, min_distance=0.1):
    """
    Check if two objects are colliding or too close to each other.
    Uses bounding box approximation for simplicity and performance.
    
    Args:
        obj1, obj2: The two objects to check
        min_distance: Minimum distance between objects
        
    Returns:
        bool: True if objects are colliding/too close, False otherwise
    """
    # Get world-space bounding boxes
    bbox1 = [obj1.matrix_world @ Vector(corner) for corner in obj1.bound_box]
    bbox2 = [obj2.matrix_world @ Vector(corner) for corner in obj2.bound_box]
    
    # Find min/max of each bounding box
    min1 = Vector((min(v.x for v in bbox1), min(v.y for v in bbox1), min(v.z for v in bbox1)))
    max1 = Vector((max(v.x for v in bbox1), max(v.y for v in bbox1), max(v.z for v in bbox1)))
    
    min2 = Vector((min(v.x for v in bbox2), min(v.y for v in bbox2), min(v.z for v in bbox2)))
    max2 = Vector((max(v.x for v in bbox2), max(v.y for v in bbox2), max(v.z for v in bbox2)))
    
    # Check for overlap in all three dimensions
    # Add min_distance to create some padding
    if (max1.x + min_distance < min2.x or max2.x + min_distance < min1.x or
        max1.y + min_distance < min2.y or max2.y + min_distance < min1.y or
        max1.z + min_distance < min2.z or max2.z + min_distance < min1.z):
        return False  # No collision
    
    return True  # Collision detected

def position_camera_for_form_constancy_task():
    """
    Adjusts the camera to ensure it is:
    1. In a plane parallel to the XY plane
    2. Equidistant from both left and right group centers
    3. Preserves the optimal viewpoint if camera already exists
    """
    # Define group positions (from the main function)
    left_group_center = (-4, -10, 0)
    right_group_center = (4, -10, 0)
    
    # Calculate the midpoint between the two group centers
    midpoint_x = (left_group_center[0] + right_group_center[0]) / 2  # = 0
    midpoint_y = (left_group_center[1] + right_group_center[1]) / 2  # = -10
    midpoint_z = (left_group_center[2] + right_group_center[2]) / 2  # = 0
    
    # Get or create the camera
    if 'Camera' not in bpy.data.objects:
        # If no camera exists, create one at an optimal position
        camera_x = midpoint_x  # Center the camera horizontally
        camera_y = midpoint_y - 10  # Move back from the objects
        camera_z = 8  # Raise the camera up to look down at the scene
        
        bpy.ops.object.camera_add(location=(camera_x, camera_y, camera_z))
        camera = bpy.context.active_object
        bpy.context.scene.camera = camera
    else:
        # Camera already exists with optimal positioning - preserve its location
        camera = bpy.data.objects['Camera']
        
        # We only need to adjust the X-coordinate to ensure it's equidistant from both groups
        # Keep Y and Z coordinates as they are (preserving optimal viewpoint)
        camera.location.x = midpoint_x
    
    # Calculate the target point to look at (midpoint between groups)
    target_x = midpoint_x
    target_y = midpoint_y
    target_z = midpoint_z + 1  # Slightly above the objects for better view
    
    # Make the camera look at the target point
    # Create an empty as a target
    if "Camera_Target" in bpy.data.objects:
        target_empty = bpy.data.objects["Camera_Target"]
        target_empty.location = (target_x, target_y, target_z)
    else:
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(target_x, target_y, target_z))
        target_empty = bpy.context.active_object
        target_empty.name = "Camera_Target"
    
    # Use the track_to constraint to make the camera face the target point
    # First check if constraint already exists
    track_constraint = None
    for constraint in camera.constraints:
        if constraint.type == 'TRACK_TO':
            track_constraint = constraint
            break
    
    if not track_constraint:
        track_constraint = camera.constraints.new(type='TRACK_TO')
        track_constraint.track_axis = 'TRACK_NEGATIVE_Z'  # Blender's camera looks down its -Z axis
        track_constraint.up_axis = 'UP_Y'  # Keep the camera upright
    
    track_constraint.target = target_empty
    
    # Add small random jitter to camera rotation for realism
    camera.rotation_euler[0] += math.radians(random.uniform(-0.5, 0.5))
    camera.rotation_euler[1] += math.radians(random.uniform(-0.5, 0.5))
    
    return camera

def generate_form_constancy_task(scene_name, light_type, 
                                 output_path=None, min_visibility=0.3,
                                 noise_amount = math.pi/4, 
                                 num_shapes=3):
    """Generate a visual form constancy task with two groups of shapes"""
    
    # Load scene (same as before)
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
    
    # Add lighting (same as before)
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
    
    # Configure render settings (same as before)
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.render.resolution_x = 800
    bpy.context.scene.render.resolution_y = 600
    bpy.context.scene.cycles.samples = 128
    
    # cycles settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    for dev in prefs.devices: dev.use = True

    # Position camera correctly - call our new function
    position_camera_for_form_constancy_task()    

    # Always set a different orientation, we will treat this task as adversarial only
    same_orientation = False
    
    # Select random shapes
    selected_shapes = random.sample(shape_types_3d, num_shapes)

    if num_shapes == 1 and selected_shapes[0] == 'sphere':
        selected_shapes = [random.choice(["cube", "cylinder", "cone", "torus"])] # avoid sphere if number of shapes is 1
    
    # Define group positions
    left_group_center = (-4, -10, 0)  # Left side of scene
    right_group_center = (4, -10, 0)   # Right side of scene
    
    # Spacing between shapes in each group
    shape_spacing = 2
        
    # Place objects for left group
    left_group_objects = []
    left_group_positions = []
    left_group_rotations = []
    
    for i, shape_type in enumerate(selected_shapes):
        # Calculate position offset from group center
        offset_x = (i - (num_shapes - 1) / 2) * shape_spacing
        position = (left_group_center[0] + offset_x, left_group_center[1], left_group_center[2])
        
        # Generate random rotation (ensuring no ground intersection)
        # IMPORTANT: For form constancy tasks, we need to be careful with rotation
        # Let's use completely fixed rotations for this task to ensure consistency
        rotation = (
            0,  # No rotation in x-axis to avoid ground intersection
            0,  # No rotation in y-axis to avoid ground intersection
            random.uniform(0, 2*math.pi)   # Only rotate around z-axis
        )
        
        scale_factor = 1
        if num_shapes > 3:
            scale_factor = 0.5
        
        # Create object
        if shape_type == 'cube':
            bpy.ops.mesh.primitive_cube_add(size=1.5*scale_factor, location=position)
        elif shape_type == 'sphere':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75*scale_factor, location=position)
        elif shape_type == 'cylinder':
            bpy.ops.mesh.primitive_cylinder_add(radius=0.75*scale_factor, depth=1.5*scale_factor, location=position)
        elif shape_type == 'cone':
            bpy.ops.mesh.primitive_cone_add(radius1=0.75*scale_factor, depth=1.5*scale_factor, location=position)
        elif shape_type == 'torus':
            bpy.ops.mesh.primitive_torus_add(major_radius=0.75*scale_factor, minor_radius=0.25*scale_factor, location=position)
        
        obj = bpy.context.active_object
        obj.name = f"left_{shape_type}_{i}"
        



        # Apply rotation - IMPORTANT: Use obj.rotation_euler and not just setting a tuple
        obj.rotation_euler[0] = rotation[0]
        obj.rotation_euler[1] = rotation[1]
        obj.rotation_euler[2] = rotation[2]
        
        # Calculate and apply z-offset to prevent ground intersection
        z_offset = get_shape_z_offset(shape_type, rotation)
        obj.location.z += z_offset
        
        # Store object information
        left_group_objects.append(obj)
        left_group_positions.append(obj.location[:])
        left_group_rotations.append((obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]))
        
        # Apply material
        color = random.choice(material_colors)
        material = create_material(color)
        obj.data.materials.append(material)
    
    # Place objects for right group
    right_group_objects = []
    substitutions = []
    
    for i, shape_type in enumerate(selected_shapes):
        # Calculate position offset from group center
        offset_x = (i - (num_shapes - 1) / 2) * shape_spacing
        position = (right_group_center[0] + offset_x, right_group_center[1], right_group_center[2])
        
        # Determine rotation
        if same_orientation:
            # Use EXACT same rotation as the corresponding left group object
            # We'll copy the rotation directly from the left object's rotation_euler
            left_rotation = left_group_rotations[i]
            rotation = left_rotation  # Use exactly the same rotation values
        else:
            # For "no" examples, add meaningful rotation difference
            base_rotation = left_group_rotations[i]
            # noise_amount = random.uniform(math.pi/4, math.pi/2)  # Between 45 and 90 degrees
            noise_axis = 2  # Always rotate around z-axis for simplicity
            
            rotation = list(base_rotation)
            if shape_type in ['cylinder', 'cone', 'spehere', 'torus']:
                noise_axis = random.choice([0, 1])
            else:
                noise_axis = 2

            rotation[noise_axis] += math.radians(noise_amount)
            rotation = tuple(rotation)
        
        # Create object
        if shape_type == 'cube':
            bpy.ops.mesh.primitive_cube_add(size=1.5*scale_factor, location=position)
        elif shape_type == 'sphere':
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.75*scale_factor, location=position)
        elif shape_type == 'cylinder':
            bpy.ops.mesh.primitive_cylinder_add(radius=0.75*scale_factor, depth=1.5*scale_factor, location=position)
        elif shape_type == 'cone':
            bpy.ops.mesh.primitive_cone_add(radius1=0.75*scale_factor, depth=1.5*scale_factor, location=position)
        elif shape_type == 'torus':
            bpy.ops.mesh.primitive_torus_add(major_radius=0.75*scale_factor, minor_radius=0.25*scale_factor, location=position)
        
        obj = bpy.context.active_object
        obj.name = f"right_{shape_type}_{i}"
        
        # Apply rotation - IMPORTANT: Use obj.rotation_euler and not just setting a tuple
        obj.rotation_euler[0] = rotation[0]
        obj.rotation_euler[1] = rotation[1]
        obj.rotation_euler[2] = rotation[2]
        
        # Calculate and apply z-offset to prevent ground intersection
        z_offset = get_shape_z_offset(shape_type, rotation)
        obj.location.z += z_offset
        
        # Use the same color as the corresponding left object
        left_material = left_group_objects[i].data.materials[0]
        obj.data.materials.append(left_material)
        
        right_group_objects.append(obj)
    
    # Render
    if output_path is None:
        # Create a descriptive filename
        same_str = "same" if same_orientation else "different"
        output_path = os.path.join(output_dir, f"form_constancy_{scene_name}_{light_type}_{same_str}.png")
    
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    
    # Save JSON with ground truth
    ground_truth = {
        "scene": scene_name,
        "light": light_type,
        "same_orientation": same_orientation,
        "shapes": [s for s in selected_shapes],
        "substitutions": substitutions if not same_orientation else [],
        "question": "Do the shapes on the left and right have the same orientation?",
        "answer": "Yes" if same_orientation else "No",
        'num_shapes': num_shapes,
        'noise_amount': noise_amount,
    }
    
    json_path = output_path.replace('.png', '.json')
    with open(json_path, 'w') as f:
        json.dump(ground_truth, f, indent=4)
    
    return output_path, ground_truth


from itertools import product
# Example usage
if __name__ == "__main__":
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate a single image with random parameters
    scene = random.choice(scenes)
    light = random.choice(lights)
    output_dir = "3D_DoYouSeeMe/form_constancy"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    rotation_list = [5, 7.5, 10, 12.5, 15]
    num_shapes = [1, 2, 3, 4]
    product_list = list(product(rotation_list, num_shapes))
    count = 0
    max_instance_per_sweep = 4
    for rotation, num_shapes in product_list:
        for i in range(max_instance_per_sweep):
            output_path = os.path.join(output_dir, f"form_constancy_{count}.png")
            # Generate image with specific parameters
            image_path, ground_truth = generate_form_constancy_task(
                scene, light, noise_amount=rotation, num_shapes=num_shapes,
                output_path=output_path)
            print(f"Image generated at: {image_path}")
            count += 1
            # break















