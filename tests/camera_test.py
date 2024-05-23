import os
import sys
import math


current_dir = os.path.dirname(os.path.abspath(__file__))
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

import bpy
from simian.camera import (
    create_camera_rig,
    set_camera_settings,
    position_camera,
)
from simian.scene import initialize_scene


def test_create_camera_rig():
    """
    Test the create_camera_rig function.
    """

    EPSILON = 1e-6  # Small value to account for floating-point inaccuracies
    rig = create_camera_rig()  # call the function

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
    print("============ Test Passed: test_create_camera_rig ============")


def test_set_camera_settings():
    """
    Test the set_camera_settings function.
    """

    initialize_scene()
    create_camera_rig()

    combination = {
        "orientation": {"yaw": 327, "pitch": 14},
        "framing": {"fov": 20, "coverage_factor": 1.0},
        "animation": {
            "name": "tilt_left",
            "keyframes": [
                {
                    "CameraAnimationRoot": {"rotation": [0, 0, 45]},
                    "Camera": {"angle_offset": 5},
                },
                {"CameraAnimationRoot": {"rotation": [0, 0, 0]}},
            ],
        },
    }

    # Retrieve the camera object from the Blender scene
    camera = bpy.data.objects["Camera"].data

    # set the camera lens_unit type to FOV
    camera.lens_unit = "FOV"

    # Call the function with full data
    set_camera_settings(combination)

    # Retrieve the orientation pivot objects
    camera_orientation_pivot_yaw = bpy.data.objects["CameraOrientationPivotYaw"]
    camera_orientation_pivot_pitch = bpy.data.objects["CameraOrientationPivotPitch"]
    print("camera.angle")
    print(camera.angle)
    print('combination["framing"]["fov"]')
    print(math.radians(combination["framing"]["fov"]))
    print(
        'combination["framing"]["fov"] + combination["animation"]["keyframes"][0]["Camera"]["angle_offset"]'
    )
    print(
        math.radians(
            combination["framing"]["fov"]
            + combination["animation"]["keyframes"][0]["Camera"]["angle_offset"]
        )
    )
    fov = math.radians(
        combination["framing"]["fov"]
        + combination["animation"]["keyframes"][0]["Camera"]["angle_offset"]
    )
    # Assert the field of view is set correctly
    epsilon = 0.0001
    assert (
        camera.angle <= fov + epsilon and camera.angle >= fov - epsilon
    ), "FOV is not set correctly"

    # Convert degrees to radians for comparison
    expected_yaw_radians = math.radians(combination["orientation"]["yaw"])
    expected_pitch_radians = -math.radians(
        combination["orientation"]["pitch"]
    )  # Negative for Blender's coordinate system

    # Assert the orientation is set correctly
    assert math.isclose(
        camera_orientation_pivot_yaw.rotation_euler[2],
        expected_yaw_radians,
        abs_tol=0.001,
    ), "Yaw is not set correctly"
    assert math.isclose(
        camera_orientation_pivot_pitch.rotation_euler[1],
        expected_pitch_radians,
        abs_tol=0.001,
    ), "Pitch is not set correctly"
    print("============ Test Passed: test_set_camera_settings ============")


def test_position_camera():
    combination = {
        "framing": {"fov": 20, "coverage_factor": 1.0},
        "animation": {
            "keyframes": [
                {
                    "Camera": {
                        "position": (0, 0, 5),
                        "rotation": (0, 0, 0),
                        "angle_offset": 5,
                    }
                },
                {
                    "Camera": {
                        "position": (5, 0, 0),
                        "rotation": (0, 0, 90),
                        "angle_offset": 10,
                    }
                },
            ]
        },
    }

    # Create a dummy object to represent the focus object
    bpy.ops.mesh.primitive_cube_add(size=2)
    focus_object = bpy.context.active_object

    position_camera(combination, focus_object)

    camera = bpy.data.objects.get("Camera")
    assert camera is not None, "Camera object not found"

    # TODO: add more asserts here

    print("============ Test Passed: test_position_camera ============")


if __name__ == "__main__":
    test_create_camera_rig()
    test_set_camera_settings()
    # test_set_camera_animation()
    test_position_camera()
    print("============ ALL TESTS PASSED ============")
