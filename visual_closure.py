import matplotlib.pyplot as plt
import itertools
import os
from tqdm import tqdm

import matplotlib.pyplot as plt
import numpy as np
import math

def define_rectangle(x=0.0, y=0.0, width=1.0, height=1.0, subdivisions=4):
    """
    Define a rectangle as a list of (x, y) vertices, subdividing each edge.

    Parameters:
    -----------
    x, y        : float
        The lower-left corner of the rectangle (or however you like to define it).
    width       : float
        The width of the rectangle along the x-axis.
    height      : float
        The height of the rectangle along the y-axis.
    subdivisions: int
        How many segments to split each edge into. 
        For example, if subdivisions=4, each edge is broken into 4 sub-segments 
        (hence 5 points along that edge).

    Returns:
    --------
    vertices : list of (float, float)
        A list of vertex coordinates in order around the perimeter.
        The shape is closed, so the last vertex = the first vertex.
    """

    # We’ll create points around the perimeter in order: bottom edge → right edge → top edge → left edge
    # Each edge will have `subdivisions + 1` points, but to avoid duplicating the corner,
    # we won’t re-append the corner for the next edge except at the very end.

    vertices = []

    # 1. Bottom edge (from left to right)
    for i in range(subdivisions + 1):
        # alpha goes from 0 to 1 in equally spaced steps
        alpha = i / subdivisions
        vx = x + alpha * width
        vy = y
        vertices.append((vx, vy))

    # 2. Right edge (from bottom to top)
    for i in range(1, subdivisions + 1):
        alpha = i / subdivisions
        vx = x + width
        vy = y + alpha * height
        vertices.append((vx, vy))

    # 3. Top edge (from right to left)
    for i in range(1, subdivisions + 1):
        alpha = i / subdivisions
        vx = x + width - alpha * width
        vy = y + height
        vertices.append((vx, vy))

    # 4. Left edge (from top back down to bottom)
    for i in range(1, subdivisions + 1):
        alpha = i / subdivisions
        vx = x
        vy = y + height - alpha * height
        vertices.append((vx, vy))

    return vertices

def define_capsule(center=(0.0, 0.0), width=2.0, height=1.0, n_arc_points=16):
    """
    Returns a list of (x, y) approximating a 'stadium' or capsule shape:
     - overall width is the horizontal dimension
     - overall height is the vertical dimension
       (which is effectively the diameter of the semicircles)
    """
    import math
    cx, cy = center
    
    # The radius of the semicircle is height / 2
    r = height / 2
    
    # The length of the straight lines is width - 2*r
    # (assuming width >= 2*r)
    half_straight = (width - 2*r) / 2
    
    # We'll define the left semicircle center and the right semicircle center
    left_center  = (cx - half_straight, cy)
    right_center = (cx + half_straight, cy)
    
    # Helper to create an arc
    def arc(center_x, center_y, start_angle, end_angle, radius, n_points):
        pts = []
        for i in range(n_points+1):
            t = start_angle + (end_angle - start_angle)*i/n_points
            px = center_x + radius * math.cos(t)
            py = center_y + radius * math.sin(t)
            pts.append((px, py))
        return pts
    
    left_arc_top = arc(left_center[0], left_center[1], 
                       start_angle= math.pi/2, 
                       end_angle  = -math.pi/2, 
                       radius=r, n_points=n_arc_points)
    bottom_line = []
    bottom_left = left_arc_top[-1]
    bottom_right = (right_center[0], right_center[1] - r)
    bottom_line.append(bottom_right)
    
    right_arc_bottom = arc(right_center[0], right_center[1], 
                           start_angle=-math.pi/2, 
                           end_angle= math.pi/2, 
                           radius=r, n_points=n_arc_points)
    top_line = []
    top_right = right_arc_bottom[-1]
    top_left = (left_center[0], left_center[1] + r)
    top_line.append(top_left)


    vertices = []
    vertices.extend(left_arc_top)
    vertices.extend(bottom_line)        
    vertices.extend(right_arc_bottom)   
    vertices.extend(top_line)           

    return vertices


