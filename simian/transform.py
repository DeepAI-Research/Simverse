from math import radians, cos, sin
import numpy as np
import random
import math


# Function Definitions


def degrees_to_radians(deg):
    return radians(deg)


def compute_rotation_matrix(theta):
    return [[cos(theta), -sin(theta)], [sin(theta), cos(theta)]]


def apply_rotation(point, rotation_matrix):
    rotated_point = np.dot(rotation_matrix, np.array(point))
    # round this to integer if it is close to an integer
    rotated_point = [
        round(val) if abs(val - round(val)) < 1e-9 else val for val in rotated_point
    ]

    return rotated_point


def adjust_positions(objects, camera_yaw):
    rotation_matrix = compute_rotation_matrix(radians(camera_yaw))
    lookup_table = {
        0: (-1, 1),
        1: (0, 1),
        2: (1, 1),
        3: (-1, 0),
        4: (0, 0),
        5: (1, 0),
        6: (-1, -1),
        7: (0, -1),
        8: (1, -1),
    }

    empty_objs = []
    for obj in objects:
        grid_x, grid_y = lookup_table[obj["placement"]]
        empty_obj = obj
        empty_obj["transformed_position"] = apply_rotation(
            [grid_x, grid_y], rotation_matrix
        )
        empty_objs.append(empty_obj)
    return empty_objs


def determine_relationships(objects, camera_yaw):
    # Inverse the rotation to transform to camera's local space
    inverse_rotation_matrix = compute_rotation_matrix(radians(-camera_yaw))

    relationships = []
    for i, obj1 in enumerate(objects):
        for j, obj2 in enumerate(objects):
            if i != j:
                # Transform positions to camera's local coordinate system
                pos1 = apply_rotation(
                    obj1["transformed_position"], inverse_rotation_matrix
                )
                pos2 = apply_rotation(
                    obj2["transformed_position"], inverse_rotation_matrix
                )

                relationship = ""

                # Determining lateral relationship
                if pos2[1] > pos1[1]:
                    relationship = "to the left of"
                elif pos2[1] < pos1[1]:
                    relationship = "to the right of"

                # Determining depth relationship
                if pos2[0] > pos1[0]:
                    relationship += " and behind"
                elif pos2[0] < pos1[0]:
                    relationship += " and in front of"

                if relationship:
                    relationships.append(
                        f"{obj1['name']} is {relationship} {obj2['name']}."
                    )

    return relationships
