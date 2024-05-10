import math
import random

def degrees_to_radians(deg):
    return deg * math.pi / 180


def adjust_positions(objects, camera_yaw):
    """
    Adjust the positions of objects based on the camera yaw angle.

    Args:
        - objects (list): List of objects with their placements.
        - camera_yaw (float): The yaw angle of the camera.
    
    Returns:
        - list: List of transformed positions for each object.
    """
    yaw_radians = degrees_to_radians(-camera_yaw)  # Negative for the clockwise rotation

    """
        Here the cos_angle and sin_angle we are getting the position of the camera on the unit circle
        x = cos(angle)
        y = sin(angle)

        just imagine a triangle
    """
    cos_angle = math.cos(yaw_radians)
    sin_angle = math.sin(yaw_radians)
    
    # Define the rotation matrix
    rotation_matrix = [
        [cos_angle, -sin_angle],
        [sin_angle, cos_angle]
    ]
    
    # Placeholder for transformed coordinates
    transformed_positions = []
    
    """
    Center of the grid assumed to be at (1, 1) for a 3x3 grid (index base 0)
    
    0 1 2
    3 4 5
    6 7 8

    the [0] is at 0 and so on. So [4] in at (1,1) right now the cneter of the grid
    """
    
    # Apply rotation to each object position
    for obj in objects:
        """
        You can think of grid_x and grid_y as the position of the object in the grid
        gridx being the column and gridy being the row

        Think of grid_x and grid_y will look like (0, 2)
        
        IMPORTANT: [4] is at (0, 0) in the grid
        """
        grid_x = (obj['placement'] % 3) - 1
        grid_y = -(obj['placement'] // 3 - 1)
        
        """
        The formula below is a bit confusing but it's just a matrix multiplication

        0 1 2
        3 4 5
        6 7 8

        IMPORTANT: [4] is at (0, 0) in the grid

        let's say tha we are rotating [5] which is at (2, 1) in the grid

        rotated x = cos(yaw) * 2 + -sin(yaw) * 1

        How does this make sense?

        We're taking the x length of the camera coordinate and multiplying it by the x length of the object
        and the y length of the camera coordinate and multiplying it by the y length of the object

        to make it easier it just looks like this:

        | cos(yaw)  -sin(yaw) | | 2 | = | rotated_x |
        | sin(yaw)   cos(yaw) | | 1 | = | rotated_y |
        """
        rotated_x = rotation_matrix[0][0] * grid_x + rotation_matrix[0][1] * grid_y
        rotated_y = rotation_matrix[1][0] * grid_x + rotation_matrix[1][1] * grid_y
        
        # Store transformed position
        transformed_positions.append((rotated_x, rotated_y))
        obj['transformed_position'] = (rotated_x, rotated_y)
    
    return transformed_positions


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
                pos1 = obj1['transformed_position']
                pos2 = obj2['transformed_position']

                # Calculate directional differences
                dx = pos2[0] - pos1[0]
                dy = pos2[1] - pos1[1]

                relationship = ""

                # Determine the horizontal relationship
                if dx > 0:  # obj2 is to the right of obj1
                    relationship = random.choice(to_the_right)
                elif dx < 0:  # obj2 is to the left of obj1
                    relationship = random.choice(to_the_left)

                # Determine the vertical relationship
                if dy > 0:  # obj2 is behind obj1
                    relationship += " and " + random.choice(behind) if relationship else random.choice(behind)
                elif dy < 0:  # obj2 is in front of obj1
                    relationship += " and " + random.choice(in_front_of) if relationship else random.choice(in_front_of)

                # If there is a significant relationship, add it to the list
                if relationship:
                    relationships.append(f"{obj1['name']} {relationship} {obj2['name']}.")

    return relationships