def define_fine_grained_star(
    num_points=10,
    center=(0.0, 0.0),
    outer_radius=1.0,
    inner_radius=0.5,
    num_subdivisions=2
):
    """
    Returns a list of (x, y) vertices forming a fine-grained star with
    'num_points' points.
    
    Each edge between consecutive star vertices is subdivided into additional
    points (num_subdivisions), so the shape can be rendered with finer
    granularity.
    
    Parameters
    ----------
    num_points : int
        The number of major outer points on the star (e.g., 5 for a typical star).
    center : tuple of float
        (x, y) coordinates for the center of the star.
    outer_radius : float
        The radius from center to each "outer" vertex.
    inner_radius : float
        The radius from center to each "inner" vertex.
    num_subdivisions : int
        The number of subdivisions to place on each edge between star vertices.
        For example, if num_subdivisions=10, each edge will be split into 10
        smaller segments, generating 11 points along that edge.
        
    Returns
    -------
    vertices : list of tuple of float
        A list of points (x, y). The first point of each edge is the star's
        vertex, and the following points are the subdivisions until the
        next vertex. The list ends at the star's closing vertex.
    """
    
    cx, cy = center
    vertices = []
    star_vertices = []
    for i in range(num_points * 2):
        # Choose outer or inner radius depending on even or odd index
        r = outer_radius if i % 2 == 0 else inner_radius
        # Angle for this vertex (half-step increments)
        theta = math.pi * i / num_points
        vx = cx + r * math.cos(theta)
        vy = cy + r * math.sin(theta)
        star_vertices.append((vx, vy))

    for i in range(len(star_vertices)):
        # Current vertex
        x0, y0 = star_vertices[i]
        # Next vertex (wrap around using modulo)
        x1, y1 = star_vertices[(i + 1) % len(star_vertices)]

        vertices.append((x0, y0))
        
        # Compute subdivisions
        for s in range(1, num_subdivisions):
            t = s / float(num_subdivisions)
            # Linear interpolation between (x0, y0) and (x1, y1)
            x_sub = (1 - t)*x0 + t*x1
            y_sub = (1 - t)*y0 + t*y1
            vertices.append((x_sub, y_sub))

    vertices.append(star_vertices[0])
    
    return vertices

def define_circle_approx(center=(0,0), radius=1.0, n_points=64):
    """
    Approximate a circle by n_points around the circumference.
    """
    cx, cy = center
    vertices = []
    for i in range(n_points):
        theta = 2.0 * math.pi * i / n_points
        vx = cx + radius * math.cos(theta)
        vy = cy + radius * math.sin(theta)
        vertices.append((vx, vy))
    return vertices



import math

def define_regular_pentagon(n_sides=5, center=(0,0), radius=1.0, subdivisions=4):
    """
    Returns a list of (x, y) vertices approximating a regular polygon with n_sides, 
    centered at (center_x, center_y), with a given radius.
    
    Each side is subdivided into `subdivisions` segments. So each edge from corner i 
    to corner i+1 is broken into smaller steps. 

    Example:
        - If n_sides=4 (square) and subdivisions=2, each edge is split into 2 smaller segments 
          (so you get 3 points per edge).
        - If n_sides=5 (pentagon) and subdivisions=3, each edge is split into 3 sub-segments, etc.
    """
    cx, cy = center

    # 1. First, get the "corner" vertices (one per side).
    corner_vertices = []
    for i in range(n_sides):
        theta = 2.0 * math.pi * i / n_sides
        vx = cx + radius * math.cos(theta)
        vy = cy + radius * math.sin(theta)
        corner_vertices.append((vx, vy))

    # 2. Now, subdivide each edge between corner i and corner (i+1) % n_sides
    granular_vertices = []
    for i in range(n_sides):
        start = corner_vertices[i]
        end   = corner_vertices[(i + 1) % n_sides]

        # We'll break the edge [start -> end] into `subdivisions` segments,
        # meaning we place `subdivisions + 1` points along that edge, 
        # but skip re-appending the 'end' corner to avoid duplication 
        # (except on the final edge, if you want a fully closed list, 
        #  you can manually add it at the end).
        
        for s in range(subdivisions):
            alpha = s / subdivisions  # goes from 0 to (subdivisions-1)/subdivisions
            x_sub = start[0] + alpha * (end[0] - start[0])
            y_sub = start[1] + alpha * (end[1] - start[1])
            granular_vertices.append((x_sub, y_sub))
    
    # If you want the final corner to appear exactly at the end, append it:
    granular_vertices.append(corner_vertices[0])  # Return to the first corner to "close"
    return granular_vertices

