from math import cos, radians, sin
import math
import random
import numpy as np
import random
import copy


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


def determine_relationships(objects, object_data):
    """
    Determine the spatial relationships between objects based on their positions.

    Args:
        - objects (list): List of objects with their transformed positions.
        - object_data (dict): Dictionary containing directional relationship phrases.

    Returns:
        - list: List of spatial relationships between objects.
    """
    # Retrieve directional relationship phrases from object data
    to_the_left = object_data["relationships"]["to_the_left"]
    to_the_right = object_data["relationships"]["to_the_right"]
    in_front_of = object_data["relationships"]["in_front_of"]
    behind = object_data["relationships"]["behind"]

    relationships = []

    # Compare each pair of objects to determine their spatial relationship
    for i, obj1 in enumerate(objects):
        for j, obj2 in enumerate(objects):
            if i != j:
                # Get transformed positions
                pos1 = obj1["transformed_position"]
                pos2 = obj2["transformed_position"]

                relationship = ""

                # Determine the lateral relationship based on y-coordinates
                if pos2[1] > pos1[1]:  # obj2 is to the left of obj1
                    relationship = random.choice(to_the_left)
                elif pos2[1] < pos1[1]:  # obj2 is to the right of obj1
                    relationship = random.choice(to_the_right)

                # Determine the depth relationship based on x-coordinates
                if (
                    pos2[0] > pos1[0]
                ):  # obj2 is in front of obj1 (negative x is closer to the camera)
                    relationship += (
                        (" and " + random.choice(behind))
                        if relationship
                        else random.choice(behind)
                    )
                elif pos2[0] < pos1[0]:  # obj2 is behind obj1
                    relationship += (
                        (" and " + random.choice(in_front_of))
                        if relationship
                        else random.choice(in_front_of)
                    )

                # If there is a significant relationship, add it to the list
                if relationship != "":
                    relationships.append(
                        f"{obj1['name']} {relationship} {obj2['name']}."
                    )

    return relationships
