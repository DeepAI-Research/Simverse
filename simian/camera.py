import math
import random
from typing import Tuple

import bpy

def set_camera_settings(combination):
    """Applies camera settings from a combination."""
    # Assuming combination has keys like 'fov', 'animation'
    camera = bpy.context.scene.objects["Camera"]
    orientation = combination['orientation']
    # rotate CameraOrientationPivotYaw by the Y
    camera_orientation_pivot_yaw = bpy.data.objects.get("CameraOrientationPivotYaw")
    random_yaw_offset = orientation['rotation_offset'][0]
    # orientation['pitch'] is in degrees, but Blender uses radians
    camera_orientation_pivot_yaw.rotation_euler[2] = (orientation['yaw'] + random_yaw_offset) * math.pi / 180
    
    # rotate CameraOrientationPivotPitch by the X
    camera_orientation_pivot_pitch = bpy.data.objects.get("CameraOrientationPivotPitch")
    # orientation['pitch'] is in degrees, but Blender uses radians
    # randomly add 3 to -3 degrees to the pitch
    random_pitch_offset = orientation['rotation_offset'][1]
    camera_orientation_pivot_pitch.rotation_euler[1] = (orientation['pitch'] + random_pitch_offset) * math.pi / -180 # negative so that 45 degrees is up
    framing = combination['framing']
    
    # set the root of the whole rig to the orientation position
    camera_animation_root = bpy.data.objects.get("CameraAnimationRoot")
    
    camera_animation_root.location = [sum(x) for x in zip(orientation['position'], orientation['position_offset'])]
        
    # set the CameraFramingPivot X to the framing  
    camera_framing_pivot = bpy.data.objects.get("CameraFramingPivot")
    
    camera_framing_pivot.location = [sum(x) for x in zip(framing['position'], framing['position_offset'])]
    camera.rotation_euler = [camera.rotation_euler[i] + (framing['rotation_offset'][i]) * math.pi / 180 for i in range(3)]

    camera.data.lens = framing['fov'] + random.random() * 5 - 2.5
    set_camera_animation(combination['animation']['name'])


def set_camera_animation(animation_name: str) -> None:
    """Play the NLA track with the given animation name on the camera."""

    # find the CameraAnimationRoot object
    camera_animation_root = bpy.data.objects.get("CameraAnimationRoot")
    
    action = None
    
    # get camera_animation_root and all empty children and store inan array
    empties = []
    # add obj to empties
    empties.append(camera_animation_root)
    def recurse_children(obj):
        for child in obj.children:
            if child.type == 'EMPTY':
                empties.append(child)
                recurse_children(child)
    recurse_children(camera_animation_root)
        
    action_object = None
        
    for empty in empties:
        # find the NLA track with the given animation name on camera_animation_root
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
    
    # set the action to the camera
    action_object.animation_data.action = action
    
    # play the action
    bpy.context.scene.frame_set(0)


def reset_cameras(scene) -> None:
    """Resets the cameras in the scene to a single default camera."""
    # CameraAnimationRoot - empty which some animations animate - for example orbiting
    # CameraOrientationPivotYaw - empty which sets the root rotation around the object, parented to the CameraAnimationRoot
    # CameraOrientationPivotPitch - empty which sets the pitch rotation up over the object, parented to the CameraOrientationPivotYaw
    # CameraFramingPivot - empty which sets the distance from the object, parented to the CameraOrientationPivotPitch
    # CameraAnimationPivot - empty from which the camera can animation, for example panning and zooming, parented to the CameraFramingPivot
    # Camera - the camera object itself, parented to the CameraAnimationPivot - fov etc can be set, but should be 0,0,0 rotation and position
    camera_animation_root = scene.objects.get("CameraAnimationRoot")
    if camera_animation_root is None:
        raise ValueError("No camera animation root found in the scene")
    
    camera_orientation_pivot_yaw = scene.objects.get("CameraOrientationPivotYaw")
    if camera_orientation_pivot_yaw is None:
        raise ValueError("No camera orientation pivot yaw found in the scene")
    
    camera_orientation_pivot_pitch = scene.objects.get("CameraOrientationPivotPitch")
    if camera_orientation_pivot_pitch is None:
        raise ValueError("No camera orientation pivot pitch found in the scene")
    
    camera_framing_pivot = scene.objects.get("CameraFramingPivot")
    if camera_framing_pivot is None:
        raise ValueError("No camera framing pivot found in the scene")
    
    camera_animation_pivot = scene.objects.get("CameraAnimationPivot")
    if camera_animation_pivot is None:
        raise ValueError("No camera animation pivot found in the scene")
    
    camera = scene.objects.get("Camera")
    if camera is None:
        raise ValueError("No camera found in the scene")
    
    # first, set the position and rotation of CameraAnimationRoot to 0,0,0
    camera_animation_root.location = (0, 0, 0)
    camera_animation_root.rotation_euler = (0, 0, 0)
    
    # then, set the position and rotation of CameraOrientationPivotYaw to 0,0,0
    camera_orientation_pivot_yaw.location = (0, 0, 0)
    camera_orientation_pivot_yaw.rotation_euler = (0, 0, 0)
    
    # then, set the position and rotation of CameraOrientationPivotPitch to 0,0,0
    camera_orientation_pivot_pitch.location = (0, 0, 0)
    camera_orientation_pivot_pitch.rotation_euler = (0, 0, 0)
    
    # then, set the position and rotation of CameraFramingPivot to 0,0,0
    camera_framing_pivot.location = (1, 0, 0)
    camera_framing_pivot.rotation_euler = (0, 0, 0)
    
    # then, set the position and rotation of CameraAnimationPivot to 0,0,0
    camera_animation_pivot.location = (0, 0, 0)
    camera_animation_pivot.rotation_euler = (0, 0, 0)
    
    # then, set the position and rotation of Camera to 0,0,0
    camera.location = (0, 0, 0)
    camera.rotation_euler = (0, 0, 0)
    
    # finally, set the camera to be the active camera
    scene.camera = camera


def sample_point_on_sphere(radius: float) -> Tuple[float, float, float]:
    """Samples a point on a sphere with the given radius.

    Args:
        radius (float): Radius of the sphere.

    Returns:
        Tuple[float, float, float]: A point on the sphere.
    """
    theta = random.random() * 2 * math.pi
    phi = math.acos(2 * random.random() - 1)
    return (
        radius * math.sin(phi) * math.cos(theta),
        radius * math.sin(phi) * math.sin(theta),
        radius * math.cos(phi),
    )