import argparse
import sys
import json
import os
import ssl
import bpy

ssl._create_default_https_context = ssl._create_unverified_context

# Get the directory of the currently executing script
current_dir = os.path.dirname(os.path.abspath(__file__))

# if the directory is simian, remove that
if current_dir.endswith("simian"):
    current_dir = os.path.dirname(current_dir)

sys.path.append(os.path.join(current_dir))

from simian.camera import (
    create_camera_rig,
    position_camera,
    set_camera_animation,
    set_camera_settings,
)
from simian.transform import find_largest_length, place_objects_on_grid
from simian.camera import create_camera_rig, set_camera_settings
from simian.object import (
    apply_all_modifiers,
    apply_and_remove_armatures,
    get_meshes_in_hierarchy,
    join_objects_in_hierarchy,
    load_object,
    lock_all_objects,
    normalize_object_scale,
    optimize_meshes_in_hierarchy,
    set_pivot_to_bottom,
    unlock_objects,
    unparent_keep_transform,
)
from simian.background import create_photosphere, set_background
from simian.scene import apply_stage_material, create_stage, initialize_scene
import simian.vendor.objaverse


def read_combination(combination_file: str, index: int = 0) -> dict:
    """
    Reads a specified camera combination from a JSON file.

    Args:
        None

    Returns:
        None
    """
    with open(combination_file, "r") as file:
        data = json.load(file)
        # read the combinations from the JSON file and load as pandas dataframe
        combinations_data = data["combinations"]
        return combinations_data[index]


def render_scene(
    output_dir: str,
    context: bpy.types.Context,
    combination_file,
    start_frame: int = 1,
    end_frame: int = 65,
    combination_index=0,
    combination=None,
    height=1080,
    width=1920,
) -> None:
    """
    Renders a scene with specified parameters.

    Args:
        output_dir (str): Path to the directory where the rendered video will be saved.
        context (bpy.types.Context): Blender context.
        combination_file (str): Path to the JSON file containing camera combinations.
        start_frame (int): Start frame of the animation. Defaults to 1.
        end_frame (int): End frame of the animation. Defaults to 65.
        combination_index (int): Index of the camera combination to use from the JSON file. Defaults to 0.
        height (int): Render output height. Defaults to 1080.
        width (int): Render output width. Defaults to 1920.

    Returns:
        None
    """

    print(f"Rendering scene with combination {combination_index}")

    os.makedirs(output_dir, exist_ok=True)

    initialize_scene()
    create_camera_rig()

    scene = context.scene
    context.scene.frame_start = start_frame
    context.scene.frame_end = end_frame

    # Lock and hide all scene objects before doing any object operations
    initial_objects = lock_all_objects()

    if combination is not None:
        combination = json.loads(combination)
    else:
        combination = read_combination(combination_file, combination_index)
    all_objects = []

    focus_object = None

    for object_data in combination["objects"]:
        object_file = simian.vendor.objaverse.load_objects([object_data["uid"]])[
            object_data["uid"]
        ]

        load_object(object_file)
        obj = [obj for obj in context.view_layer.objects.selected][0]

        apply_and_remove_armatures()
        apply_all_modifiers(obj)
        join_objects_in_hierarchy(obj)
        optimize_meshes_in_hierarchy(obj)

        meshes = get_meshes_in_hierarchy(obj)
        obj = meshes[0]

        if focus_object is None:
            focus_object = obj

        unparent_keep_transform(obj)
        set_pivot_to_bottom(obj)

        obj.scale = [object_data["scale"]["factor"] for _ in range(3)]
        normalize_object_scale(obj)

        obj.name = object_data["uid"]  # Set the Blender object's name to the UID

        all_objects.append({obj: object_data})

    largest_length = find_largest_length(all_objects)
    place_objects_on_grid(all_objects, largest_length)

    # Unlock and unhide the initial objects
    unlock_objects(initial_objects)

    set_camera_settings(combination)
    set_camera_animation(combination, end_frame)
    set_background(args.hdri_path, combination)

    create_photosphere(args.hdri_path, combination).scale = (10, 10, 10)

    stage = create_stage(combination)
    apply_stage_material(stage, combination)

    # Set height and width of rendered output
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100

    # Set the render type to H264, visually lossless
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "PERC_LOSSLESS"
    scene.render.ffmpeg.ffmpeg_preset = "BEST"

    position_camera(combination, focus_object)

    # Set output path and start rendering
    render_path = os.path.join(output_dir, f"{combination_index}.mp4")

    scene.render.filepath = render_path
    bpy.ops.render.render(animation=True)
    bpy.ops.wm.save_as_mainfile(
        filepath=os.path.join(output_dir, f"{combination_index}.blend")
    )
    print(f"Rendered video saved to {render_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        type=str,
        default="renders",
        required=False,
        help="Path to the directory where the rendered video will be saved.",
    )
    parser.add_argument(
        "--combination_file",
        type=str,
        default="combinations.json",
        help="Path to the JSON file containing camera combinations.",
    )
    parser.add_argument(
        "--hdri_path",
        type=str,
        default="backgrounds",
        help="Path to the directory where the background HDRs will be saved.",
    )
    parser.add_argument(
        "--combination_index",
        type=int,
        default=0,
        help="Index of the camera combination to use from the JSON file.",
        required=False,
    )
    parser.add_argument(
        "--start_frame",
        type=int,
        default=1,
        help="Start frame of the animation.",
        required=False,
    )
    parser.add_argument(
        "--end_frame",
        type=int,
        default=65,
        help="End frame of the animation.",
        required=False,
    )
    parser.add_argument(
        "--width", type=int, default=1920, help="Render output width.", required=False
    )
    parser.add_argument(
        "--height", type=int, default=1080, help="Render output height.", required=False
    )
    parser.add_argument(
        "--combination", type=str, default=None, help="Combination dictionary."
    )

    if "--" in sys.argv:
        argv = sys.argv[sys.argv.index("--") + 1 :]
    else:
        argv = []

    args = parser.parse_args(argv)

    context = bpy.context
    scene = context.scene
    render = scene.render

    if args.combination is not None:
        combination = json.loads(args.combination)
    else:
        combination = read_combination(args.combination_file, args.combination_index)

    # get the object uid from the 'object' column, which is a dictionary
    objects_column = combination["objects"]

    for object in objects_column:
        uid = object["uid"]

        downloaded = simian.vendor.objaverse.load_objects([uid])

    # Render the images
    render_scene(
        start_frame=args.start_frame,
        end_frame=args.end_frame,
        output_dir=args.output_dir,
        context=context,
        combination_file=args.combination_file,
        combination_index=args.combination_index,
        combination=args.combination,
        height=args.height,
        width=args.width,
    )
