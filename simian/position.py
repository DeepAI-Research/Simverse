import bpy


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

        print(f"Object: {obj.name} - Width: {width}, Height: {height}")

        # Calculate the maximum dimension for the current object
        current_max = max(width, height)
        largest_dimension = max(largest_dimension, current_max)

    print("LARGEST DIMENSION:", largest_dimension)
    return largest_dimension


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
        print("Here 1")
        if obj:
            placement = list(obj.values())[0]
            if placement:
                print("Here 3")
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
                padding = 0.1
                # cell_center_x is the x-coordinate of the center of the cell (row)
                cell_center_x = (coordinate_x + padding) * largest_length
                cell_center_y = (coordinate_y + padding) * largest_length
                print("Here 4")
                print(obj)  # {bpy.data.objects['9b1fe3f138e746c1a69224856732a01b']: 4}
                obj = list(obj.keys())[0]
                obj.location = (cell_center_x, cell_center_y, 0)  # Set object location
                print("Here 5")
