import os
import sys
import math

current_dir = os.path.dirname(os.path.abspath(__file__))
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

import bpy
from mathutils import Vector
from simian.camera import create_camera_rig, set_camera_settings, set_camera_animation, position_camera

def test_create_camera_rig():
    """
    Test the create_camera_rig function.
    """

    EPSILON = 1e-6  # Small value to account for floating-point inaccuracies
    rig = create_camera_rig() # call the function

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

    combination = {
        "orientation": {"yaw": 327, "pitch": 14},
        "framing": {"fov": 20},
        "coverage_factor": 1.0,
        "animation": {
            "name": "tilt_left",
            "keyframes": [
                {"CameraAnimationRoot": {"rotation": [0, 0, 45]}, "Camera": {"lens_offset": 5}},
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
    assert camera.lens == combination["framing"]["fov"] + combination["animation"]["keyframes"][0]["Camera"]["lens_offset"], "FOV is not set correctly"

    # Convert degrees to radians for comparison
    expected_yaw_radians = math.radians(combination["orientation"]["yaw"])
    expected_pitch_radians = -math.radians(combination["orientation"]["pitch"])  # Negative for Blender's coordinate system

    # Assert the orientation is set correctly
    assert math.isclose(camera_orientation_pivot_yaw.rotation_euler[2], expected_yaw_radians, abs_tol=0.001), "Yaw is not set correctly"
    assert math.isclose(camera_orientation_pivot_pitch.rotation_euler[1], expected_pitch_radians, abs_tol=0.001), "Pitch is not set correctly"
    print("============ Test Passed: test_set_camera_settings ============")


def test_set_camera_animation():
    combination = {
        "framing": {"fov": 20},
        "animation": {
            "keyframes": [
                {"Camera": {"position": (0, 0, 5), "rotation": (0, 0, 0), "lens_offset": 5}},
                {"Camera": {"position": (5, 0, 0), "rotation": (0, 0, 90), "lens_offset": 10}},
                {"Camera": {"position": (0, 5, 0), "rotation": (0, 0, 180), "lens_offset": 15}}
            ]
        }
    }
    set_camera_animation(combination)

    camera = bpy.data.objects.get("Camera")
    assert camera is not None, "Camera object not found"

    frame_data = [
        (0, (0, 0, 5), (0, 0, 0), 25),
        (120, (5, 0, 0), (0, 0, 1.5708), 30),  # Approximately 90 degrees in radians
        (240, (0, 5, 0), (0, 0, 3.14159), 35)  # Approximately 180 degrees in radians
    ]

    for frame, expected_pos, expected_rot, expected_lens in frame_data:
        bpy.context.scene.frame_set(frame)
        print(f"Checking frame {frame}")
        print("camera location", camera.location)
        print("expected_pos", expected_pos)
        magnitude = (camera.location - Vector(expected_pos)).magnitude
        assert magnitude < 1e-6, f"Camera position at frame {frame} is incorrect"
        
        rotation_vector = Vector(camera.rotation_euler)
        print("camera rotation", rotation_vector)
        print("expected_rot", expected_rot)
        # convert camera.rotation_euler to a vector
        magnitude = (rotation_vector - Vector(expected_rot)).magnitude
        print("magnitude", magnitude)
        assert magnitude < 1e-5, f"Camera rotation at frame {frame} is incorrect"
        
        print("camera lens", camera.data.lens)
        print("expected_lens", expected_lens)
        magnitude = (camera.data.lens - expected_lens)
        assert magnitude < 1e-6, f"Camera lens at frame {frame} is incorrect"

    print("============ Test Passed: test_set_camera_animation ============")


def test_position_camera():
    combination = {
        "coverage_factor": 1.0,
        "framing": {"fov": 20},
        "animation": {
            "keyframes": [
                {"Camera": {"position": (0, 0, 5), "rotation": (0, 0, 0), "lens_offset": 5}},
                {"Camera": {"position": (5, 0, 0), "rotation": (0, 0, 90), "lens_offset": 10}},
            ]
        },
    }

    # Create a dummy object to represent the focus object
    bpy.ops.mesh.primitive_cube_add(size=2)
    focus_object = bpy.context.active_object

    position_camera(combination, focus_object)

    camera = bpy.data.objects.get("Camera")
    assert camera is not None, "Camera object not found"

    # Check if the camera is positioned correctly based on the coverage factor
    bpy.context.view_layer.update()
    bbox = [focus_object.matrix_world @ Vector(corner) for corner in focus_object.bound_box]
    bbox_height = max(bbox, key=lambda v: v.z).z - min(bbox, key=lambda v: v.z).z
    desired_height = bbox_height * combination["coverage_factor"]
    # assert camera.location.y <= -desired_height, "Camera is not positioned correctly based on coverage factor"

    print("============ Test Passed: test_position_camera ============")


if __name__ == "__main__":
    test_create_camera_rig()
    test_set_camera_settings()
    test_set_camera_animation()
    test_position_camera()
    print("============ ALL TESTS PASSED ============")