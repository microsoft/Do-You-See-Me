# imports specific to Blender's python API
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
output_dir = "letter_a_3d"

# Scene and lighting configuration from original code
scenes = ["city square", "bridge", "indoor", "outdoor", "playground", "hall", "grassland", "garage", "street", "beach", "station", "tunnel", "moonlit grass", "dusk city", "skywalk", "garden"]
lights = ["left", "middle", "right"]

# Light positions
light_position = {
    "left": [5, -5, 7],
    "middle": [0, 0, 7],
    "right": [-5, 5, 7]
}

import string

# Define the grid dimensions
HEIGHT = 9
WIDTH = 7

# Helper function to create an empty grid
def create_empty_grid():
    return [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

# Dictionary to store letter patterns
LETTER_PATTERNS = {}

# --- Define Patterns ---

# A (Provided by user)
LETTER_PATTERNS['A'] = [
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0]
]

# B
LETTER_PATTERNS['B'] = [
    [1, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 1, 1, 1, 0, 0, 0]
]

# C
LETTER_PATTERNS['C'] = [
    [0, 0, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 0, 0]
]

# D
LETTER_PATTERNS['D'] = [
    [1, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 1, 1, 1, 0, 0, 0]
]

# E
LETTER_PATTERNS['E'] = [
    [1, 1, 1, 1, 1, 1, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 0]
]

# F
LETTER_PATTERNS['F'] = [
    [1, 1, 1, 1, 1, 1, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0]
]

# G
LETTER_PATTERNS['G'] = [
    [0, 0, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 1, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 0, 0]
]

# H
LETTER_PATTERNS['H'] = [
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 1, 1, 1, 1, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0]
]

# I
LETTER_PATTERNS['I'] = [
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0]
]

# J
LETTER_PATTERNS['J'] = [
    [0, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [0, 1, 1, 1, 0, 0, 0]
]

# K
LETTER_PATTERNS['K'] = [
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 1, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0] # Adjusted last row to match stem
]

# L
LETTER_PATTERNS['L'] = [
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 0]
]

# M
LETTER_PATTERNS['M'] = [
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 0, 0, 0, 1, 1],
    [1, 0, 1, 0, 1, 0, 1],
    [1, 0, 0, 1, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1]
]

# N
LETTER_PATTERNS['N'] = [
    [1, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 0, 0, 1, 0],
    [1, 0, 1, 0, 0, 1, 0],
    [1, 0, 0, 1, 0, 1, 0],
    [1, 0, 0, 0, 1, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0]
]

# O
LETTER_PATTERNS['O'] = [
    [0, 0, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 0, 0]
]

# P
LETTER_PATTERNS['P'] = [
    [1, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0]
]

# Q
LETTER_PATTERNS['Q'] = [
    [0, 0, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0], # Adjusted tail
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 0, 1] # Adjusted tail
]


# R
LETTER_PATTERNS['R'] = [
    [1, 1, 1, 1, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 1, 1, 1, 0, 0, 0],
    [1, 0, 1, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0],
    [1, 0, 0, 0, 1, 0, 0]
]

# S
LETTER_PATTERNS['S'] = [
    [0, 0, 1, 1, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 0, 0]
]

# T
LETTER_PATTERNS['T'] = [
    [1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0]
]

# U
LETTER_PATTERNS['U'] = [
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [1, 0, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 1, 1, 0, 0]
]

# V
LETTER_PATTERNS['V'] = [
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0]
]

# W
LETTER_PATTERNS['W'] = [
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 0, 1],
    [1, 1, 0, 0, 0, 1, 1],
    [0, 1, 0, 0, 0, 1, 0], # Adjusted bottom width
    [0, 1, 0, 0, 0, 1, 0]  # Adjusted bottom width
]

# X
LETTER_PATTERNS['X'] = [
    [1, 0, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 1, 0, 0, 0, 1, 0], # Extend legs
    [1, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 1] # Extend legs
]


# Y
LETTER_PATTERNS['Y'] = [
    [1, 0, 0, 0, 0, 0, 1],
    [0, 1, 0, 0, 0, 1, 0],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0]
]