def define_regular_hexagon(n_sides=6, center=(0,0), radius=1.0, subdivisions=4):
    """
    Returns a list of (x, y) vertices approximating a regular polygon with n_sides, 
    centered at (center_x, center_y), with a given radius.
    
    Each side is subdivided into `subdivisions` segments. So each edge from corner i 
    to corner i+1 is broken into smaller steps. 

    Example:
        - If n_sides=4 (square) and subdivisions=2, each edge is split into 2 smaller segments 
          (so you get 3 points per edge).
        - If n_sides=5 (pentagon) and subdivisions=3, each edge is split into 3 sub-segments, etc.
    """
    cx, cy = center

    # 1. First, get the "corner" vertices (one per side).
    corner_vertices = []
    for i in range(n_sides):
        theta = 2.0 * math.pi * i / n_sides
        vx = cx + radius * math.cos(theta)
        vy = cy + radius * math.sin(theta)
        corner_vertices.append((vx, vy))

    # 2. Now, subdivide each edge between corner i and corner (i+1) % n_sides
    granular_vertices = []
    for i in range(n_sides):
        start = corner_vertices[i]
        end   = corner_vertices[(i + 1) % n_sides]

        # We'll break the edge [start -> end] into `subdivisions` segments,
        # meaning we place `subdivisions + 1` points along that edge, 
        # but skip re-appending the 'end' corner to avoid duplication 
        # (except on the final edge, if you want a fully closed list, 
        #  you can manually add it at the end).
        
        for s in range(subdivisions):
            alpha = s / subdivisions  # goes from 0 to (subdivisions-1)/subdivisions
            x_sub = start[0] + alpha * (end[0] - start[0])
            y_sub = start[1] + alpha * (end[1] - start[1])
            granular_vertices.append((x_sub, y_sub))
    
    # If you want the final corner to appear exactly at the end, append it:
    granular_vertices.append(corner_vertices[0])  # Return to the first corner to "close"
    return granular_vertices

def define_regular_rectangle(n_sides=4, center=(0,0), radius=1.0, subdivisions=2):
    """
    Returns a list of (x, y) vertices approximating a regular polygon with n_sides, 
    centered at (center_x, center_y), with a given radius.
    
    Each side is subdivided into `subdivisions` segments. So each edge from corner i 
    to corner i+1 is broken into smaller steps. 

    Example:
        - If n_sides=4 (square) and subdivisions=2, each edge is split into 2 smaller segments 
          (so you get 3 points per edge).
        - If n_sides=5 (pentagon) and subdivisions=3, each edge is split into 3 sub-segments, etc.
    """
    cx, cy = center

    # 1. First, get the "corner" vertices (one per side).
    corner_vertices = []
    for i in range(n_sides):
        theta = 2.0 * math.pi * i / n_sides
        vx = cx + radius * math.cos(theta)
        vy = cy + radius * math.sin(theta)
        corner_vertices.append((vx, vy))

    # 2. Now, subdivide each edge between corner i and corner (i+1) % n_sides
    granular_vertices = []
    for i in range(n_sides):
        start = corner_vertices[i]
        end   = corner_vertices[(i + 1) % n_sides]

        for s in range(subdivisions):
            alpha = s / subdivisions  # goes from 0 to (subdivisions-1)/subdivisions
            x_sub = start[0] + alpha * (end[0] - start[0])
            y_sub = start[1] + alpha * (end[1] - start[1])
            granular_vertices.append((x_sub, y_sub))
    
    # If you want the final corner to appear exactly at the end, append it:
    granular_vertices.append(corner_vertices[0])  # Return to the first corner to "close"
    return granular_vertices

