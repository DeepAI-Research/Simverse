import logging
from math import radians, cos, sin
from typing import Dict, List, Union
import numpy as np

import bpy
import mathutils
from mathutils import Vector

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


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
    logger.info(f"Object {obj.name} bounding box: {corners_xy}")
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
    logger.info(
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

            logger.info(
                f"Object {obj.name} position: {obj.location}, Collision: {collision}, Iterations: {iterations}"
            )

            if collision or (obj.location.x == 0 and obj.location.y == 0):
                break

            iterations += 1
            distance_to_origin = obj.location.length
            step_size = min(
                distance_to_origin / 10, 0.5
            )  # Update step size dynamically

        logger.info(
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
                obj.location.z,
            )
        )
        logger.info(f"Placed object {obj.name} at {obj.location}")

    bpy.context.view_layer.update()
    if len(objects) > 1:
        bring_objects_to_origin(objects)


def get_camera_plane_vertices(camera):
    scene = bpy.context.scene
    cam_data = camera.data
    cam_matrix_world = camera.matrix_world

    # Log camera settings
    logger.info(f"Camera Focal Length: {cam_data.lens}")
    logger.info(f"Camera Sensor Width: {cam_data.sensor_width}")
    logger.info(f"Camera Sensor Height: {cam_data.sensor_height}")
    logger.info(f"Camera Aspect Ratio: {cam_data.sensor_width / cam_data.sensor_height}")

    # Get the camera's frustum
    frame = cam_data.view_frame(scene=scene)
    logger.info(f"Camera frame: {frame}")
    
    # Convert the frame coordinates to world coordinates
    frame_world = [cam_matrix_world @ v for v in frame]
    logger.info(f"World frame: {frame_world}")

    # Project the world coordinates to the plane
    plane_normal = mathutils.Vector((0, 0, 1))  # Assuming the plane is the XY plane at Z=0
    plane_point = mathutils.Vector((0, 0, 0))  # Point on the plane
    
    # Calculate intersection of rays with the plane
    plane_vertices = []
    for v in frame_world:
        direction = v - cam_matrix_world.translation

        logger.info(f"Direction: {direction}")

        denom = plane_normal.dot(direction)

        logger.info(f"Denominator: {denom}")
        if abs(denom) > 1e-6:
            logger.info(f"Denominator is not near zero")
            t = (plane_point - cam_matrix_world.translation).dot(plane_normal) / denom

            # Adding detailed debug information to check the calculations
            logger.info(f"Ray origin (o): {cam_matrix_world.translation}")
            logger.info(f"Vector (p0 - o): {plane_point - cam_matrix_world.translation}")
            logger.info(f"Dot product (d . n): {direction.dot(plane_normal)}")

            print("This is the t value: ", t)
            intersection_point = cam_matrix_world.translation + t * direction

            logger.info(f"Intersection point: {intersection_point}")
            plane_vertices.append(intersection_point)
        else:
            logger.warning(f"Skipping vertex due to near-zero denominator: {v}")
    
    # Ensure vertices form a rectangle
    if len(plane_vertices) == 4:
        plane_vertices = [plane_vertices[i] for i in [1, 0, 3, 2]]
    else:
        logger.warning(f"Expected 4 plane vertices, got {len(plane_vertices)}")
    
    logger.info(f"Plane vertices: {plane_vertices}")
    return plane_vertices


def create_mesh_from_vertices(vertices, name="Plane_POV"):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    
    # Ensure we have 4 vertices
    if len(vertices) == 4:
        faces = [(0, 1, 2, 3)]
    else:
        faces = []

    mesh.from_pydata(vertices, [], faces)
    mesh.update()