# Z
LETTER_PATTERNS['Z'] = [
    [1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0], # Extend bottom start
    [1, 1, 1, 1, 1, 1, 0]
]

color_map = {
    'red': (0.8, 0.1, 0.1, 1),
    'blue': (0.1, 0.1, 0.8, 1),
    'yellow': (0.8, 0.8, 0.1, 1),
    'green': (0.1, 0.8, 0.1, 1),
    'purple': (0.8, 0.1, 0.8, 1),
    'orange': (0.8, 0.4, 0.1, 1), 
    'black': (0.05, 0.05, 0.05, 1),
    'white': (0.9, 0.9, 0.9, 1),
}
    

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
        'green': (0.1, 0.8, 0.1, 1),
        'purple': (0.8, 0.1, 0.8, 1),
        'orange': (0.8, 0.4, 0.1, 1), 
        'black': (0.05, 0.05, 0.05, 1),
        'white': (0.9, 0.9, 0.9, 1),
    }
    
    node_pbr.inputs["Base Color"].default_value = color_map.get(color_name, (0.5, 0.5, 0.5, 1))
    # Add some roughness for more realistic appearance
    node_pbr.inputs["Roughness"].default_value = 0.4
    
    return material

def generate_3d_dot_letter_a(scene_name=None, light_type=None, output_path=None, 
                           dot_size=0.1, spacing=0.5, dot_type="sphere", 
                           dot_color="red", background_dots=False, letter='A'):
    """Generate a 3D dot-style letter A with random scene and lighting"""
    
    # If not specified, choose random scene and light
    if scene_name is None:
        scene_name = random.choice(scenes)
    if light_type is None:
        light_type = random.choice(lights)
    
    # Load scene
    scene_file = os.path.join(data_dir, "scenes", scene_name + ".blend")
    if not os.path.exists(scene_file):
        # If scene file doesn't exist, create a simple scene
        bpy.ops.wm.read_homefile(use_empty=True)
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
        ground = bpy.context.active_object
        ground.name = "Ground"
        # Create a simple grey material for the ground
        ground_mat = create_material("black")
        ground.data.materials.append(ground_mat)
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
    
    # Position camera
    if 'Camera' not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(0, -8, 4))
        camera = bpy.context.active_object
        camera.rotation_euler = (math.radians(70), 0, 0)
        bpy.context.scene.camera = camera
    else:
        camera = bpy.data.objects['Camera']
        # # Move camera to better position for letter viewing
        # camera.location = (0, -8, 4)
        # camera.rotation_euler = (math.radians(1), 0, 0)
    
    # Calculate center position for the letter
    grid_height = len(LETTER_PATTERNS[letter])
    grid_width = len(LETTER_PATTERNS[letter][0])
    
    # Center the letter in the scene
    center_x = -(grid_width * spacing) / 2
    center_y = (grid_height * spacing) / 2  # Center vertically
    center_z = 0  # Keep at ground level
    
    # Create material for dots
    dot_material = create_material(dot_color)
    if background_dots:
        background_material = create_material("black")
    
    # Fixed code:
    for row_idx, row in enumerate(LETTER_PATTERNS[letter]):
        for col_idx, is_active in enumerate(row):
            x = center_x + col_idx * spacing
            # Make the letter stand up by swapping y and z coordinates, but reverse row order
            y = center_y - (grid_height - 1 - row_idx) * spacing  # This inverts the vertical positioning
            z = 0.25  # Slight elevation from ground
            position = (x, y, z)
            
            # Create dot only if active, or if we want background dots
            if is_active or background_dots:
                if dot_type == "sphere":
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=dot_size, location=position, segments=16, ring_count=8)
                elif dot_type == "cube":
                    bpy.ops.mesh.primitive_cube_add(size=dot_size * 2, location=position)
                else:  # cylinder
                    bpy.ops.mesh.primitive_cylinder_add(radius=dot_size, depth=dot_size * 2, location=position)
                    bpy.context.active_object.rotation_euler = (math.pi/2, 0, 0)
                
                obj = bpy.context.active_object
                obj.name = f"dot_{row_idx}_{col_idx}"
                
                # Apply material
                if is_active:
                    obj.data.materials.append(dot_material)
                else:
                    obj.data.materials.append(background_material)
                
                # Add slight random rotation for visual interest
                if dot_type != "cylinder":
                    obj.rotation_euler = (
                        random.uniform(-0.1, 0.1),
                        random.uniform(-0.1, 0.1),
                        random.uniform(-0.1, 0.1)
                    )
    
    # Create a parent empty for all dots to make it easier to move them together
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    letter_parent = bpy.context.active_object
    letter_parent.name = f"Letter_{letter}_Parent"
    
    # Parent all dots to the empty
    for obj in bpy.data.objects:
        if obj.name.startswith("dot_"):
            obj.parent = letter_parent
    
    # Optional: Position and rotate the letter for better visibility
    letter_parent.location = (0, 0, 0)  # Move closer to camera
    letter_parent.rotation_euler = (0, 0, 0)  # No rotation needed when standing up
    slant_angle_x = -5
    slant_angle_z = 0
    letter_parent.rotation_euler = (math.radians(slant_angle_x), 0, math.radians(slant_angle_z))

    # Render
    if output_path is None:
        output_path = os.path.join(output_dir, f"letter_{letter}_3d_{scene_name}_{light_type}_{dot_type}_{dot_color}.png")
    
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    
    # Save JSON with parameters
    parameters = {
        "scene": scene_name,
        "light": light_type,
        "dot_type": dot_type,
        "dot_size": dot_size,
        "spacing": spacing,
        "dot_color": dot_color,
        "background_dots": background_dots,
        "letter": letter,
    }
    
    json_path = output_path.replace('.png', '.json')
    with open(json_path, 'w') as f:
        json.dump(parameters, f, indent=4)
    
    logging.info(f"Generated image: {output_path}")
    logging.info(f"Parameters: {json_path}")
    
    return output_path, parameters