def define_regular_triangle(n_sides=3, center=(0,0), radius=1.0, subdivisions=4):
    """
    Returns a list of (x, y) vertices approximating a regular polygon with n_sides, 
    centered at (center_x, center_y), with a given radius.
    
    Each side is subdivided into `subdivisions` segments. So each edge from corner i 
    to corner i+1 is broken into smaller steps. 

    Example:
        - If n_sides=4 (square) and subdivisions=2, each edge is split into 2 smaller segments 
          (so you get 3 points per edge).
        - If n_sides=5 (pentagon) and subdivisions=3, each edge is split into 3 sub-segments, etc.
    """
    cx, cy = center

    # 1. First, get the "corner" vertices (one per side).
    corner_vertices = []
    for i in range(n_sides):
        theta = 2.0 * math.pi * i / n_sides
        vx = cx + radius * math.cos(theta)
        vy = cy + radius * math.sin(theta)
        corner_vertices.append((vx, vy))

    # 2. Now, subdivide each edge between corner i and corner (i+1) % n_sides
    granular_vertices = []
    for i in range(n_sides):
        start = corner_vertices[i]
        end   = corner_vertices[(i + 1) % n_sides]


        for s in range(subdivisions):
            alpha = s / subdivisions  # goes from 0 to (subdivisions-1)/subdivisions
            x_sub = start[0] + alpha * (end[0] - start[0])
            y_sub = start[1] + alpha * (end[1] - start[1])
            granular_vertices.append((x_sub, y_sub))
    
    # If you want the final corner to appear exactly at the end, append it:
    granular_vertices.append(corner_vertices[0])  # Return to the first corner to "close"
    return granular_vertices


def draw_segments(ax, segments, color='k'):
    """
    Given a list of ((x1, y1), (x2, y2)) segments,
    draw them on the given axes object 'ax'.
    """
    for (x1, y1), (x2, y2) in segments:
        ax.plot([x1, x2], [y1, y2], color=color)

def create_unconnected_shape(vertices, omit_edges=[], omit_partial=[]):
    """
    vertices: list of points in path order
    omit_edges: list of edges (start_index, end_index) to remove entirely
    omit_partial: list of edges on which we remove only the midpoint or a portion,
                  so it looks partially drawn.
    Returns a list of segment pairs that can be drawn.
    """
    edges = []
    num_pts = len(vertices)
    for i in range(num_pts):
        start = vertices[i]
        end   = vertices[(i+1) % num_pts]  # wrap around

        # If this edge is in `omit_edges`, skip it entirely
        if (i, (i+1) % num_pts) in omit_edges or ((i+1) % num_pts, i) in omit_edges:
            continue
        
        # If this edge is in `omit_partial`, we'll skip part of it
        if (i, (i+1) % num_pts) in omit_partial or ((i+1) % num_pts, i) in omit_partial:
            # Example: draw only half the segment
            midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
            edges.append((start, midpoint))  # only partial
        else:
            # Full edge
            edges.append((start, end))
    
    return edges

import random

def distort_shape(vertices, max_offset=1, num_edges_to_distort=1, omit_edges=[], omit_partial=[]):
    """
    Return a new list of vertices with random perturbations.
    'max_offset' controls how large the perturbation can be.
    """
    distorted = []
    vertexes = []
    for i in range(len(vertices)-1):
        vertexes.append((i, i+1))

    for omit_edge in omit_edges:
        if omit_edge in vertexes:
            vertexes.remove(omit_edge)
    for omit_partial in omit_partial:
        if omit_partial in vertexes:
            vertexes.remove(omit_partial)

    vertexes = list(set(list(itertools.chain.from_iterable(vertexes))))
    selected_edges = random.sample(vertexes, num_edges_to_distort)

    for idx, (x, y) in enumerate(vertices):
        dx = 0
        dy = 0
        if idx in selected_edges:
            # random.uniform(-max_offset, max_offset) for x and y
            dx = random.sample([-max_offset, max_offset], 1)[0]
            dy = random.sample([-max_offset, max_offset], 1)[0]
        distorted.append((x + dx, y + dy))
    return distorted


