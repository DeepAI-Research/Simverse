from math import radians, cos, sin
from typing import Dict, List, Union
import numpy as np

import bpy
from mathutils import Vector


def degrees_to_radians(deg: float) -> float:
    """Convert degrees to radians.

    Args:
        deg (float): Angle in degrees.

    Returns:
        float: Angle in radians.
    """
    return radians(deg)


def compute_rotation_matrix(theta: float) -> List[List[float]]:
    """Compute the 2D rotation matrix for a given angle.

    Args:
        theta (float): Angle in radians.

    Returns:
        List[List[float]]: 2D rotation matrix.
    """
    return [[cos(theta), -sin(theta)], [sin(theta), cos(theta)]]


def apply_rotation(
    point: List[float], rotation_matrix: List[List[float]]
) -> List[Union[int, float]]:
    """Apply rotation matrix to a point and round to integer if close.

    Args:
        point (List[float]): 2D point as [x, y].
        rotation_matrix (List[List[float]]): 2D rotation matrix.

    Returns:
        List[Union[int, float]]: Rotated point with rounded coordinates.
    """
    rotated_point = np.dot(rotation_matrix, np.array(point))
    return [
        round(val) if abs(val - round(val)) < 1e-9 else val for val in rotated_point
    ]


def adjust_positions(objects: List[Dict], camera_yaw: float) -> List[Dict]:
    """Adjust the positions of objects based on the camera yaw.

    Args:
        objects (List[Dict]): List of object dictionaries.
        camera_yaw (float): Camera yaw angle in degrees.

    Returns:
        List[Dict]: List of object dictionaries with adjusted positions.
    """
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
        empty_obj = obj.copy()
        empty_obj["transformed_position"] = apply_rotation(
            [grid_x, grid_y], rotation_matrix
        )
        empty_objs.append(empty_obj)
    return empty_objs


def determine_relationships(objects: List[Dict], camera_yaw: float) -> List[str]:
    """Determine the spatial relationships between objects based on camera yaw.

    Args:
        objects (List[Dict]): List of object dictionaries.
        camera_yaw (float): Camera yaw angle in degrees.

    Returns:
        List[str]: List of relationship strings.
    """
    inverse_rotation_matrix = compute_rotation_matrix(radians(-camera_yaw))

    relationships = []
    for i, obj1 in enumerate(objects):
        for j, obj2 in enumerate(objects):
            if i != j:
                pos1 = apply_rotation(
                    obj1["transformed_position"], inverse_rotation_matrix
                )
                pos2 = apply_rotation(
                    obj2["transformed_position"], inverse_rotation_matrix
                )

                relationship = ""

                if pos2[1] > pos1[1]:
                    relationship = "to the left of"
                elif pos2[1] < pos1[1]:
                    relationship = "to the right of"

                if pos2[0] > pos1[0]:
                    relationship += " and behind"
                elif pos2[0] < pos1[0]:
                    relationship += " and in front of"

                if relationship:
                    relationships.append(
                        f"{obj1['name']} is {relationship} {obj2['name']}."
                    )

    return relationships


def find_largest_length(objects: List[Dict[bpy.types.Object, Dict]]) -> float:
    """Find the largest dimension among the objects' bounding boxes.

    Args:
        objects (List[Dict[bpy.types.Object, Dict]]): List of object dictionaries.

    Returns:
        float: Largest dimension.
    """
    largest_dimension = 0
    for obj_dict in objects:
        obj = list(obj_dict.keys())[0]
        bpy.context.view_layer.update()
        bbox_corners = obj.bound_box
        width = (
            max(bbox_corners, key=lambda v: v[0])[0]
            - min(bbox_corners, key=lambda v: v[0])[0]
        )
        height = (
            max(bbox_corners, key=lambda v: v[1])[1]
            - min(bbox_corners, key=lambda v: v[1])[1]
        )
        current_max = max(width, height)
        largest_dimension = max(largest_dimension, current_max)

    print("THIS IS THE LARGEST DIMENSION: ", largest_dimension)
    return largest_dimension


def get_world_bounding_box_xy(obj: bpy.types.Object) -> List[Vector]:
    """Get the 2D bounding box corners of an object in world space.

    Args:
        obj (bpy.types.Object): Blender object.

    Returns:
        List[Vector]: List of 2D bounding box corners in world space.
    """
    world_bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_x = min(corner.x for corner in world_bbox)
    max_x = max(corner.x for corner in world_bbox)
    min_y = min(corner.y for corner in world_bbox)
    max_y = max(corner.y for corner in world_bbox)
    corners_xy = [
        Vector((min_x, min_y, 0)),
        Vector((max_x, min_y, 0)),
        Vector((min_x, max_y, 0)),
        Vector((max_x, max_y, 0)),
    ]
    print(f"Object {obj.name} bounding box: {corners_xy}")
    return corners_xy


