import bpy
import math
from mathutils import Vector

from ..camera import create_camera_rig


def calculate_optimal_distance(camera, obj):
    """
    Calculate the optimal distance between the camera and an object
    so that the entire object is within the camera's frame, considering the object's depth.

    Args:
        camera (bpy.types.Object): The camera object.
        obj (bpy.types.Object): The object to be framed.

    Returns:
        float: The optimal distance between the camera and the object.
    """
    # Get the camera's field of view
    fov_h = camera.data.angle_x
    fov_v = camera.data.angle_y

    # Calculate the object's bounding box dimensions in world space
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    bbox_dimensions = [max(coord) - min(coord) for coord in zip(*bbox)]
    obj_width, obj_height, obj_depth = bbox_dimensions

    # Find the diagonal of the bounding box which will require the farthest distance
    diagonal = math.sqrt(obj_width**2 + obj_height**2 + obj_depth**2)

    # Calculate the required distance to fit the diagonal in view
    fov_average = (fov_h + fov_v) / 2
    distance = (diagonal / 2) / math.tan(fov_average / 2)

    return distance


def position_camera_for_object(camera, obj):
    """
    Position the camera so that all vertices of the object are in frame or at the frame border.

    Args:
        camera (bpy.types.Object): The camera object.
        obj (bpy.types.Object): The object to frame.
    """
    optimal_distance = calculate_optimal_distance(camera, obj)
    camera.location = obj.location + Vector((optimal_distance, 0, 0))
    camera.rotation_euler = (0, 0, 0)  # Reset rotation or set as needed


def is_vertex_in_frame(camera, vertex):
    """
    Check if a vertex is within the camera's frame.

    Args:
        camera (bpy.types.Object): The camera object.
        vertex (mathutils.Vector): The vertex to check.

    Returns:
        bool: True if the vertex is within the camera's frame, False otherwise.
    """
    # Transform the vertex to camera space
    camera_matrix = camera.matrix_world.inverted()
    vertex_camera = camera_matrix @ vertex

    # Check if the vertex is within the camera's view frustum
    fov_h = camera.data.angle_x
    fov_v = camera.data.angle_y
    aspect_ratio = camera.data.sensor_width / camera.data.sensor_height

    # Calculate tangent values
    tan_fov_h_half = math.tan(fov_h / 2)
    tan_fov_v_half = math.tan(fov_v / 2)

    # Calculate the near plane dimensions
    near_plane_width = 2 * tan_fov_h_half * vertex_camera.z
    near_plane_height = 2 * tan_fov_v_half * vertex_camera.z

    # Check if the vertex is within the near plane
    x_relative = vertex_camera.x / near_plane_width
    y_relative = vertex_camera.y / near_plane_height

    return abs(x_relative) <= 0.5 and abs(y_relative) <= 0.5


def test_optimal_distance():
    # Clear existing objects
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    # Create the camera rig
    dict = create_camera_rig()
    camera = dict["camera_object"]

    # Set camera properties
    camera.data.sensor_width = 36
    camera.data.sensor_height = 24
    camera.data.lens_unit = "FOV"
    camera.data.angle = math.radians(35)

    # Define different cube dimensions
    cube_dimensions = [(1, 10, 1), (10, 1, 1), (1, 1, 10)]

    # Iterate over each set of dimensions
    for i, (width, depth, height) in enumerate(cube_dimensions, start=1):
        # Create a test object (cube) with specific dimensions
        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0))
        cube = bpy.context.active_object
        cube.scale = (
            width / 2,
            depth / 2,
            height / 2,
        )  # Blender uses half-dimensions for scale
        bpy.context.view_layer.update()

        # Apply scale to ensure the transformations are correct
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        # Position the camera for the cube
        position_camera_for_object(camera, cube)

        all_vertices_in_frame = True
        for vertex in cube.data.vertices:
            world_vertex = cube.matrix_world @ vertex.co
            if not is_vertex_in_frame(camera, world_vertex):
                all_vertices_in_frame = False
                print(f"Cube {i}: Vertex {vertex.co} is outside the camera's frame.")

        if all_vertices_in_frame:
            print(f"All vertices of Cube {i} are within the camera's frame.")
        else:
            print(f"Some vertices of Cube {i} are outside the camera's frame.")

        # Remove the cube after rendering to prepare for the next one
        bpy.data.objects.remove(cube, do_unlink=True)

    print("Test completed.")


if __name__ == "__main__":
    test_optimal_distance()
