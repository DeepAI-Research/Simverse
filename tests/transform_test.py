import math
import os
import sys
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
combiner_path = os.path.join(current_dir, "../")
sys.path.append(combiner_path)

from simian.transform import (
    degrees_to_radians,
    compute_rotation_matrix,
    apply_rotation,
    adjust_positions,
    determine_relationships,
)


def test_degrees_to_radians():
    epsilon = 1e-9
    assert abs(degrees_to_radians(180) - math.pi) < epsilon


def test_compute_rotation_matrix():
    epsilon = 1e-9
    theta = math.pi / 4  # 45 degrees in radians
    expected_matrix = [
        [math.sqrt(2) / 2, -math.sqrt(2) / 2],
        [math.sqrt(2) / 2, math.sqrt(2) / 2],
    ]
    result_matrix = compute_rotation_matrix(theta)
    for i in range(2):
        for j in range(2):
            assert abs(result_matrix[i][j] - expected_matrix[i][j]) < epsilon


def test_apply_rotation():
    epsilon = 1e-9
    point = [1, 0]
    rotation_matrix = compute_rotation_matrix(math.pi / 2)  # 90 degrees rotation
    expected_point = [0, 1]
    result_point = apply_rotation(point, rotation_matrix)
    for i in range(2):
        assert abs(result_point[i] - expected_point[i]) < epsilon


def test_adjust_positions():
    objects = [{"placement": 0}, {"placement": 1}]
    camera_yaw = 90
    adjusted_objects = adjust_positions(objects, camera_yaw)
    for obj in adjusted_objects:
        assert "transformed_position" in obj


def test_determine_relationships():
    def compute_rotation_matrix(theta):
        return [[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]

    def apply_rotation(point, rotation_matrix):
        return np.dot(rotation_matrix, np.array(point)).tolist()

    # Test case 1: Objects in front-behind relationship
    objects = [
        {"name": "obj1", "transformed_position": [0, 0]},
        {"name": "obj2", "transformed_position": [1, 0]},
    ]
    object_data = {
        "relationships": {
            "to_the_left": ["is to the left of"],
            "to_the_right": ["is to the right of"],
            "in_front_of": ["is in front of"],
            "behind": ["is behind"],
        }
    }
    camera_yaw = 0
    relationships = determine_relationships(objects, camera_yaw)
    print(relationships)
    assert len(relationships) == 2
    assert "obj2 is in front of obj1." in relationships
    assert "obj1 is behind obj2." in relationships

    # Test case 2: Objects in left-right relationship
    objects = [
        {"name": "obj1", "transformed_position": [0, 0]},
        {"name": "obj2", "transformed_position": [0, 1]},
    ]
    object_data = {
        "relationships": {
            "to_the_left": ["is to the left of"],
            "to_the_right": ["is to the right of"],
            "in_front_of": ["is in front of"],
            "behind": ["is behind"],
        }
    }
    camera_yaw = 0
    relationships = determine_relationships(objects, camera_yaw)
    print(relationships)
    assert len(relationships) == 2
    assert "obj2 is to the left of obj1." in relationships
    assert "obj1 is to the right of obj2." in relationships

    # Test case 3: Objects in front-behind relationship with camera yaw
    objects = [
        {"name": "obj1", "transformed_position": [0, 0]},
        {"name": "obj2", "transformed_position": [1, 0]},
    ]
    object_data = {
        "relationships": {
            "to_the_left": ["is to the left of"],
            "to_the_right": ["is to the right of"],
            "in_front_of": ["is in front of"],
            "behind": ["is behind"],
        }
    }
    camera_yaw = 90
    relationships = determine_relationships(objects, camera_yaw)
    print(relationships)
    assert len(relationships) == 2
    assert "obj1 is to the left of obj2." in relationships
    assert "obj2 is to the right of obj1." in relationships

    # Test case 4: Objects in left-right relationship with camera yaw
    objects = [
        {"name": "obj1", "transformed_position": [0, 0]},
        {"name": "obj2", "transformed_position": [0, 1]},
    ]
    object_data = {
        "relationships": {
            "to_the_left": ["is to the left of"],
            "to_the_right": ["is to the right of"],
            "in_front_of": ["is in front of"],
            "behind": ["is behind"],
        }
    }
    camera_yaw = 90
    relationships = determine_relationships(objects, camera_yaw)
    print(relationships)
    assert len(relationships) == 2
    assert "obj2 is behind obj1." in relationships
    assert "obj1 is in front of obj2." in relationships


if __name__ == "__main__":
    test_degrees_to_radians()
    test_compute_rotation_matrix()
    test_apply_rotation()
    test_adjust_positions()
    test_determine_relationships()
    print("============ ALL TESTS PASSED ============")