def visualize_frustum(camera, vertices):
    curve_data = bpy.data.curves.new(name='FrustumLines', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 2

    obj = bpy.data.objects.new('FrustumLines', curve_data)
    bpy.context.collection.objects.link(obj)

    polyline = curve_data.splines.new('POLY')
    polyline.points.add(len(vertices) + 1)  # Add points for each vertex plus one for the camera location

    polyline.points[0].co = (camera.location.x, camera.location.y, camera.location.z, 1)
    for i, vertex in enumerate(vertices):
        polyline.points[i + 1].co = (vertex.x, vertex.y, vertex.z, 1)


def visualize_plane_vertices(vertices):
    curve_data = bpy.data.curves.new(name='PlaneVerticesLines', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 2

    obj = bpy.data.objects.new('PlaneVerticesLines', curve_data)
    bpy.context.collection.objects.link(obj)

    polyline = curve_data.splines.new('POLY')
    polyline.points.add(len(vertices) + 1)  # Add points for each vertex and close the loop

    for i, vertex in enumerate(vertices):
        polyline.points[i].co = (vertex.x, vertex.y, vertex.z, 1)
    polyline.points[-1].co = (vertices[0].x, vertices[0].y, vertices[0].z, 1)  # Close the loop


def draw_vector_from_camera(camera_obj):
    import bmesh
    bm = bmesh.new()
    layer = bm.verts.layers.float_vector.new('direction')
    cam_matrix = camera_obj.matrix_world
    cam_location = cam_matrix.translation
    frame = camera_obj.data.view_frame(scene=bpy.context.scene)
    
    for v in frame:
        world_coord = cam_matrix @ v
        direction = world_coord - cam_location
        vert = bm.verts.new(cam_location)
        vert[layer] = direction  # Store direction as custom data on the vertex
        
        # Create an edge to visualize the direction
        end_point = vert.co + direction.normalized() * 10  # Extend the direction
        end_vert = bm.verts.new(end_point)
        bm.edges.new([vert, end_vert])
    
    mesh = bpy.data.meshes.new("VectorVisual")
    bm.to_mesh(mesh)
    obj = bpy.data.objects.new("VectorVisualObj", mesh)
    bpy.context.collection.objects.link(obj)
    bm.free()


def apply_movement(objects, yaw, start_frame, end_frame):
    yaw_radians = radians(yaw)
    rotation_matrix = mathutils.Matrix.Rotation(yaw_radians, 4, 'Z')
    scene = bpy.context.scene
    camera = scene.camera

    # output camera's location
    logger.info(f"Camera location: {camera.location}")

    # Get camera plane vertices
    plane_vertices = get_camera_plane_vertices(camera)
    create_mesh_from_vertices(plane_vertices)
    visualize_frustum(camera, plane_vertices)
    visualize_plane_vertices(plane_vertices)

    draw_vector_from_camera(camera)

    logger.info(f"planer_vertices: {plane_vertices}")

    # Calculate midpoints of each edge
    bottom_center = (plane_vertices[0] + plane_vertices[3]) / 2
    top_center = (plane_vertices[1] + plane_vertices[2]) / 2
    left_center = (plane_vertices[2] + plane_vertices[3]) / 2
    right_center = (plane_vertices[0] + plane_vertices[1]) / 2

    logger.info(f"Bottom center: {bottom_center}")
    logger.info(f"Top center: {top_center}")
    logger.info(f"Left center: {left_center}")
    logger.info(f"Right center: {right_center}")

    for obj_dict in objects:
        obj = list(obj_dict.keys())[0]
        properties = list(obj_dict.values())[0]
        movement = properties.get('movement')

        if not movement:
            continue
        
        logger.info(f"Applying movement to object")
        
        # Determine initial placement based on movement direction
        if movement["direction"] == "right":
            initial_position = left_center
        elif movement["direction"] == "left":
            initial_position = right_center
        elif movement["direction"] == "forward":
            initial_position = top_center
        elif movement["direction"] == "backward":
            initial_position = bottom_center

        # Rotate direction vector according to yaw
        direction_vector = mathutils.Vector({
            "forward": (1, 0, 0),
            "backward": (-1, 0, 0),
            "right": (0, 1, 0),
            "left": (0, -1, 0)
        }[movement["direction"]])
        rotated_vector = rotation_matrix @ direction_vector
        step_vector = rotated_vector * movement["speed"]

        logger.info(f"Initial position: {initial_position}")

        # Calculate offset
        offset_multiplier = 2  # Adjust this value to increase or decrease the offset
        offset = step_vector * offset_multiplier

        # Position object at initial location at the start frame
        scene.frame_set(start_frame)
        obj.location = obj.location + initial_position - offset
        obj.keyframe_insert(data_path="location", frame=start_frame)

        # Animate object from start_frame to end_frame
        for frame in range(start_frame + 1, end_frame + 1):
            obj.location += step_vector
            obj.keyframe_insert(data_path="location", frame=frame)

    logger.info(f"Movement applied from frame {start_frame} to {end_frame}")
    bpy.context.view_layer.update()