def check_overlap_xy(
    bbox1: List[Vector], bbox2: List[Vector], padding: float = 0.08
) -> bool:
    """Check if two 2D bounding boxes overlap with optional padding.

    Args:
        bbox1 (List[Vector]): First bounding box corners.
        bbox2 (List[Vector]): Second bounding box corners.
        padding (float, optional): Padding around the bounding boxes. Defaults to 0.08.

    Returns:
        bool: True if the bounding boxes overlap, False otherwise.
    """
    min1 = Vector(
        (min(corner.x for corner in bbox1), min(corner.y for corner in bbox1), 0)
    )
    max1 = Vector(
        (max(corner.x for corner in bbox1), max(corner.y for corner in bbox1), 0)
    )
    min2 = Vector(
        (min(corner.x for corner in bbox2), min(corner.y for corner in bbox2), 0)
    )
    max2 = Vector(
        (max(corner.x for corner in bbox2), max(corner.y for corner in bbox2), 0)
    )
    overlap = not (
        min1.x > max2.x + padding
        or max1.x < min2.x - padding
        or min1.y > max2.y + padding
        or max1.y < min2.y - padding
    )
    print(
        f"Checking overlap between {bbox1} and {bbox2} with padding {padding}: {overlap}"
    )
    return overlap


def bring_objects_to_origin(objects: List[Dict[bpy.types.Object, Dict]]) -> None:
    """Bring objects to the origin while avoiding collisions.

    Args:
        objects (List[Dict[bpy.types.Object, Dict]]): List of object dictionaries.
    """
    object_bboxes = []
    for obj_dict in objects:
        obj = list(obj_dict.keys())[0]
        xy_corners = get_world_bounding_box_xy(obj)
        object_bboxes.append({obj: xy_corners})

    for obj_dict in objects:
        obj = list(obj_dict.keys())[0]
        if obj.location.x == 0 and obj.location.y == 0:
            continue

        direction = Vector((-obj.location.x, -obj.location.y, 0)).normalized()
        distance_to_origin = obj.location.length
        step_size = min(distance_to_origin / 10, 0.5)  # Dynamic step size
        iterations = 0
        max_iterations = 1000

        while iterations < max_iterations:
            obj.location += direction * step_size
            bpy.context.view_layer.update()
            current_obj_bbox = get_world_bounding_box_xy(obj)
            collision = False

            for other_obj_dict in object_bboxes:
                other_obj = list(other_obj_dict.keys())[0]
                other_bbox = other_obj_dict[other_obj]

                if other_obj != obj and check_overlap_xy(current_obj_bbox, other_bbox):
                    obj.location -= direction * step_size
                    bpy.context.view_layer.update()
                    collision = True
                    break

            print(
                f"Object {obj.name} position: {obj.location}, Collision: {collision}, Iterations: {iterations}"
            )

            if collision or (obj.location.x == 0 and obj.location.y == 0):
                break

            iterations += 1
            distance_to_origin = obj.location.length
            step_size = min(
                distance_to_origin / 10, 0.5
            )  # Update step size dynamically

        print(
            f"Final position of {obj.name}: {obj.location} after {iterations} iterations"
        )

        for bbox_dict in object_bboxes:
            if list(bbox_dict.keys())[0] == obj:
                bbox_dict[obj] = current_obj_bbox
                break


def place_objects_on_grid(
    objects: List[Dict[bpy.types.Object, Dict]], largest_length: float
) -> None:
    """Place objects on a grid based on their transformed positions.

    Args:
        objects (List[Dict[bpy.types.Object, Dict]]): List of object dictionaries.
        largest_length (float): Largest dimension among the objects.
    """
    for obj_dict in objects:
        obj = list(obj_dict.keys())[0]
        transformed_position = obj_dict[obj]["transformed_position"]
        obj.location = Vector(
            (
                transformed_position[0] * largest_length,
                transformed_position[1] * largest_length,
                0,
            )
        )
        print(f"Placed object {obj.name} at {obj.location}")

    bpy.context.view_layer.update()
    if len(objects) > 1:
        bring_objects_to_origin(objects)