def visual_closure_fn(fname, base_vertices, visual_closure_offset, num_edges_to_distort=1, num_edges_to_remove_complete=1, num_edges_to_remove_partial=1):    
    max_vertices = len(base_vertices)
    omit_partial = []
    vertex_init_list = random.sample(range(max_vertices-2), num_edges_to_remove_partial)
    for vertex_init in vertex_init_list:
        omit_partial.append((vertex_init, vertex_init+1))

    omit_edges = []
    vertex_init_list = random.sample(range(max_vertices-2), num_edges_to_remove_complete)
    for vertex_init in vertex_init_list:
        omit_edges.append((vertex_init, vertex_init+1))

    unconnected_segments = create_unconnected_shape(
        base_vertices,
        omit_edges=omit_edges,     
        omit_partial=omit_partial    
    )

    connected_segments = create_unconnected_shape(base_vertices)
    
    # 3. Create three wrong versions via distortion
    wrong_shapes_segments = []
    for _ in range(3):
        distorted_vertices = distort_shape(base_vertices, max_offset=visual_closure_offset, num_edges_to_distort=num_edges_to_distort, omit_edges=omit_edges, omit_partial=omit_partial)
        segs = create_unconnected_shape(distorted_vertices, omit_edges=omit_edges, omit_partial=omit_partial)
        wrong_shapes_segments.append(segs)
    
    # --- Plot and save ---
    fig, axes = plt.subplots(2, 4, figsize=(12, 3))
    
    axes[0, 0].set_title("Target Shape")
    draw_segments(axes[0, 0], connected_segments)



    segment_list = [unconnected_segments] + wrong_shapes_segments
    
    idx = list(range(4))
    random.shuffle(idx)
    segment_list = [segment_list[i] for i in idx]
    correct_option = idx.index(0)
    for i in range(4):
        axes[1, i].set_title(f"Option {i+1}")
        draw_segments(axes[1, i], segment_list[i])
    # Hide the axes for clarity
    for ax in axes.flatten():
        ax.set_aspect('equal')
        ax.axis('off')
    
    plt.tight_layout()
    # plt.show()
    plt.savefig(fname)
    plt.close()
    return correct_option+1

shapes_list = [define_capsule, define_fine_grained_star, define_regular_hexagon, define_circle_approx, define_regular_pentagon, define_regular_rectangle, define_regular_triangle]
visual_closure_offset_list = [0.1, 0.12, 0.14]
num_edges_to_distort_list = [1, 3]
num_edges_to_remove_complete_list = [1, 3]
num_edges_to_remove_partial_list = [1, 3]



sweep_list = itertools.product(shapes_list, visual_closure_offset_list, num_edges_to_distort_list, num_edges_to_remove_complete_list, num_edges_to_remove_partial_list)
base_dir = "visual_discrimination/sweep/visual_closure"
if not os.path.exists(base_dir):
    os.makedirs(base_dir)
idx = 0

data = []
for sweep in tqdm(sweep_list):
    define_shape, visual_closure_offset, num_edges_to_distort, num_edges_to_remove_complete, num_edges_to_remove_partial = sweep
    base_vertices = define_shape()
    fname = os.path.join(base_dir, f"{idx}.png")
    answer = visual_closure_fn(fname, base_vertices, visual_closure_offset=visual_closure_offset, num_edges_to_distort=num_edges_to_distort, num_edges_to_remove_complete=num_edges_to_remove_complete, num_edges_to_remove_partial=num_edges_to_remove_partial)
    data.append({
        "filename": f"{idx}.png",
        "answer": answer,
        "sweep": [visual_closure_offset, num_edges_to_distort, num_edges_to_remove_complete, num_edges_to_remove_partial]
    })

    idx += 1

import pandas as pd
pd.DataFrame(data).to_csv(os.path.join(base_dir, "dataset_info.csv") , index=False)