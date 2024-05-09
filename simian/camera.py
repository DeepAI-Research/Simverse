import math
import bpy
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


def set_camera_settings(combination: dict) -> None:
    """
    Applies camera settings from a combination to the Blender scene.

    This function updates various camera settings including orientation, pivot adjustments, and
    framing based on the provided combination dictionary.

    Args:
        combination (dict): A dictionary containing camera settings including 'fov', 'animation',
                            and orientation details.
    Returns:
        None
    """
    camera = bpy.context.scene.objects["Camera"]
    camera_data = camera.data

    # Get the initial lens value from the combination
    initial_lens = combination["framing"]["fov"]

    # Get the first keyframe's lens_offset value, if available
    animation = combination["animation"]
    keyframes = animation["keyframes"]
    if keyframes and "Camera" in keyframes[0] and "lens_offset" in keyframes[0]["Camera"]:
        lens_offset = keyframes[0]["Camera"]["lens_offset"]
        camera_data.lens = initial_lens + lens_offset
    else:
        camera_data.lens = initial_lens

    orientation_data = combination["orientation"]
    orientation = {"pitch": orientation_data["pitch"], "yaw": orientation_data["yaw"]}

    # Rotate CameraOrientationPivotYaw by the Y
    camera_orientation_pivot_yaw = bpy.data.objects.get("CameraOrientationPivotYaw")
    camera_orientation_pivot_yaw.rotation_euler[2] = orientation["yaw"] * math.pi / 180

    # Rotate CameraOrientationPivotPitch by the X
    camera_orientation_pivot_pitch = bpy.data.objects.get("CameraOrientationPivotPitch")
    camera_orientation_pivot_pitch.rotation_euler[1] = (
        orientation["pitch"] * -math.pi / 180
    )

    set_camera_animation(combination)
    position_camera(combination)


def set_camera_animation(combination: dict, frame_distance: int = 120) -> None:
    """
    Applies the specified animation to the camera based on the keyframes from the camera_data.json file.

    Args:
        combination (dict): The combination dictionary containing animation data.
        frame_distance (int): The distance between frames for keyframe placement.

    Returns:
        None
    """
    animation = combination["animation"]
    keyframes = animation["keyframes"]

    for i, keyframe in enumerate(keyframes):
        for obj_name, transforms in keyframe.items():
            obj = bpy.data.objects.get(obj_name)
            if obj is None:
                raise ValueError(f"Object {obj_name} not found in the scene")

            frame = i * frame_distance
            for transform_name, value in transforms.items():
                if transform_name == "position":
                    obj.location = value
                    obj.keyframe_insert(data_path="location", frame=frame)
                elif transform_name == "rotation":
                    obj.rotation_euler = [math.radians(angle) for angle in value]
                    obj.keyframe_insert(data_path="rotation_euler", frame=frame)
                elif transform_name == "scale":
                    obj.scale = value
                    obj.keyframe_insert(data_path="scale", frame=frame)
                elif transform_name == "lens_offset" and obj_name == "Camera":
                    camera_data = bpy.data.objects["Camera"].data
                    camera_data.lens = combination["framing"]["fov"] + value
                    camera_data.keyframe_insert(data_path="lens", frame=frame)

    bpy.context.scene.frame_set(0)


def position_camera(combination: dict) -> None:
    """
    Positions the camera based on the coverage factor and lens values.

    Args:
        combination (dict): The combination dictionary containing coverage factor and lens values.

    Returns:
        None
    """
    camera = bpy.context.scene.objects["Camera"]
    
    # Check if there are any selected objects
    if not bpy.context.selected_objects:
        raise ValueError("No objects selected. Please select a focus object.")
    
    focus_object = bpy.context.selected_objects[0]

    # Get the bounding box of the focus object in screen space
    bpy.context.view_layer.update()
    bbox = [focus_object.matrix_world @ Vector(corner) for corner in focus_object.bound_box]
    bbox_min = min(bbox, key=lambda v: v.z)
    bbox_max = max(bbox, key=lambda v: v.z)

    # Calculate the height of the bounding box
    bbox_height = bbox_max.z - bbox_min.z

    # Check if the focus object's height is above a minimum threshold
    min_height_threshold = 0.001
    if bbox_height < min_height_threshold:
        # Position the camera based on a predefined distance
        predefined_distance = 5.0
        camera.location.y = -predefined_distance
        return

    # Calculate the desired object height based on the coverage factor
    coverage_factor = combination["coverage_factor"]
    desired_height = bbox_height * coverage_factor

    # Move the camera backwards until the object's height matches the desired height
    step_size = max(bbox_height, 1.0)  # Dynamic step size based on the focus object's height
    max_iterations = 1000  # Maximum number of iterations to prevent infinite loop
    iteration = 0
    while iteration < max_iterations:
        bpy.context.view_layer.update()
        bbox = [focus_object.matrix_world @ Vector(corner) for corner in focus_object.bound_box]
        bbox_min = min(bbox, key=lambda v: v.z)
        bbox_max = max(bbox, key=lambda v: v.z)
        current_height = bbox_max.z - bbox_min.z

        if current_height <= desired_height:
            break

        camera.location.x += step_size
        step_size *= 0.5  # Decrease the step size as we get closer to the desired position
        iteration += 1
    
    if iteration == max_iterations:
        print("Warning: Maximum iterations reached while positioning the camera. The resulting coverage factor may not be exactly as desired.")