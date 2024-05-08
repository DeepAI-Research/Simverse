import os
import sys
from unittest.mock import patch, MagicMock
import math

current_dir = os.path.dirname(os.path.abspath(__file__))

# Append the simian directory to sys.path
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

from simian.camera import (
    set_camera_settings,
    set_camera_animation
)

current_dir = os.path.dirname(os.path.abspath(__file__))

# Append the simian directory to sys.path
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

import bpy


def test_set_camera_settings():
    # Prepare test data
    combination = {
        "orientation": {"yaw": 90, "pitch": 45, "rotation_offset": [10, 5]},
        "framing": {
            "fov": 35,
            "position": [10, 5, 2],
            "position_offset": [0.5, 0.5, 0.1],
            "rotation_offset": [1, 2, 3],
        },
    }

    # Mock bpy context and objects
    with patch.dict(
        "bpy.data.objects",
        {
            "Camera": MagicMock(),
            "CameraOrientationPivotYaw": MagicMock(),
            "CameraOrientationPivotPitch": MagicMock(),
            "CameraAnimationRoot": MagicMock(),
            "CameraFramingPivot": MagicMock(),
        },
    ):
        set_camera_settings(combination)

        # Assertions to check if the settings have been applied correctly
        assert bpy.data.objects["CameraOrientationPivotYaw"].rotation_euler[
            2
        ] == math.radians(100), "Yaw rotation not set correctly"
        assert bpy.data.objects["CameraOrientationPivotPitch"].rotation_euler[
            1
        ] == -math.radians(50), "Pitch rotation not set correctly"


def test_set_camera_animation():
    # Prepare mock NLA tracks and action
    action = MagicMock(name="Action")
    track = MagicMock(strips=[MagicMock(action=action)])
    animation_root = MagicMock(animation_data=MagicMock(nla_tracks=[track]))

    with patch.dict("bpy.data.objects", {"CameraAnimationRoot": animation_root}):
        # Test when animation is found
        set_camera_animation("TestAnimation")
        assert (
            animation_root.animation_data.action == action
        ), "Animation was not set correctly"

        # Test when animation is not found
        with patch(
            "bpy.data.objects",
            {"CameraAnimationRoot": MagicMock(animation_data=MagicMock(nla_tracks=[]))},
        ):
            try:
                set_camera_animation("MissingAnimation")
            except ValueError:
                pass

# Run tests if this file is executed as a script
if __name__ == "__main__":
    test_set_camera_settings()
    test_set_camera_animation()
    print("All tests passed.")
