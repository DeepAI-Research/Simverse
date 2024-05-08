import math
import random
from typing import Tuple
import bpy


def create_camera_rig() -> bpy.types.Object:
    """
    Creates a camera rig consisting of multiple objects in Blender.

    Returns:
        dict: A dictionary containing the created objects:
            - camera_animation_root: The root object of the camera animation hierarchy.
            - camera_orientation_pivot_yaw: The yaw pivot object for camera orientation.
            - camera_orientation_pivot_pitch: The pitch pivot object for camera orientation.
            - camera_framing_pivot: The pivot object for camera framing.
            - camera_animation_pivot: The pivot object for camera animation.
            - camera_object: The camera object.
            - camera: The camera data.
    """
    camera_animation_root = bpy.data.objects.new("CameraAnimationRoot", None)

    camera_orientation_pivot_yaw = bpy.data.objects.new(
        "CameraOrientationPivotYaw", None
    )
    camera_orientation_pivot_yaw.parent = camera_animation_root

    camera_orientation_pivot_pitch = bpy.data.objects.new(
        "CameraOrientationPivotPitch", None
    )
    camera_orientation_pivot_pitch.parent = camera_orientation_pivot_yaw

    camera_framing_pivot = bpy.data.objects.new("CameraFramingPivot", None)
    camera_framing_pivot.parent = camera_orientation_pivot_pitch

    camera_animation_pivot = bpy.data.objects.new("CameraAnimationPivot", None)

    camera = bpy.data.cameras.new("Camera")
    camera_object = bpy.data.objects.new("Camera", camera)
    camera_object.parent = camera_animation_pivot

    bpy.context.scene.camera = camera_object
    bpy.context.scene.collection.objects.link(camera_animation_root)

    return {
        "camera_animation_root": camera_animation_root,
        "camera_orientation_pivot_yaw": camera_orientation_pivot_yaw,
        "camera_orientation_pivot_pitch": camera_orientation_pivot_pitch,
        "camera_framing_pivot": camera_framing_pivot,
        "camera_animation_pivot": camera_animation_pivot,
        "camera_object": camera_object,
        "camera": camera,
    }


def set_camera_settings(combination: dict) -> None:
    """
    Applies camera settings from a combination to the Blender scene.

    This function updates various camera settings including orientation, pivot adjustments, and
    framing based on the provided combination dictionary.

    Args:
        combination (dict): A dictionary containing camera settings including 'fov', 'animation',
                            and orientation details.
    Returns:
        None
    """

    # Assuming combination has keys like 'fov', 'animation'
    camera = bpy.context.scene.objects["Camera"]
    orientation = combination["orientation"]
    
    orientation_data = combination["orientation"]

    # Randomly generate pitch and yaw angles
    random_pitch = random.uniform(orientation_data["pitch_min"], orientation_data["pitch_max"])
    random_yaw = random.uniform(orientation_data["yaw_min"], orientation_data["yaw_max"])

    orientation = {
        "pitch": random_pitch,
        "yaw": random_yaw
    }

    # Rotate CameraOrientationPivotYaw by the Y
    camera_orientation_pivot_yaw = bpy.data.objects.get("CameraOrientationPivotYaw")

    # Convert from degrees to radians. orientation['pitch'] is in degrees, but Blender uses radians
    camera_orientation_pivot_yaw.rotation_euler[2] = (
        orientation["yaw"]* math.pi / 180
    )

    # Rotate CameraOrientationPivotPitch by the X
    camera_orientation_pivot_pitch = bpy.data.objects.get("CameraOrientationPivotPitch")

    # Apply the pitch rotation adjustment. Negative sign used to invert the rotation for upward pitch in Blender's coordinate system.
    camera_orientation_pivot_pitch.rotation_euler[1] = (
        orientation["pitch"] * -math.pi / 180
    )
    framing = combination["framing"]

    # Set the root of the whole rig to the orientation position
    camera_animation_root = bpy.data.objects.get("CameraAnimationRoot")
    
    # TODO: Get the center of the bounding box of the focus object and set the camera to that position
    camera_animation_root.location = [0, 0, 0.5]

    # Set the CameraFramingPivot X to the framing
    camera_framing_pivot = bpy.data.objects.get("CameraFramingPivot")
    camera_framing_pivot.location = framing["position"]
    set_camera_animation(combination["animation"]["name"])


def set_camera_animation(animation_name: str) -> None:
    """
    Plays the specified NLA track animation on the camera.

    This function finds and applies an NLA track with the given animation name to the camera object
    in the Blender scene.

    Args:
        animation_name (str): The name of the animation to play on the camera.

    Raises:
        ValueError: If the animation or the animation target object is not found.

    Returns:
        None
    """

    # Get CameraAnimationRoot object
    camera_animation_root = bpy.data.objects.get("CameraAnimationRoot")

    action = None

    # Get camera_animation_root and all empty children and store in an array
    empties = []

    # Add obj to empties
    empties.append(camera_animation_root)

    def recurse_children(obj):
        for child in obj.children:
            if child.type == "EMPTY":
                empties.append(child)
                recurse_children(child)

    recurse_children(camera_animation_root)

    action_object = None

    for empty in empties:
        # Find the NLA track with the given animation name on camera_animation_root
        if empty.animation_data is None or empty.animation_data.nla_tracks is None:
            continue
        for track in empty.animation_data.nla_tracks:
            if track.name == animation_name:
                action_object = empty
                action = track.strips[0].action
                break

    if action is None:
        raise ValueError(f"Animation {animation_name} not found on camera")

    if action_object is None:
        raise ValueError(
            f"Animation target object not found for animation {animation_name}"
        )

    # Set the action to the camera
    action_object.animation_data.action = action

    # Play the action
    bpy.context.scene.frame_set(0)