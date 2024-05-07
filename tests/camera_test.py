import os
import sys
import pytest
from unittest.mock import patch, MagicMock
import math
from simian.camera import set_camera_settings, set_camera_animation, reset_cameras, sample_point_on_sphere

current_dir = os.path.dirname(os.path.abspath(__file__))

# Append the simian directory to sys.path
simian_path = os.path.join(current_dir, "../")
sys.path.append(simian_path)

import bpy


def test_set_camera_settings():
    # Prepare test data
    combination = {
        'orientation': {'yaw': 90, 'pitch': 45, 'rotation_offset': [10, 5]},
        'framing': {'fov': 35, 'position': [10, 5, 2], 'position_offset': [0.5, 0.5, 0.1], 'rotation_offset': [1, 2, 3]}
    }

    # Mock bpy context and objects
    with patch.dict('bpy.data.objects', {'Camera': MagicMock(), 'CameraOrientationPivotYaw': MagicMock(), 'CameraOrientationPivotPitch': MagicMock(), 'CameraAnimationRoot': MagicMock(), 'CameraFramingPivot': MagicMock()}):
        set_camera_settings(combination)
        
        # Assertions to check if the settings have been applied correctly
        assert bpy.data.objects['CameraOrientationPivotYaw'].rotation_euler[2] == math.radians(100), "Yaw rotation not set correctly"
        assert bpy.data.objects['CameraOrientationPivotPitch'].rotation_euler[1] == -math.radians(50), "Pitch rotation not set correctly"


def test_set_camera_animation():
    # Prepare mock NLA tracks and action
    action = MagicMock(name='Action')
    track = MagicMock(strips=[MagicMock(action=action)])
    animation_root = MagicMock(animation_data=MagicMock(nla_tracks=[track]))
    
    with patch.dict('bpy.data.objects', {'CameraAnimationRoot': animation_root}):
        # Test when animation is found
        set_camera_animation('TestAnimation')
        assert animation_root.animation_data.action == action, "Animation was not set correctly"

        # Test when animation is not found
        with patch('bpy.data.objects', {'CameraAnimationRoot': MagicMock(animation_data=MagicMock(nla_tracks=[]))}), \
             pytest.raises(ValueError):
            set_camera_animation('MissingAnimation')


def test_reset_cameras():
    # Setup scene mock
    scene = MagicMock()
    scene.objects = {'Camera': MagicMock(), 'CameraAnimationRoot': MagicMock(), 'CameraOrientationPivotYaw': MagicMock(), 'CameraOrientationPivotPitch': MagicMock(), 'CameraFramingPivot': MagicMock(), 'CameraAnimationPivot': MagicMock()}
    with patch.object(bpy, 'context', MagicMock(scene=scene)):
        reset_cameras(scene)
        # Assertions to check if all components were reset
        for key in scene.objects:
            obj = scene.objects[key]
            assert obj.location == (0, 0, 0), f"{key} location not reset"
            assert obj.rotation_euler == (0, 0, 0), f"{key} rotation not reset"


def test_sample_point_on_sphere():
    radius = 5
    point = sample_point_on_sphere(radius)
    # Check if the point is on the surface of the sphere
    assert math.isclose(math.sqrt(point[0]**2 + point[1]**2 + point[2]**2), radius, abs_tol=1e-6), "Point is not on the surface of the sphere"


# Run tests if this file is executed as a script
if __name__ == "__main__":
    pytest.main()
