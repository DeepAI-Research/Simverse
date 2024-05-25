import bpy
from mathutils import Vector


def find_largest_length(objects):
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


def get_world_bounding_box_xy(obj):
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


def check_overlap_xy(bbox1, bbox2, padding=0.08):
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


def bring_objects_to_origin(objects):
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


def place_objects_on_grid(objects, largest_length):
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


# (-1 ,1) (0, 1) (1, 1)
# (-1, 0) (0, 0) (1, 0)
# (-1, -1) (0, -1) (1, -1)
