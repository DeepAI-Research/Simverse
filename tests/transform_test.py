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
    # Define a set of objects with known transformed positions
    objects = [
        {"name": "obj1", "transformed_position": [0, 0]},
        {"name": "obj2", "transformed_position": [1, 1]},
        {"name": "obj3", "transformed_position": [-1, -1]}
    ]

    # Define a known camera yaw
    camera_yaw = 45

    # Determine the relationships between the objects
    relationships = determine_relationships(objects, camera_yaw)

    # Check if the relationships are correctly formed
    for relationship in relationships:
        assert " is " in relationship and " of " in relationship, "Relationship is not correctly formed"

    # Check if all objects are related to each other
    for obj1 in objects:
        for obj2 in objects:
            if obj1 != obj2:
                assert any(f"{obj1['name']} is" in relationship and obj2['name'] in relationship for relationship in relationships), f"{obj1['name']} is not related to {obj2['name']}"


if __name__ == "__main__":
    test_degrees_to_radians()
    test_compute_rotation_matrix()
    test_apply_rotation()
    test_adjust_positions()
    test_determine_relationships()
    print("============ ALL TESTS PASSED ============")
