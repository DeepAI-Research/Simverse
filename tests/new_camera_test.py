import bpy
import math
from mathutils import Vector

def create_camera_rig() -> bpy.types.Object:
    """
    Creates a camera rig consisting of multiple objects in Blender.

    Returns:
        dict: A dictionary containing the created objects:
            - camera_animation_root: The root object of the camera animation hierarchy.
            - camera_orientation_pivot_yaw: The yaw pivot object for camera orientation.
            - camera_orientation_pivot_pitch: The pitch pivot object for camera orientation.
            - camera_framing_pivot: The pivot object for camera framing.
            - camera_animation_pivot: The pivot object for camera animation.
            - camera_object: The camera object.
            - camera: The camera data.
    """
    camera_animation_root = bpy.data.objects.new("CameraAnimationRoot", None)
    bpy.context.scene.collection.objects.link(camera_animation_root)

    camera_orientation_pivot_yaw = bpy.data.objects.new(
        "CameraOrientationPivotYaw", None
    )
    camera_orientation_pivot_yaw.parent = camera_animation_root
    bpy.context.scene.collection.objects.link(camera_orientation_pivot_yaw)

    camera_orientation_pivot_pitch = bpy.data.objects.new(
        "CameraOrientationPivotPitch", None
    )
    camera_orientation_pivot_pitch.parent = camera_orientation_pivot_yaw
    bpy.context.scene.collection.objects.link(camera_orientation_pivot_pitch)

    camera_framing_pivot = bpy.data.objects.new("CameraFramingPivot", None)
    camera_framing_pivot.parent = camera_orientation_pivot_pitch
    bpy.context.scene.collection.objects.link(camera_framing_pivot)

    camera_animation_pivot = bpy.data.objects.new("CameraAnimationPivot", None)
    camera_animation_pivot.parent = camera_framing_pivot
    bpy.context.scene.collection.objects.link(camera_animation_pivot)

    camera = bpy.data.cameras.new("Camera")
    
    camera_object = bpy.data.objects.new("Camera", camera)
    camera_object.data.lens_unit = 'FOV'

    # Rotate the Camera 90º
    camera_object.delta_rotation_euler = [1.5708, 0, 1.5708]

    camera_object.parent = camera_animation_pivot
    bpy.context.scene.collection.objects.link(camera_object)

    bpy.context.scene.camera = camera_object

    return {
        "camera_animation_root": camera_animation_root,
        "camera_orientation_pivot_yaw": camera_orientation_pivot_yaw,
        "camera_orientation_pivot_pitch": camera_orientation_pivot_pitch,
        "camera_framing_pivot": camera_framing_pivot,
        "camera_animation_pivot": camera_animation_pivot,
        "camera_object": camera_object,
        "camera": camera,
    }

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
    # Create a test scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    dict = create_camera_rig()
    
    camera = dict['camera_object']

    # Set camera properties
    camera.data.sensor_width = 36
    camera.data.sensor_height = 24
    camera.data.lens_unit = 'FOV'
    camera.data.angle = math.radians(35)

    # Create a test object (cube)
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    cube = bpy.context.active_object
    
    # update view
    bpy.context.view_layer.update()

    # Position the camera for the cube
    position_camera_for_object(camera, cube)
    
    all_vertices_in_frame = True
    for vertex in cube.data.vertices:
        world_vertex = cube.matrix_world @ vertex.co
        if not is_vertex_in_frame(camera, world_vertex):
            all_vertices_in_frame = False
            print(f"Vertex {vertex.co} is outside the camera's frame.")

    if all_vertices_in_frame:
        print("All vertices are within the camera's frame.")
    else:
        print("Some vertices are outside the camera's frame.")
    
    # add a light
    bpy.ops.object.light_add(type='SUN', location=(0, 0, 10))

    # set render file path to render.png
    bpy.context.scene.render.filepath = 'render.png'
    
    bpy.ops.render.render(write_still=True)
    
    # save the scene
    bpy.ops.wm.save_as_mainfile(filepath='test.blend')

    print("Test completed.")

if __name__ == "__main__":
    test_optimal_distance()