def generate_3d_dot_letters(scene_name=None, light_type=None, output_path=None,
                                dot_size=0.05, spacing=0.4, dot_type="sphere",
                                dot_color="red", background_dots=False, letters=None):
    """Generate 3D dot-style letters (single or multiple) with random scene and lighting"""
    # Handle single or multiple letters
    if letters is None:
        letters = [random.choice(string.ascii_uppercase)]
    elif isinstance(letters, str):
        letters = [letters]

    # If not specified, choose random scene and light
    if scene_name is None:
        scene_name = random.choice(scenes)
    if light_type is None:
        light_type = random.choice(lights)

    # Load or setup scene (unchanged from original)
    scene_file = os.path.join(data_dir, "scenes", scene_name + ".blend")
    if not os.path.exists(scene_file):
        bpy.ops.wm.read_homefile(use_empty=True)
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
        ground = bpy.context.active_object
        ground_mat = create_material("black")
        ground.data.materials.append(ground_mat)
    else:
        bpy.ops.wm.open_mainfile(filepath=scene_file)

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

    # switch to GPU
    bpy.context.scene.cycles.device = 'GPU'

    # enable all GPU devices (CUDA / OPTIX / OPENCL as appropriate)
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'    # or 'OPTIX' / 'OPENCL'
    for dev in prefs.devices:
        dev.use = True

    
    # Position camera
    if 'Camera' not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(0, -8, 4))
        camera = bpy.context.active_object
        camera.rotation_euler = (math.radians(70), 0, 0)
        bpy.context.scene.camera = camera
    else:
        camera = bpy.data.objects['Camera']
        # # Move camera to better position for letter viewing
        # camera.location = (0, -8, 4)
        # camera.rotation_euler = (math.radians(1), 0, 0)

    # Create material for dots
    dot_material = create_material(dot_color)
    if background_dots:
        background_material = create_material("black")

    # Generate each letter at offset positions
    for idx, letter in enumerate(letters[::-1]):
        pattern = LETTER_PATTERNS.get(letter)
        grid_height = len(pattern)
        grid_width = len(pattern[0])
        # offset each letter along X
        offset_x = idx * (grid_width * spacing + spacing)
        center_x = -(grid_width * spacing) / 2 + offset_x
        center_y = (grid_height * spacing) / 2
        center_z = 0.5

        for row_idx, row in enumerate(pattern):
            for col_idx, is_active in enumerate(row):
                # x = center_x + col_idx * spacing
                x = center_x + (grid_width - 1 - col_idx) * spacing 
                y = center_y - (grid_height - 1 - row_idx) * spacing
                z = center_z
                if not is_active and not background_dots:
                    continue
                # Create dot primitive
                if dot_type == "sphere":
                    bpy.ops.mesh.primitive_uv_sphere_add(radius=dot_size, location=(x, y, z), segments=16, ring_count=8)
                elif dot_type == "cube":
                    bpy.ops.mesh.primitive_cube_add(size=dot_size * 2, location=(x, y, z))
                else:
                    bpy.ops.mesh.primitive_cylinder_add(radius=dot_size, depth=dot_size * 2, location=(x, y, z))
                    bpy.context.active_object.rotation_euler = (math.pi/2, 0, 0)

                obj = bpy.context.active_object
                obj.name = f"dot_{letter}_{row_idx}_{col_idx}"
                obj.data.materials.append(dot_material if is_active else background_material)
                if dot_type != "cylinder":
                    obj.rotation_euler = (random.uniform(-0.1, 0.1),
                                          random.uniform(-0.1, 0.1),
                                          random.uniform(-0.1, 0.1))

        # Parent dots for this letter
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
        parent = bpy.context.active_object
        parent.name = f"Letter_{letter}_Parent"
        for obj in bpy.data.objects:
            if obj.name.startswith(f"dot_{letter}_"):
                obj.parent = parent

        # Optional: Position and rotate the letter for better visibility
        parent.location = (0, 0, 0)  # Move closer to camera
        parent.rotation_euler = (0, 0, 0)  # No rotation needed when standing up
        slant_angle_x = -10
        slant_angle_z = 0
        parent.rotation_euler = (math.radians(slant_angle_x), 0, math.radians(slant_angle_z))

    # Render
    if output_path is None:
        output_path = os.path.join(output_dir, f"letter_{letter}_3d_{scene_name}_{light_type}_{dot_type}_{dot_color}.png")
    
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    
    # Save JSON with parameters
    parameters = {
        "scene": scene_name,
        "light": light_type,
        "dot_type": dot_type,
        "dot_size": dot_size,
        "spacing": spacing,
        "dot_color": dot_color,
        "background_dots": background_dots,
        "letters": letters,
    }
    
    json_path = output_path.replace('.png', '.json')
    with open(json_path, 'w') as f:
        json.dump(parameters, f, indent=4)
    
    logging.info(f"Generated image: {output_path}")
    logging.info(f"Parameters: {json_path}")


    # Final positioning, rendering, and JSON export (unchanged)
    # ... existing rendering and JSON dump code ...
    return output_path, parameters  




