import bpy
from mathutils import Vector


def find_largest_length(objects):
    """
    Find the largest dimension (width, height, or depth) of all objects based on their bounding box dimensions.

    Args:
        objects (list): List of Blender objects.

    Returns:
        largest_dimension (float): The largest dimension found among all objects.
    """

    # object = [{obj: [placement_x, placement_y]}]
    largest_dimension = 0
    for obj in objects:
        obj = list(obj.keys())[0]
        # Ensure the object's current transformations are applied
        bpy.context.view_layer.update()

        # The bounding box returns a list of 8 vertices [(x, y, z), ..., (x, y, z)]
        bbox_corners = obj.bound_box
        width = (
            max(bbox_corners, key=lambda v: v[0])[0]
            - min(bbox_corners, key=lambda v: v[0])[0]
        )
        height = (
            max(bbox_corners, key=lambda v: v[1])[1]
            - min(bbox_corners, key=lambda v: v[1])[1]
        )

        # Calculate the maximum dimension for the current object
        current_max = max(width, height)
        largest_dimension = max(largest_dimension, current_max)

    return largest_dimension


def get_world_bounding_box_xy(obj):
    """
    Get the world-space bounding box of an object on the XY plane.
    
    Args:
        obj: Blender object.
    
    Returns:
        list: List of 4 corners of the bounding box in world coordinates on the XY plane.
    """
    # Transform each corner of the local bounding box to world space
    world_bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    
    # Find the min and max x and y values
    min_x = min(corner.x for corner in world_bbox)
    max_x = max(corner.x for corner in world_bbox)
    min_y = min(corner.y for corner in world_bbox)
    max_y = max(corner.y for corner in world_bbox)
    
    # Create the 4 corners on the XY plane
    corners_xy = [
        Vector((min_x, min_y, 0)),
        Vector((max_x, min_y, 0)),
        Vector((min_x, max_y, 0)),
        Vector((max_x, max_y, 0))
    ]
    
    # Print the corners for debugging
    for i, corner in enumerate(corners_xy):
        print(f"Bounding box XY corner {i}: {corner}")
    
    return corners_xy


def check_overlap_xy(bbox1, bbox2, padding=0.1):
    """
    Check if two bounding boxes overlap on the XY plane, considering a padding.
    
    Args:
        bbox1, bbox2: Lists of corners of the bounding boxes.
        padding: Additional space to consider around each bounding box.
    
    Returns:
        bool: True if the bounding boxes overlap, False otherwise.
    """
    min1 = Vector((min(corner.x for corner in bbox1), min(corner.y for corner in bbox1), 0))
    max1 = Vector((max(corner.x for corner in bbox1), max(corner.y for corner in bbox1), 0))
    
    min2 = Vector((min(corner.x for corner in bbox2), min(corner.y for corner in bbox2), 0))
    max2 = Vector((max(corner.x for corner in bbox2), max(corner.y for corner in bbox2), 0))
    
    return not (min1.x > max2.x + padding or max1.x < min2.x - padding or
                min1.y > max2.y + padding or max1.y < min2.y - padding)


def bring_objects_to_origin(objects):
    """
    Move objects towards the origin, stopping if they collide with another object.
    
    Args:
        objects (list of bpy.types.Object): List of Blender objects.
    
    Returns:
        None
    """

    step_size = 0.1

    # Get initial bounding boxes for all objects
    object_bboxes = []
    for obj_dict in objects:
        obj = list(obj_dict.keys())[0]
        xy_corners = get_world_bounding_box_xy(obj)
        object_bboxes.append({obj: xy_corners})

    for obj_dict in objects:
        obj = list(obj_dict.keys())[0]  # Extract the Blender object from the dictionary
        
        # Skip the object if it is at the center
        if obj.location.x == 0 and obj.location.y == 0:
            continue

        direction = Vector(obj.location)
        direction.x = -obj.location.x
        direction.y = -obj.location.y
        
        # check if Vector is 0,0,0
        if direction.length == 0:
            continue
        
        direction = direction.normalized() * step_size
        iterations = 0
        max_iterations = 1000
        
        while iterations < max_iterations:
            # # Move the object in small steps along the direction vector
            obj.location += direction
            bpy.context.view_layer.update()
            
            current_obj_bbox = get_world_bounding_box_xy(obj)
            collision = False

            for other_obj_dict in object_bboxes:
                other_obj = list(other_obj_dict.keys())[0]
                other_bbox = other_obj_dict[other_obj]
                
                if other_obj != obj and check_overlap_xy(current_obj_bbox, other_bbox):
                    obj.location -= direction
                    bpy.context.view_layer.update()
                    collision = True
                    break
            
            if collision or (obj.location.x == 0 and obj.location.y == 0):
                break

            iterations += 1

        # Update the bounding box list with the new position
        for bbox_dict in object_bboxes:
            if list(bbox_dict.keys())[0] == obj:
                bbox_dict[obj] = current_obj_bbox
                break

        print(f"Object {obj.name} final position: {obj.location}")


def place_objects_on_grid(objects, largest_length):
    """
    Place objects in the scene based on a conceptual grid.

    Args:
        objects (list of bpy.types.Object): List of Blender objects.
        largest_length (float): The largest dimension found among the objects used to define grid size.

    Returns:
        None
    """

    # objects = [{obj: 1}, {obj: 1}]
    for obj in objects:
        if obj:
            placement = list(obj.values())[0]
            if placement:
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
                coordinate_x, coordinate_y = lookup_table[placement]

                # cell_center_x is the x-coordinate of the center of the cell (row)
                cell_center_x = (coordinate_x) * largest_length
                cell_center_y = (coordinate_y) * largest_length

                obj = list(obj.keys())[0]
                obj.location = (cell_center_x, cell_center_y, 0)  # Set object location
                # Ensure the object's current transformations are applied
            
    bpy.context.view_layer.update()
    
    # Bring objects closer to the center
    if len(objects) > 1:
        bring_objects_to_origin(objects)

# (-1 ,1) (0, 1) (1, 1)
# (-1, 0) (0, 0) (1, 0)
# (-1, -1) (0, -1) (1, -1)