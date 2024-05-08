import os
import sys
import math
from unittest.mock import patch, MagicMock

current_dir = os.path.dirname(os.path.abspath(__file__))
# Append the simian directory to sys.path
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

import bpy
from simian.camera import create_camera_rig, set_camera_settings, set_camera_animation


import math

EPSILON = 1e-6  # Small value to account for floating-point inaccuracies

def test_create_camera_rig():
    # Call the function
    rig = create_camera_rig()

    # Check if all the expected objects are created
    assert isinstance(rig["camera_animation_root"], bpy.types.Object)
    assert isinstance(rig["camera_orientation_pivot_yaw"], bpy.types.Object)
    assert isinstance(rig["camera_orientation_pivot_pitch"], bpy.types.Object)
    assert isinstance(rig["camera_framing_pivot"], bpy.types.Object)
    assert isinstance(rig["camera_animation_pivot"], bpy.types.Object)
    assert isinstance(rig["camera_object"], bpy.types.Object)
    assert isinstance(rig["camera"], bpy.types.Camera)

    # Check if the camera is set correctly
    assert bpy.context.scene.camera == rig["camera_object"]

    # Check if the camera rotation is set correctly
    camera_rotation = rig["camera_object"].delta_rotation_euler

    # Expected rotation values
    expected_x_rotation = 1.5708  # 90 degrees
    expected_y_rotation = 0.0
    expected_z_rotation = 1.5708  # 90 degrees

    # Check rotation values with epsilon error
    assert math.isclose(camera_rotation[0], expected_x_rotation, abs_tol=EPSILON)
    assert math.isclose(camera_rotation[1], expected_y_rotation, abs_tol=EPSILON)
    assert math.isclose(camera_rotation[2], expected_z_rotation, abs_tol=EPSILON)
    

def test_set_camera_settings():
    # Define the combination data with 'animation' included
    combination = {
        "orientation": {"yaw": 327, "pitch": 14},
        "framing": {"position": [2, 0, 0], "fov": 20},
        "animation": {
            "name": "tilt_left",
            "keyframes": [
                {"CameraAnimationRoot": {"rotation": [0, 0, 45]}},
                {"CameraAnimationRoot": {"rotation": [0, 0, 0]}}
            ]
        }
    }

    # Call the function with full data
    set_camera_settings(combination)

    # Retrieve the camera object from the Blender scene
    camera = bpy.data.objects['Camera'].data

    # Retrieve the orientation pivot objects
    camera_orientation_pivot_yaw = bpy.data.objects['CameraOrientationPivotYaw']
    camera_orientation_pivot_pitch = bpy.data.objects['CameraOrientationPivotPitch']

    # Assert the field of view is set correctly
    assert camera.lens == combination["framing"]["fov"], "FOV is not set correctly"

    # Convert degrees to radians for comparison
    expected_yaw_radians = math.radians(combination["orientation"]["yaw"])
    expected_pitch_radians = -math.radians(combination["orientation"]["pitch"])  # Negative for Blender's coordinate system

    # Assert the orientation is set correctly
    assert math.isclose(camera_orientation_pivot_yaw.rotation_euler[2], expected_yaw_radians, abs_tol=0.001), "Yaw is not set correctly"
    assert math.isclose(camera_orientation_pivot_pitch.rotation_euler[1], expected_pitch_radians, abs_tol=0.001), "Pitch is not set correctly"


def set_camera_animation(combination: dict, frame_distance: int = 120) -> None:
    """
    Applies the specified animation to the camera based on the keyframes from the camera_data.json file.
    """
    # Check if 'animation' key exists in the combination
    if "animation" not in combination:
        print("No animation data provided.")
        return  # Exit the function if no animation data is found

    animation = combination["animation"]
    keyframes = animation.get("keyframes", [])

    for i, keyframe in enumerate(keyframes):
        for obj_name, transforms in keyframe.items():
            obj = bpy.data.objects.get(obj_name)
            if obj is None:
                raise ValueError(f"Object {obj_name} not found in the scene")

            frame = i * frame_distance
            for transform_name, value in transforms.items():
                if transform_name == "position":
                    obj.location = value
                elif transform_name == "rotation":
                    obj.rotation_euler = [math.radians(angle) for angle in value]
                elif transform_name == "scale":
                    obj.scale = value

                obj.keyframe_insert(data_path=transform_name, frame=frame)

    bpy.context.scene.frame_set(0)


if __name__ == "__main__":
    # Correct your test or combination data
    combination = {
        # Ensure this dictionary is correctly populated
        "animation": {
            "name": "example_animation",
            "keyframes": [
                # Example keyframe data
            ]
        }
    }

    test_create_camera_rig()
    test_set_camera_settings()
    set_camera_animation(combination)
    print("All tests passed")