from itertools import product

# Example usage with different variations
if __name__ == "__main__":
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    variations = [
        {"dot_type": "sphere", "background_dots": False},
        {"dot_type": "cube", "background_dots": False},
        {"dot_type": "cylinder", "background_dots": False},
    ]
    
    dot_size_list = [0.05, 0.08, 0.11, 0.14]
    do_spacing_list = [0.4, 0.5]
    letter_numbers = [1, 2]

    # Generate all combinations of variations
    product_variations = list(product(variations, dot_size_list, do_spacing_list, letter_numbers))
    count = 0
    max_instance_per_sweep = 2
    output_dir = "3D_DoYouSeeMe/letter_disambiguation"

    for entry in product_variations:
        for i in range(max_instance_per_sweep):
            # Unpack the variation tuple
            variation, dot_size, spacing, letter_number = entry
            scene = random.choice(scenes)
            light = random.choice(lights)
            letters = [random.choice(string.ascii_uppercase) for _ in range(letter_number)]
            image_path, parameters = generate_3d_dot_letters(
                scene_name=scene,
                light_type=light,
                dot_type=variation["dot_type"],
                dot_color=random.choice(list(color_map.keys())),
                background_dots=variation["background_dots"],
                dot_size=dot_size,
                spacing=spacing,
                letters=letters,
                output_path=os.path.join(output_dir, f"{count}.png")
            )
            count += 1
