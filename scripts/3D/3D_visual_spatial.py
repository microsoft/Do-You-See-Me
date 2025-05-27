# imports specific to Blender's python API
import bpy
from mathutils import Vector, Euler
from bpy_extras.object_utils import world_to_camera_view
import bmesh
from mathutils import Euler
import os
import random
import math
import json
import logging
from collections import defaultdict
# --- add a slight tilt relative to the current orientation ---
import math

logging.basicConfig(level=logging.INFO)

# Configuration
data_dir = "data"
output_dir = "3D_DoYouSeeMe/3D_visual_spatial"

# Scene and lighting configuration from original code
scenes = ["city square", "bridge", "indoor", "outdoor", "playground", "hall", "grassland", "garage", "street", "beach", "station", "tunnel", "moonlit grass", "dusk city", "skywalk", "garden"]
lights = ["left", "middle", "right"]
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


def generate_random_shape_grid(
        grid_id,
        scene_name=None,
        light_type=None,
        grid_rows=6,
        grid_cols=5,
        spacing=3.0,
        shape_size=0.3,
        shapes=None,
        output_path=None):
    """
    Drops a grid_rows×grid_cols grid of random shapes into the scene,
    returns a dict mapping (grid_id, row, col) -> shape_name.
    """
    # --- reuse your scenes/lights definitions ---
    if scene_name is None:
        scene_name = random.choice(scenes)
    if light_type is None:
        light_type = random.choice(lights)

    # Load or create scene
    scene_file = os.path.join(data_dir, "scenes", scene_name + ".blend")
    if os.path.exists(scene_file):
        bpy.ops.wm.open_mainfile(filepath=scene_file)
    else:
        bpy.ops.wm.read_homefile(use_empty=True)
        bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, 0))
        ground = bpy.context.active_object
        ground.data.materials.append(create_material("white"))

    # add / position light (exactly as in your letter code)
    if os.path.exists(os.path.join(data_dir, "lights", "lights.blend")):
        with bpy.data.libraries.load(os.path.join(data_dir, "lights", "lights.blend")) as (_, data_to):
            data_to.objects = ["Point"]
        for obj in data_to.objects:
            if obj: bpy.context.collection.objects.link(obj)
    else:
        bpy.ops.object.light_add(type='POINT', location=light_position[light_type])
        bpy.context.active_object.data.energy = 1000
    if "Point" in bpy.data.objects:
        bpy.data.objects["Point"].location = Vector(light_position[light_type])


        # Position camera
    if 'Camera' not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(0, -8, 4))
        camera = bpy.context.active_object
        camera.rotation_euler = (math.radians(70), 0, 0)
        bpy.context.scene.camera = camera
    else:
        camera = bpy.data.objects['Camera']
        camera.location.z += 0.5
        tilt_angle = math.radians(-5)
        camera.rotation_euler.rotate_axis('X', tilt_angle)

    # cycles settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'CUDA'
    for dev in prefs.devices: dev.use = True

    # prepare shape factories
    shape_factories = {
        "sphere": lambda loc: bpy.ops.mesh.primitive_uv_sphere_add(radius=shape_size, location=loc),
        "cube":   lambda loc: bpy.ops.mesh.primitive_cube_add(size=shape_size*2, location=loc),
        "cylinder": lambda loc: (
            bpy.ops.mesh.primitive_cylinder_add(radius=shape_size, depth=shape_size*2, location=loc),
            setattr(
                bpy.context.active_object,
                "rotation_euler",
                Euler((math.pi/2, 0, 0))
            )
        ),        
        "cone":   lambda loc: bpy.ops.mesh.primitive_cone_add(radius1=shape_size, depth=shape_size*2, location=loc),
        "torus":  lambda loc: bpy.ops.mesh.primitive_torus_add(major_radius=shape_size, minor_radius=shape_size*0.3, location=loc),
    }
    if shapes is None:
        shapes = list(shape_factories.keys())

    mapping = {}
    bpy.ops.object.select_all(action='DESELECT')

    xmin = bounds[scene_name]["xmin"]
    xmax = bounds[scene_name]["xmax"]
    ymin = bounds[scene_name]["ymin"]
    ymax = bounds[scene_name]["ymax"]

    origin_x = ((xmax + xmin) / 2) - ((grid_cols - 1) * spacing) / 2
    origin_y = ((ymax + ymin) / 2) + ((grid_rows - 1) * spacing) / 2
    origin_z = 0.5

    # # grid origin so that whole grid is centered
    # origin_x = -((grid_cols - 1) * spacing) / 2
    # origin_y =  ((grid_rows - 1) * spacing) / 2
    # origin_z =  0.5
    origin_x = xmax
    origin_y = ymin + 5

    base_scale = 1
    scale_factor = 0.8


    for row in range(grid_rows):
        for col in range(grid_cols):
            shape_name = random.choice(shapes)
            x = origin_x - col * spacing
            y = origin_y + row * spacing
            z = origin_z
            print(x, y, z)
            shape_factories[shape_name]((x, y, z))
            obj = bpy.context.active_object
            obj.name = f"{grid_id}_{shape_name}_{row}_{col}"
            # give it a random material for clarity
            mat = create_material(random.choice(list(color_map.keys())))
            obj.data.materials.append(mat)
            # Scale down the object for size reduction
            obj.scale = (base_scale, base_scale, base_scale)
            mapping[(grid_id, row, col)] = shape_name
        base_scale *= scale_factor

    # render
    if output_path:
        bpy.context.scene.render.filepath = output_path
        bpy.ops.render.render(write_still=True)

    # also dump mapping to JSON alongside the image if you like
    if output_path:
        meta_path = output_path.replace('.png','.json')
        with open(meta_path,'w') as f:
            json.dump(
                {f"{gid}_{r}_{c}": s for (gid,r,c),s in mapping.items()},
                f, indent=2)

    return mapping

from itertools import product

if __name__ == "__main__":
    os.makedirs(output_dir, exist_ok=True)

    grid_rows_list = [2, 3, 4, 5]
    grid_cols_list = [2, 3, 4, 5]
    product_list = list(product(grid_rows_list, grid_cols_list))
    count = 0
    max_instance_per_sweep = 5
    for grid_rows, grid_cols in product_list:
        for i in range(max_instance_per_sweep):
            grid_id = f"grid_{count}"
            scene_name = random.choice(scenes)
            light_type = random.choice(lights)
            output_path = os.path.join(output_dir, f"{grid_id}.png")
            generate_random_shape_grid(
                grid_id=grid_id,
                scene_name=scene_name,
                light_type=light_type,
                grid_rows=grid_rows,
                grid_cols=grid_cols,
                output_path=output_path
            )
            count += 1
            logging.info(f"Generated {grid_id} with {grid_rows} rows and {grid_cols} columns in scene {scene_name} with light {light_type}.")
            # Clean up the scene for the next iteration
            bpy.ops.object.select_all(action='DESELECT')
