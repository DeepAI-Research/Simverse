import math
import random
from typing import Tuple

import bpy

def set_camera_settings(camera, combination):
    """Applies camera settings from a combination."""
    # Assuming combination has keys like 'fov', 'animation'
    print(combination)
    orientation = combination['orientation']
    framing = combination['framing']
    print('framing', framing)
    camera.data.lens = framing['fov']
    print("combination['animation']")
    print(combination['animation'])
    set_camera_animation(combination['animation']['name'])


def set_camera_animation(animation_name: str) -> None:
    """Play the NLA track with the given animation name on the camera."""

    # find the CameraAnimationRoot object
    camera_animation_root = bpy.data.objects.get("CameraAnimationRoot")
    
    action = None
    
    print('camera')
    print(camera_animation_root)
    
    # find the NLA track with the given animation name on camera_animation_root
    for track in camera_animation_root.animation_data.nla_tracks:
        if track.name == animation_name:
            action = track.strips[0].action
            return
    
    if action is None:
        raise ValueError(f"Animation {animation_name} not found on camera")
    
    # set the action to the camera
    camera_animation_root.animation_data.action = action
    
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