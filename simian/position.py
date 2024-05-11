import bpy
import random


def find_largest_length(objects):
    """
    Find the largest dimension (width, height, or depth) of all objects based on their bounding box dimensions.

    Args:
        objects (list): List of Blender objects.

    Returns:
        largest_dimension (float): The largest dimension found among all objects.
    """
    largest_dimension = 0
    for obj in objects:
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
    cell_size = largest_length  # Creates grid cell size

    for obj in objects:
        if obj:
            # Calculate grid cell row and column based on placement
            placement = obj.get("placement")
            if placement is not None:
                cell_row = placement % 3
                cell_col = placement // 3

                """
                    Imagine a 3x3 grid with cells numbered as follows:
                    0 1 2
                    3 4 5
                    6 7 8

                    Let's say that each cell is length 2

                    In Blender the [4] is (0,0,0).
                    [1] would be negative x
                    [3] would be negative y

                    (cell_col + 0.5) * cell_size
                    The above part of the formula gets you where you would be IF 
                    the graph was 0,0,0 at [6]

                    Example:
                        Let's say we want to go to 2 2 which is [8]
                        And let's say the cell size is 2

                        Let's start with row: 
                        (2*0.5) * 2 = 5. Which makes intuitive sense because

                        So cell is 6x6

                        if this were a 0,0,0 at [0] we would have 5 which is center of row 3

                        But this isn't ur typical grid and center is at [4]. In blender 4 is 0,0,0
                        and [7] is (+)

                        So we simply subtract by half the grid to get where we want to be.
                        That's where the - (1.5 * cell_size). This is basically centering the grid at [4]

                        A lot to take in but take your time here :)
                """

                # cell_center_x is the x-coordinate of the center of the cell (row)
                cell_center_x = (cell_col + 0.5) * cell_size - (1.5 * cell_size)
                cell_center_y = (cell_row + 0.5) * cell_size - (1.5 * cell_size)

                """
                0 1 2
                3 4 5
                6 7 8

                How we can get objects closer to each other:

                1) Get everything to move toward the center.
                2) So if an object is at [0] we want to move it closer to [4].
                """

                # THIS IS FOR X:
                distance_from_boundary_to_obj_x = abs(
                    abs(obj.dimensions[0] / 2) - abs(cell_size / 2)
                )
                if placement in [0, 1, 2]:
                    cell_center_x += distance_from_boundary_to_obj_x
                elif placement in [6, 7, 8]:
                    cell_center_x -= distance_from_boundary_to_obj_x

                # THIS IS FOR Y:
                distance_from_boundary_to_obj_y = abs(
                    abs(obj.dimensions[1] / 2) - abs(cell_size / 2)
                )
                if placement in [2, 5, 8]:
                    cell_center_y -= distance_from_boundary_to_obj_y
                elif placement in [0, 3, 6]:
                    cell_center_y += distance_from_boundary_to_obj_y

                obj.location = (cell_center_x, cell_center_y, 0)  # Set object location
