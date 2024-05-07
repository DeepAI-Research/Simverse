import math
import random
from typing import Tuple
import bpy


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
    orientation = combination['orientation']

    # Rotate CameraOrientationPivotYaw by the Y
    camera_orientation_pivot_yaw = bpy.data.objects.get("CameraOrientationPivotYaw")
    random_yaw_offset = orientation['rotation_offset'][0]

    # Convert from degrees to radians. orientation['pitch'] is in degrees, but Blender uses radians
    camera_orientation_pivot_yaw.rotation_euler[2] = (orientation['yaw'] + random_yaw_offset) * math.pi / 180
    
    # Rotate CameraOrientationPivotPitch by the X
    camera_orientation_pivot_pitch = bpy.data.objects.get("CameraOrientationPivotPitch")

    # Convert orientation['pitch'] from degrees to radians, randomly add 3 to -3 degrees to the pitch
    random_pitch_offset = orientation['rotation_offset'][1]

    # Apply the pitch rotation adjustment. Negative sign used to invert the rotation for upward pitch in Blender's coordinate system.
    camera_orientation_pivot_pitch.rotation_euler[1] = (orientation['pitch'] + random_pitch_offset) * -math.pi / 180
    framing = combination['framing']
    
    # Set the root of the whole rig to the orientation position
    camera_animation_root = bpy.data.objects.get("CameraAnimationRoot")
    camera_animation_root.location = [sum(x) for x in zip(orientation['position'], orientation['position_offset'])]
        
    # Set the CameraFramingPivot X to the framing  
    camera_framing_pivot = bpy.data.objects.get("CameraFramingPivot")
    camera_framing_pivot.location = [sum(x) for x in zip(framing['position'], framing['position_offset'])]
    camera.rotation_euler = [camera.rotation_euler[i] + (framing['rotation_offset'][i]) * math.pi / 180 for i in range(3)]
    camera.data.lens = framing['fov'] + random.random() * 5 - 2.5
    set_camera_animation(combination['animation']['name'])


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
            if child.type == 'EMPTY':
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
        raise ValueError(f"Animation target object not found for animation {animation_name}")
    
    # Set the action to the camera
    action_object.animation_data.action = action
    
    # Play the action
    bpy.context.scene.frame_set(0)


def reset_cameras(scene) -> None:
    """
    Resets all camera-related objects in the Blender scene to their default positions.
    - CameraAnimationRoot - empty which some animations animate - for example orbiting
    - CameraOrientationPivotYaw - empty which sets the root rotation around the object, parented to the CameraAnimationRoot
    - CameraOrientationPivotPitch - empty which sets the pitch rotation up over the object, parented to the CameraOrientationPivotYaw
    - CameraFramingPivot - empty which sets the distance from the object, parented to the CameraOrientationPivotPitch
    - CameraAnimationPivot - empty from which the camera can animation, for example panning and zooming, parented to the CameraFramingPivot
    - Camera - the camera object itself, parented to the CameraAnimationPivot - fov etc can be set, but should be 0,0,0 rotation and position

    Args:
        scene (bpy.types.Scene): The Blender scene containing the cameras.
    
    Returns: 
        None
    """

    components = {
        "CameraAnimationRoot": (0, 0, 0),
        "CameraOrientationPivotYaw": (0, 0, 0),
        "CameraOrientationPivotPitch": (0, 0, 0),
        "CameraFramingPivot": (1, 0, 0),
        "CameraAnimationPivot": (0, 0, 0),
        "Camera": (0, 0, 0)
    }

    for component, position in components.items():
        obj = scene.objects.get(component)
        if obj is None:
            raise ValueError(f"No {component} found in the scene")
        obj.location = position
        obj.rotation_euler = (0, 0, 0)
    
    scene.camera = scene.objects.get("Camera")


def sample_point_on_sphere(radius: float) -> Tuple[float, float, float]:
    """
    Samples a point on the surface of a sphere given a radius.

    Args:
        radius (float): The radius of the sphere.

    Returns:
        Tuple[float, float, float]: The coordinates of the sampled point on the sphere.
    """

    theta = random.random() * 2 * math.pi
    phi = math.acos(2 * random.random() - 1)
    
    return (
        radius * math.sin(phi) * math.cos(theta),
        radius * math.sin(phi) * math.sin(theta),
        radius * math.cos(phi),
    )