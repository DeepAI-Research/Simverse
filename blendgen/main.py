"""Blender script to render images of 3D models."""

import argparse
import platform
import sys
import json
import os
from typing import Any, Dict, List, Set
from mathutils import Vector

import bpy

# Get the directory of the currently executing script
current_dir = os.path.dirname(os.path.abspath(__file__))

# if the directory is blendgen, remove that
if current_dir.endswith("blendgen"):
    current_dir = os.path.dirname(current_dir)  

# Append the blendgen directory to sys.path
blendgen_path = os.path.join(current_dir)
sys.path.append(blendgen_path)

from blendgen.camera import reset_cameras, set_camera_settings
from blendgen.scene import reset_scene, scene_bbox
from blendgen.object import delete_invisible_objects, load_object
from blendgen.background import set_background

def read_combination(combination_file, index=0):
    """Reads a specified camera combination from a JSON file."""
    with open(combination_file, 'r') as file:
        combinations = json.load(file)
        return combinations[min(index, len(combinations) - 1)]

def get_hierarchy_bbox(obj, context):
    """Calculate the bounding box of an object and its children."""
    # Ensure the object's matrix_world is updated
    context.view_layer.update()
    
    # Initialize min and max coordinates with extremely large and small values
    min_coord = [float('inf'), float('inf'), float('inf')]
    max_coord = [-float('inf'), -float('inf'), -float('inf')]
    
    # Function to update min and max coordinates
    def update_bounds(obj):
        # Update the object's bounding box based on its world matrix
        bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
        for corner in bbox_corners:
            for i in range(3):
                min_coord[i] = min(min_coord[i], corner[i])
                max_coord[i] = max(max_coord[i], corner[i])
    
    # Recursive function to process each object
    def process_object(obj):
        update_bounds(obj)
        for child in obj.children:
            process_object(child)

    # Start processing from the root object
    process_object(obj)
    
    return min_coord, max_coord

def render_scene(
    object_file: str,
    output_dir: str,
    context: bpy.types.Context,
    combination_file,
    combination_index=0,
    height=1080,
    width=1920
) -> None:
    """Saves rendered video of the object."""
    os.makedirs(output_dir, exist_ok=True)
    scene = context.scene
    
    combination = read_combination(combination_file, combination_index)

    # Load the object
    if object_file.endswith(".blend"):
        bpy.ops.object.mode_set(mode="OBJECT")
        reset_cameras(scene)
        delete_invisible_objects(context)
    else:
        reset_scene()
        load_object(object_file, context=context)
    
    # Get the object just loaded and ensure all children are selected
    obj = [obj for obj in context.view_layer.objects.selected][0]
    obj.select_set(True)
    
    # Get the bounding box of the object and its children
    bbox_min, bbox_max = get_hierarchy_bbox(obj, context)
    print("Bounding box:", bbox_min, bbox_max)
    
    # Calculate the scale of the bounding box and scale the object if necessary
    bbox_dimensions = [bbox_max[i] - bbox_min[i] for i in range(3)]
    max_dimension = max(bbox_dimensions)
    print("Max dimension:", max_dimension)
    
    if max_dimension > 1:
        print("Scaling object")
        scale = 1 / max_dimension
        print("scale", scale)
        obj.scale = (scale, scale, scale)
        
    # Set up cameras
    
    set_camera_settings(context, combination)
    set_background(context, args, combination)
    
    # set height and width of rendered output
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
        
    # set the render type to H264, visually lossless
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'PERC_LOSSLESS'
    scene.render.ffmpeg.ffmpeg_preset = 'BEST'
    
    # Set output path and start rendering
    render_path = os.path.join(output_dir, f"{combination_index}.mp4")
    
    scene.render.filepath = render_path
    bpy.ops.render.render(animation=True)  # Use animation=True for video rendering
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--object_path",
        type=str,
        required=True,
        help="Path to the object file",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        required=True,
        help="Path to the directory where the rendered video will be saved.",
    )
    parser.add_argument(
        "--combination_file",
        type=str,
        default="combinations.json",
        help="Path to the JSON file containing camera combinations.",
    )
    parser.add_argument(
        "--background_path",
        type=str,
        default="backgrounds",
        help="Path to the directory where the background HDRs will be saved.",
    )
    parser.add_argument(
        "--combination_index",
        type=int,
        default=0,
        help="Index of the camera combination to use from the JSON file.",
    )
    parser.add_argument("--width", type=int, default=1920, help="Render output width.")
    parser.add_argument("--height", type=int, default=1080, help="Render output height.")
    argv = sys.argv[sys.argv.index("--") + 1 :]
    args = parser.parse_args(argv)

    context = bpy.context

    bpy.ops.wm.open_mainfile(filepath="scenes/video_generation_v1.blend")

    scene = context.scene
    render = scene.render

    scene.render.film_transparent = True

    os_system = platform.system()

    # if we are on mac, device type is METAL
    # if we are on windows or linux, device type is CUDA
    if os_system == "Darwin":
        bpy.context.preferences.addons[
            "cycles"
        ].preferences.compute_device_type = "METAL"
    else:
        bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA"

    # Render the images
    render_scene(
        object_file=args.object_path,
        output_dir=args.output_dir,
        context=context,
        combination_file=args.combination_file,
        combination_index=args.combination_index,
        height=args.height,
        width=args.width
    )
